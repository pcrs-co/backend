from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework import serializers
from django.db import transaction
from io import BytesIO
from .models import *
import pandas as pd
import string
import random
import re


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Handles the fields specific to the Customer profile.
    """

    class Meta:
        model = Customer
        fields = ["middle_name", "date_of_birth", "avatar", "district", "region"]


class UserSerializer(serializers.ModelSerializer):
    """
    Handles the creation and updating of a CustomUser and their linked Customer profile.
    This is for standard user/customer registration.
    """

    # From Customer profile model, but handled here for convenience
    customer_profile = CustomerProfileSerializer(required=False)

    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "region",
            "district",
            "customer_profile",
            "password",
            "password2",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "validators": [validate_password]},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_phone_number(self, phone):
        # Clean the phone number just like your form
        phone = re.sub(r"[^\d+]", "", phone)
        if not phone.startswith("+"):
            phone = "+255" + phone
        if not re.match(r"^\+\d{1,4}\d{7,15}$", phone):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return phone

    def validate(self, attrs):
        if attrs["password"] != attrs.pop(
            "password2"
        ):  # pop password2 after comparison
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        customer_data = validated_data.pop("customer_profile", {})

        with transaction.atomic():
            user = CustomUser.objects.create_user(**validated_data)

            # Create the customer profile linked to the new user
            Customer.objects.create(user=user, **customer_data)

            # Add user to the 'customer' group (or 'default')
            customer_group, _ = Group.objects.get_or_create(name="customer")
            user.groups.add(customer_group)

        return user

    def update(self, instance, validated_data):
        customer_data = validated_data.pop("customer_profile", {})
        customer_profile = instance.customer_profile

        # Update the CustomUser instance
        instance = super().update(instance, validated_data)

        # Update the nested CustomerProfile instance
        if customer_data:
            for attr, value in customer_data.items():
                setattr(customer_profile, attr, value)
            customer_profile.save()

        return instance


class CustomerListSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for listing customers in the admin panel.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name", "email", "phone_number"]


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class VendorListSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for listing vendors in the admin panel.
    Uses 'source' to pull data from the related user model.
    """

    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "company_name",
            "location",
            "logo",
            "verified",
            "username",
            "email",
            "phone_number",
        ]


class VendorSerializer(serializers.ModelSerializer):
    """
    The main serializer for CREATING and RETRIEVING a single Vendor.
    It accepts user data for creation but doesn't map it directly to the Vendor model.
    """

    # User fields for write operations (creating a new vendor)
    email = serializers.EmailField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(write_only=True, required=True)
    region = serializers.CharField(write_only=True, required=False)
    district = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "company_name",
            "location",
            "logo",
            "verified",
            # Write-only fields for user creation:
            "email",
            "username",
            "phone_number",
            "region",
            "district",
        ]
        read_only_fields = ["id", "verified"]  # These fields are not set on create

    def to_representation(self, instance):
        """
        Controls the output (read) representation.
        We start with the Vendor fields and add the related User fields.
        """
        representation = super().to_representation(instance)
        user_info = UserSerializer(instance.user).data
        # Merge user info into the main representation for easy frontend access
        representation["user"] = {
            "id": user_info.get("id"),
            "username": user_info.get("username"),
            "email": user_info.get("email"),
            "phone_number": user_info.get("phone_number"),
            "region": user_info.get("region"),
            "district": user_info.get("district"),
        }
        return representation

        # Your email sending logic can remain here if needed.

    @staticmethod
    def generate_temp_password(length=12):
        characters = string.ascii_letters + string.digits + "@#$!%^&*"
        return "".join(random.choices(characters, k=length))

    def create(self, validated_data):
        # --- KEY CHANGE: GENERATE PASSWORD HERE ---
        temp_password = self.generate_temp_password()

        user_data = {
            "email": validated_data.pop("email"),
            "username": validated_data.pop("username"),
            "phone_number": validated_data.pop("phone_number"),
            "region": validated_data.pop("region", ""),
            "district": validated_data.pop("district", ""),
            # Add the generated password to the user data
            "password": temp_password,
        }

        # What's left in validated_data are the Vendor fields:
        # company_name, location, logo

        try:
            with transaction.atomic():
                user = CustomUser.objects.create_user(**user_data)

                vendor_group, _ = Group.objects.get_or_create(name="vendor")
                user.groups.add(vendor_group)

                vendor = Vendor.objects.create(user=user, **validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed during account creation: {e}"}
            )

        self._send_welcome_email(user.email, user_data["password"])
        return vendor

    def _send_welcome_email(self, email, password):
        try:
            subject = "Your Vendor Account Credentials"
            message = f"Welcome! Your temporary password: {password}"
            from_email = "noreply@yourdomain.com"

            send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,  # Set to True in production if you want to ignore errors
            )
        except Exception as e:
            print(f"Failed to send email: {e}")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Check group memberships
        if user.groups.filter(name="vendor").exists():
            data["role"] = "vendor"
        elif user.is_superuser:
            data["role"] = "admin"
        else:
            data["role"] = "user"

        data["username"] = user.username
        return data
