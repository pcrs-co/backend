from django.db.models.signals import post_migrate
from django.apps import AppConfig


class AiRecommenderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_recommender"
