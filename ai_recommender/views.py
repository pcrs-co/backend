# ai_recommender/views.py
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *
from .logic.recommendation_engine import generate_recommendation
from .mixins import AsynchronousBenchmarkUploadMixin
from vendor.models import Product
from vendor.serializers import ProductRecommendationSerializer

# ===================================================================
# Admin ViewSets for Benchmark Management
# ===================================================================


class CPUBenchmarkViewSet(AsynchronousBenchmarkUploadMixin, viewsets.ModelViewSet):
    queryset = CPUBenchmark.objects.all().order_by("-score")
    serializer_class = CPUBenchmarkSerializer
    permission_classes = [IsAuthenticated]  # Or IsAdminUser for more security

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        return self._handle_upload(request, item_type="cpu")


class GPUBenchmarkViewSet(AsynchronousBenchmarkUploadMixin, viewsets.ModelViewSet):
    queryset = GPUBenchmark.objects.all().order_by("-score")
    serializer_class = GPUBenchmarkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        return self._handle_upload(request, item_type="gpu")


class DiskBenchmarkViewSet(AsynchronousBenchmarkUploadMixin, viewsets.ModelViewSet):
    queryset = DiskBenchmark.objects.all().order_by("-score")
    serializer_class = DiskBenchmarkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        return self._handle_upload(request, item_type="disk")


# ===================================================================
# Admin ViewSets for Core Data
# ===================================================================


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]


class ApplicationSystemRequirementViewSet(viewsets.ModelViewSet):
    queryset = ApplicationSystemRequirement.objects.all()
    serializer_class = ApplicationSystemRequirementSerializer
    permission_classes = [IsAuthenticated]


# ===================================================================
# Main User-Facing API Views
# ===================================================================


class UserPreferenceView(APIView):
    """
    Handles the submission of a user's preferences.
    This view accepts the user's activities and applications, saves them,
    and triggers a high-priority background task to enrich the data.
    """

    permission_classes = [AllowAny]  # Allow anonymous users

    def post(self, request):
        # The serializer now handles creating the preference and triggering the Celery task.
        serializer = UserPreferenceSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # We return a simple success message. The frontend knows to start polling.
        return Response(
            {"message": "Preferences received and analysis started."},
            status=status.HTTP_201_CREATED,
        )


class GenerateRecommendationView(APIView):
    """
    Generates and returns the final hardware specifications.
    This is the endpoint the frontend will poll.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        # The session_id comes from the frontend API call
        session_id = request.data.get("session_id")

        if not user and not session_id:
            return Response(
                {"error": "User or session_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recommendation = generate_recommendation(user=user, session_id=session_id)

        if not recommendation:
            return Response(
                {
                    "error": "Could not determine any specs. The AI might still be processing your request."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use the dedicated serializer to format the response correctly for the frontend.
        serializer = RecommendationSpecificationSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductRecommendationView(APIView):
    """
    Finds and returns a paginated list of products that meet or exceed
    the user's generated recommended specifications.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get("session_id")

        if not user and not session_id:
            return Response(
                {"error": "User or session_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build the filter based on whether a user is logged in or anonymous
        spec_filter = (
            {"user": user}
            if user and user.is_authenticated
            else {"session_id": session_id}
        )

        rec_spec = (
            RecommendationSpecification.objects.filter(**spec_filter)
            .order_by("-created_at")
            .first()
        )

        if not rec_spec or not rec_spec.recommended_cpu_score:
            return Response(
                {
                    "error": "No recommendation specification found for this user/session. Please generate specs first."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Filter products that meet or exceed the *recommended* specs for the best experience.
        products = Product.objects.filter(
            cpu_score__gte=rec_spec.recommended_cpu_score,
            gpu_score__gte=rec_spec.recommended_gpu_score,
            # We can use the 'memory' related name from the Product model
            memory__capacity_gb__gte=rec_spec.recommended_ram,
            # And the 'storage' related name
            storage__capacity_gb__gte=rec_spec.recommended_storage_size,
        ).order_by(
            "price"
        )  # Order by price to show the most affordable options first

        # Paginate the response
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductRecommendationSerializer(paginated_products, many=True)

        return paginator.get_paginated_response(serializer.data)
