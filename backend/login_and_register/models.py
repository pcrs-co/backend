from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20, unique=True)

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "date_of_birth",
    ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
