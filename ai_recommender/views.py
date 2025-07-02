# ai_recommender/views.py
from django.db.models import Case, When, F, FloatField, Value
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *
from .logic.recommendation_engine import generate_recommendation
from .logic.ai_discovery import discover_and_enrich_apps_for_activity
from .mixins import AsynchronousBenchmarkUploadMixin
from vendor.models import Product
from vendor.serializers import ProductRecommendationSerializer
from .logic.matching_engine import find_matching_products


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


class RecommendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        This single endpoint now orchestrates the entire recommendation process.
        1. Validates user input and creates a UserPreference.
        2. Runs AI discovery to find applications for the given activities.
        3. Generates the final hardware specification recommendation.
        4. Returns the specs to the frontend.
        """
        # Step 1: Validate input and create the UserPreference object
        # We can still use our excellent serializer for this.
        serializer = UserPreferenceSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # The .save() method on the serializer will create the preference and link activities
        preference = serializer.save()

        # --- Step 2: Perform AI Enrichment Synchronously ---
        # Instead of a Celery task, we do the work right here, because the user is waiting.
        user_activities = preference.activities.all()
        # --- GET THE CONSIDERATIONS FROM THE PREFERENCE OBJECT ---
        user_considerations = preference.considerations

        print(f"--- Starting Synchronous Enrichment for Preference {preference.id} ---")
        for activity in user_activities:
            # Only run the expensive AI call if we don't already have data for this activity
            if not activity.applications.exists():
                print(f"-> Activity '{activity.name}' is new. Running AI discovery...")
                # --- PASS CONSIDERATIONS TO THE FUNCTION ---
                newly_processed_apps = discover_and_enrich_apps_for_activity(
                    activity, user_considerations
                )
                if newly_processed_apps:
                    preference.applications.add(*newly_processed_apps)
            else:
                print(
                    f"-> Activity '{activity.name}' is already known. Linking existing apps."
                )
                existing_apps = activity.applications.all()
                preference.applications.add(*existing_apps)

        print(f"--- Enrichment complete for Preference {preference.id} ---")

        # --- Step 3: Generate the final recommendation ---
        # This function will now find a fully enriched preference object
        user = request.user if request.user.is_authenticated else None
        session_id = preference.session_id if not user else None

        final_spec = generate_recommendation(user=user, session_id=session_id)

        if not final_spec:
            return Response(
                {
                    "detail": "Could not generate a recommendation. The AI may have been unable to find requirements for the specified activities."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # --- Step 4: Serialize and return the result ---
        result_serializer = RecommendationSpecificationSerializer(final_spec)
        return Response(result_serializer.data, status=status.HTTP_200_OK)


class ProductRecommendationView(APIView):
    permission_classes = [AllowAny]
    from vendor.serializers import ProductRecommendationSerializer

    def get(self, request, *args, **kwargs):
        # 1. Get the user's latest recommendation spec
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get("session_id")
        if not user and not session_id:
            return Response(
                {"error": "User or session_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        if not rec_spec:
            return Response(
                {"error": "No recommendation found."}, status=status.HTTP_404_NOT_FOUND
            )

        # 2. Get the desired spec level from the request
        spec_level = request.query_params.get("spec_level", "recommended").lower()

        # --- 3. CALL THE MATCHING ENGINE ---
        # All the complex logic is now in one place.
        matching_products = find_matching_products(rec_spec, spec_level)

        # 4. Apply optional budget filter
        max_price_str = request.query_params.get("max_price")
        if max_price_str:
            try:
                matching_products = matching_products.filter(
                    price__lte=Decimal(max_price_str)
                )
            except (InvalidOperation, ValueError):
                pass

        # 5. Paginate and Serialize
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(matching_products, request)

        # We still pass context to the serializer so it can generate helpful tags
        serializer_context = {
            "request": request,
            "rec_spec": rec_spec,
            "spec_level": spec_level,
        }
        serializer = ProductRecommendationSerializer(
            paginated_products, many=True, context=serializer_context
        )

        return paginator.get_paginated_response(serializer.data)


class SuggestionView(generics.GenericAPIView):
    """
    Provides a list of all unique activity names for frontend autocomplete suggestions.
    This endpoint is public and cached for performance.
    """

    permission_classes = [AllowAny]
    serializer_class = SuggestionSerializer

    def get(self, request, *args, **kwargs):
        # Fetch unique, non-empty activity names, ordered alphabetically
        activities = (
            Activity.objects.values_list("name", flat=True).distinct().order_by("name")
        )

        # Create the data structure the serializer expects
        data = {"activities": list(activities)}

        return Response(data, status=status.HTTP_200_OK)


class LatestRecommendationView(APIView):
    """
    Fetches the most recent RecommendationSpecification for the current user
    or session_id, allowing the results page to be reloaded.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get("session_id")

        if not user and not session_id:
            return Response(
                {"detail": "User or session ID must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        spec_filter = {}
        if user:
            spec_filter["user"] = user
        else:
            spec_filter["session_id"] = session_id

        # Find the most recently created recommendation that matches
        latest_spec = (
            RecommendationSpecification.objects.filter(**spec_filter)
            .order_by("-created_at")
            .first()
        )

        if not latest_spec:
            return Response(
                {"detail": "No recommendations found for this session."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RecommendationSpecificationSerializer(latest_spec)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Add at the end of ai_recommender/views.py


class UserHistoryView(generics.ListAPIView):
    """
    Returns the recommendation history for the currently authenticated user.
    """

    serializer_class = UserRecommendationHistorySerializer  # Use our new serializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Show all history, no pagination

    def get_queryset(self):
        # Filter for the current user and order by most recent first
        return RecommendationSpecification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
