from django.db.models.signals import post_migrate
from django.apps import AppConfig


class LoginAndRegisterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "login_and_register"

    def ready(self):
        from .scripts.setup_groups import create_default_groups

        post_migrate.connect(lambda **kwargs: create_default_groups(), sender=self)
