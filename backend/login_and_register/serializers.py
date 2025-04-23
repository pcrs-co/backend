from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework import serializers
from .models import *
import string
import random
import re


class RegisterSerializer(serializers.ModelSerializer):
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
            "password",
            "password2",
        ]

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
            region=validated_data["region"],
            district=validated_data["district"],
            date_of_birth=validated_data["date_of_birth"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
        )

        default_group, created = Group.objects.get_or_create(name="default")
        user.groups.add(default_group)

        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["avatar"]


class VendorSerializer(serializers.ModelSerializer):
    # Fields from CustomUser
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    region = serializers.CharField()
    district = serializers.CharField()
    phone_number = serializers.CharField()

    # Extra fields
    temporary_password = serializers.CharField(write_only=True, required=False)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Vendor
        fields = [
            "company_name",
            "location",
            "logo",
            "email",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "region",
            "district",
            "temporary_password",
        ]

    def create(self, validated_data):
        # Extract CustomUser fields
        email = validated_data.pop("email")
        username = validated_data.pop("username")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        phone_number = validated_data.pop("phone_number")
        region = validated_data.pop("region")
        district = validated_data.pop("district")

        # Generate random password
        temporary_password = validated_data.pop(
            "temporary_password", self._generate_temp_password()
        )

        # Create the user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=temporary_password,
            phone_number=phone_number,
            region=region,
            district=district,
        )

        # Add to 'vendor' group
        vendor_group, _ = Group.objects.get_or_create(name="vendor")
        user.groups.add(vendor_group)

        # Create Vendor profile
        vendor = Vendor.objects.create(user=user, **validated_data)

        # Send email verification / welcome email
        self._send_email(user.email, temporary_password)

        return vendor

    def generate_temp_password(length=12):
        characters = string.ascii_letters + string.digits + "@#$!%^&*"
        return "".join(random.choices(characters, k=length))

    def _send_email(self, to_email, password):
        subject = "Your Vendor Account Details"
        message = f"Welcome! Here are your login credentials:\n\nTemporary Password: {password}\n\nPlease log in and change your password."
        send_mail(subject, message, "no-reply@example.com", [to_email])


class ProductSerializer(serializers.ModelSerializer):
    pass
