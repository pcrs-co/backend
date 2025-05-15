from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *

router = DefaultRouter()
router.register("admin/questions", QuestionViewSet)
router.register("admin/cpu-benchmarks", CPUBenchmarkViewSet)
router.register("admin/gpu-benchmarks", GPUBenchmarkViewSet)
router.register("admin/activities", ActivityViewSet)
router.register("admin/applications", ApplicationViewSet)
router.register("admin/requirements", ApplicationSystemRequirementViewSet)

urlpatterns = [
    path("user_preference/", UserPreferenceView.as_view(), name="user_preference"),
    path("recommend/", RecommenderView.as_view(), name="recommend"),
    path("recommend_product/", ProductRecommendationView.as_view(), name="recommend"),
] + router.urls
