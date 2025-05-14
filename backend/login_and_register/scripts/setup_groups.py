# setup_groups.py
from django.contrib.auth.models import Group, Permission


def create_default_groups():
    group_definitions = {
        "admin": {
            "permissions": Permission.objects.all(),  # All permissions
        },
        "vendor": {
            "permissions": [],
        },
        "default": {
            "permissions": [],
        },
    }

    for group_name, config in group_definitions.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        if isinstance(config["permissions"], list):
            # Add new permissions by codename
            for perm_codename in config["permissions"]:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    if not group.permissions.filter(id=permission.id).exists():
                        group.permissions.add(permission)
                        print(f"Added {perm_codename} to {group_name}")
                except Permission.DoesNotExist:
                    print(f"Permission not found: {perm_codename}")
        else:
            # Set all permissions (e.g., for admin)
            group.permissions.set(config["permissions"])
            print(f"Set all permissions for {group_name}")
