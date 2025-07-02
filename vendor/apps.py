from django.apps import AppConfig


class VendorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vendor"

    def ready(self):
        """
        This method is called when the app is ready.
        We import our signals here to register them.
        """
        import vendor.signals
