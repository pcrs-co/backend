# ai_recommender/scripts/setup_groups.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from login_and_register.models import CustomUser  # adjust to your user model if needed


def create_default_groups():
    # Define groups
    group_definitions = {
        "admin": {
            "permissions": Permission.objects.all(),  # Full access (or filter if needed)
        },
        "vendor": {
            "permissions": [],
        },
        "default": {
            "permissions": [],
        },
    }

    for group_name, config in group_definitions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Created group: {group_name}")
        else:
            print(f"Group already exists: {group_name}")

        if isinstance(config["permissions"], list):
            # Fetch and assign permissions by codename
            for perm_codename in config["permissions"]:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission not found: {perm_codename}")
        else:
            # Assume it's a queryset or full set
            group.permissions.set(config["permissions"])
