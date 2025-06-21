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


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "phone_number",
            "region",
            "district",
            "email",
            "username",
            "avatar",
            "password",
            "password2",
        ]
        extra_kwargs = {
            "date_of_birth": {"required": False},
            "region": {"required": False},
            "district": {"required": False},
            "avatar": {"required": False},  # Also making avatar optional if not already
        }

    def validate_phone_number(self, phone):
        # Clean the phone number just like your form
        phone = re.sub(r"[^\d+]", "", phone)
        if not phone.startswith("+"):
            phone = "+255" + phone
        if not re.match(r"^\+\d{1,4}\d{7,15}$", phone):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return phone

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            region=validated_data.get("region"),
            district=validated_data.get("district"),
            date_of_birth=validated_data.get("date_of_birth"),
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
        )

        default_group, created = Group.objects.get_or_create(name="default")
        user.groups.add(default_group)

        return user


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class VendorSerializer(serializers.ModelSerializer):
    # User fields
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    region = serializers.CharField()
    district = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )

    # Vendor fields
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "company_name",
            "location",
            "email",
            "logo",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "region",
            "district",
            "password",  # Now properly named
        ]
        extra_kwargs = {
            "first_name": {"required": False, "allow_null": True},
            "last_name": {"required": False, "allow_null": True},
            "logo": {"required": False, "allow_null": True},
            "date_of_birth": {"required": False},
            "region": {"required": False},
            "district": {"required": False},
            "avatar": {"required": False},  # Also making avatar optional if not already
        }

    def create(self, validated_data):
        # Use .pop() safely. This is much cleaner.
        user_data = {
            "email": validated_data.pop("email"),
            "username": validated_data.pop("username"),
            "phone_number": validated_data.pop("phone_number"),
            "password": validated_data.pop("password"),
            "first_name": validated_data.pop(
                "first_name", ""
            ),  # Use default empty string
            "last_name": validated_data.pop(
                "last_name", ""
            ),  # Use default empty string
            "region": validated_data.pop("region", ""),  # Use default empty string
            "district": validated_data.pop("district", ""),  # Use default empty string
        }

        # The remaining keys in validated_data are for the Vendor model:
        # { 'company_name': '...', 'location': '...', 'logo': ... }

        # --- TRANSACTION ---
        # It's best practice to wrap creations in a transaction.
        # If the vendor creation fails, the user creation will be rolled back.
        try:
            with transaction.atomic():
                # Create user
                user = CustomUser.objects.create_user(**user_data)

                # Add to vendor group
                vendor_group, _ = Group.objects.get_or_create(name="vendor")
                user.groups.add(vendor_group)

                # Create vendor profile with the remaining data
                vendor = Vendor.objects.create(user=user, **validated_data)

        except Exception as e:
            # If anything goes wrong, raise a generic error that the view will catch
            # The original validation error (e.g., "username already exists") would have
            # been caught by serializer.is_valid() in the view.
            raise serializers.ValidationError(
                f"Failed to create user and vendor profile. Error: {str(e)}"
            )

        # Send credentials AFTER the transaction is successful
        # We pass the original, un-hashed password for the email
        self._send_welcome_email(user.email, user_data["password"])

        return vendor

    @staticmethod
    def generate_temp_password(length=12):
        characters = string.ascii_letters + string.digits + "@#$!%^&*"
        return "".join(random.choices(characters, k=length))

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
            # You can log this error to your error tracking system
            # or queue it for retry later


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


class VendorListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    region = serializers.CharField(source="user.region")
    district = serializers.CharField(source="user.district")
    phone_number = serializers.CharField(source="user.phone_number")

    class Meta:
        model = Vendor
        fields = [
            "id",
            "company_name",
            "location",
            "email",
            "logo",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "region",
            "district",
        ]
