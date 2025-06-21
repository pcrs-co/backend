from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework import serializers
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
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    region = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        validators=[validate_password],
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
            "password",
        ]

    def validate_phone_number(self, phone):
        phone = re.sub(r"[^\d+]", "", phone)
        if not phone.startswith("+"):
            phone = "+255" + phone
        if not re.match(r"^\+\d{1,4}\d{7,15}$", phone):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return phone

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def create(self, validated_data):
        try:
            # Extract user data
            user_data = {
                "email": validated_data.pop("email"),
                "username": validated_data.pop("username"),
                "first_name": validated_data.pop("first_name"),
                "last_name": validated_data.pop("last_name"),
                "phone_number": validated_data.pop("phone_number"),
                "region": validated_data.get("region", ""),
                "district": validated_data.get("district", ""),
                "password": validated_data.pop(
                    "password", self.generate_temp_password()
                ),
            }

            # Create user
            user = CustomUser.objects.create_user(**user_data)

            # Add to vendor group
            vendor_group, _ = Group.objects.get_or_create(name="vendor")
            user.groups.add(vendor_group)

            # Create vendor profile
            vendor = Vendor.objects.create(user=user, **validated_data)

            # Send credentials
            self._send_welcome_email(user.email, user_data["password"])

            return vendor
        except Exception as e:
            # Log the error for debugging
            print(f"Error creating vendor: {str(e)}")
            raise serializers.ValidationError(
                {"non_field_errors": ["Failed to create vendor. Please try again."]}
            )

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
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
            # Consider logging this error properly


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
