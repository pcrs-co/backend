from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *

router = DefaultRouter()
router.register("questions", QuestionViewSet)
router.register("cpu-benchmarks", CPUBenchmarkViewSet)
router.register("gpu-benchmarks", GPUBenchmarkViewSet)
router.register("activities", ActivityViewSet)
router.register("applications", ApplicationViewSet)
router.register("requirements", ApplicationSystemRequirementViewSet)

urlpatterns = [
    path("user_preference/", UserPreferenceView.as_view(), name="user_preference"),
    path("recommend/", RecommenderView.as_view(), name="recommend"),
    path("recommend_product/", ProductRecommendationView.as_view(), name="recommend"),
] + router.urls

