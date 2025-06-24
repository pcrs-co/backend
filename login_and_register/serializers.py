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


# A serializer specifically for the nested Vendor profile
class NestedVendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "company_name", "location", "logo"]


# This is your main, unified serializer for viewing and UPDATING user details
class UserDetailSerializer(serializers.ModelSerializer):
    # This field is for READING the vendor profile.
    vendor_profile_read = NestedVendorProfileSerializer(source="vendor", read_only=True)

    # This field is for WRITING (updating) the vendor profile. It's not part of the model itself.
    vendor_profile_write = serializers.JSONField(write_only=True, required=False)

    role = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",  # Read-only
            "vendor_profile_read",  # Read-only representation of vendor data
            "vendor_profile_write",  # Write-only field for receiving vendor updates
            "date_joined",
        ]
        read_only_fields = ["username", "date_joined", "role", "vendor_profile_read"]

    def get_role(self, obj):
        """Determines the user's primary role."""
        if obj.is_superuser or obj.is_staff:
            return "admin"
        if hasattr(obj, "vendor"):
            return "vendor"
        return "customer"

    def update(self, instance, validated_data):
        """Handle updates for both CustomUser and the nested Vendor profile."""
        # Pop the vendor data before calling the parent update method
        vendor_data = validated_data.pop("vendor_profile_write", None)

        # Update the CustomUser fields (first_name, last_name, etc.)
        instance = super().update(instance, validated_data)

        # If vendor data was provided and the user is a vendor, update the vendor profile
        if vendor_data and hasattr(instance, "vendor"):
            vendor_profile = instance.vendor
            # Assuming vendor_data is a dict like {'company_name': 'New Name'}
            for attr, value in vendor_data.items():
                setattr(vendor_profile, attr, value)
            vendor_profile.save()

        return instance

    def to_representation(self, instance):
        """
        Custom representation to rename `vendor_profile_read` to `vendor_profile`
        for a cleaner frontend experience.
        """
        representation = super().to_representation(instance)
        # The write-only field won't be in the output, so we don't need to pop it.
        representation["vendor_profile"] = representation.pop(
            "vendor_profile_read", None
        )
        return representation


# Create a small, reusable serializer for the user data
class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email"]


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Handles the fields specific to the Customer profile.
    """

    class Meta:
        model = Customer
        fields = ["middle_name", "date_of_birth", "avatar"]


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


# New serializer specifically for an admin updating a customer's user profile.
class UpdateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # List only the fields an admin should be able to change on the user model.
        # We exclude sensitive fields like password.
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "region",
            "district",
        ]
        # --- THIS IS THE FIX ---
        # Mark the username as read-only. An admin can see it, but not change it.
        # This prevents accidental changes and is a common source of validation errors.
        read_only_fields = ['username']


class VendorListSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for listing vendors in the admin panel.
    Uses 'source' to pull data from the related user model.
    """

    # This line tells DRF to use the UserNestedSerializer for the 'user' field
    user = UserNestedSerializer(read_only=True)

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
            "user",
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


# New serializer specifically for updating a vendor's own profile.
class UpdateVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        # List only the fields you want to be editable by an admin.
        fields = ["company_name", "location", "logo", "verified"]


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
