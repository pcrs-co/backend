from django.urls import path
from .views import *

urlpatterns = [
    path("user_preference/", UserPreferenceView.as_view(), name="user_preference"),
    path("recommend/", RecommenderView.as_view(), name="recommend"),
    path("recommend_product/", ProductRecommendationView.as_view(), name="recommend"),
]
