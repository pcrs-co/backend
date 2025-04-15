from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import *
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
            "middle_name",
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
            middle_name=validated_data.get("middle_name", ""),
            surname=validated_data["last_name"],
            surname=validated_data["region"],
            surname=validated_data["district"],
            date_of_birth=validated_data["date_of_birth"],
            email_address=validated_data["email"],
            phone_number=validated_data["phone_number"],
        )

        default_group, created = Group.objects.get_or_create(name="default")
        user.groups.add(default_group)

        return user


class ProductSerializer(serializers.ModelSerializer):
    pass


class VendorSerializer(serializers.ModelSerializer):
    pass
