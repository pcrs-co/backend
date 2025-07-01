from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *

router = DefaultRouter()
router.register("admin/cpu-benchmarks", CPUBenchmarkViewSet)
router.register("admin/gpu-benchmarks", GPUBenchmarkViewSet)
router.register("admin/disk-benchmarks", DiskBenchmarkViewSet)
router.register("admin/activities", ActivityViewSet)
router.register("admin/applications", ApplicationViewSet)
router.register("admin/requirements", ApplicationSystemRequirementViewSet)

urlpatterns = [
    path(
        "suggestions/", SuggestionView.as_view(), name="suggestions-list"
    ),  # <-- ADD THIS
    path(
        "recommend/",
        RecommendView.as_view(),
        name="generate-recommendation",
    ),
    path("recommend_product/", ProductRecommendationView.as_view(), name="recommend"),
    path(
        "history/recommendations/",
        UserHistoryView.as_view(),
        name="user-recommendation-history",
    ),
    path(
        "recommend/latest/",
        LatestRecommendationView.as_view(),
        name="latest-recommendation",
    ),  # ADD
] + router.urls
