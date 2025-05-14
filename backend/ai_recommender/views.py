from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django.db import transaction
from vendor.serializers import *
from vendor.models import *
from .serializers import *
from .models import *
import uuid
import pandas as pd


class BenchmarkUploadView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admin can upload benchmarks

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        item_type = request.data.get("item_type")

        if not file or not item_type:
            return Response(
                {"error": "Both file and item_type are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item_type = item_type.lower()
        if item_type not in ["cpu", "gpu"]:
            return Response(
                {"error": "Invalid item_type. Must be 'cpu' or 'gpu'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith((".xls", ".xlsx", ".ods")):
                df = pd.read_excel(
                    file, engine="odf" if file.name.endswith(".ods") else None
                )
            else:
                return Response(
                    {"error": "Unsupported file type."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Expecting columns like: name, score
            required_columns = {"name", "score"}
            if not required_columns.issubset(df.columns):
                return Response(
                    {"error": "Missing required columns (name, score)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                for _, row in df.iterrows():
                    name = row["name"]
                    score = int(row["score"])

                    if item_type == "cpu":
                        CPUBenchmark.objects.update_or_create(
                            name=name, defaults={"benchmark_score": score}
                        )
                    elif item_type == "gpu":
                        GPUBenchmark.objects.update_or_create(
                            name=name, defaults={"benchmark_score": score}
                        )

            return Response(
                {"message": "Benchmark upload successful!"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPreferenceView(generics.CreateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = []  # Allow anonymous access

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        session_id = self.request.data.get("session_id") or str(uuid.uuid4())

        preference = serializer.save(user=user, session_id=session_id)

        answers = self.request.data.get("answers", {})
        for slug, value in answers.items():
            try:
                question = Question.objects.get(slug=slug)
                UserAnswer.objects.create(
                    preference=preference, question=question, answer=value
                )
            except Question.DoesNotExist:
                continue


class RecommenderView(APIView):
    """
    This view receives activities (and optional budget) from the user,
    calculates the minimum specifications needed (CPU, GPU, RAM, Storage),
    and returns them. It does NOT fetch vendor products.
    """

    permission_classes = []  # AllowAny by default

    def post(self, request, *args, **kwargs):
        activities = request.data.get("activities", [])
        raw_budget = request.data.get("budget")

        if not activities:
            raise ValidationError("Activities are required.")

        # Validate and parse budget (optional)
        budget = None
        if raw_budget is not None:
            try:
                budget = float(raw_budget)
                if budget < 0:
                    raise ValidationError("Budget must be a positive number.")
            except (ValueError, TypeError):
                raise ValidationError("Budget must be a valid number.")

        # Fetch applications related to the selected activities
        applications = Application.objects.filter(activity__name__in=activities)

        if not applications.exists():
            return Response(
                {"error": "No applications found for the selected activities."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Initialize maximum requirements
        max_cpu_score = 0
        max_gpu_score = 0
        max_ram = 0
        max_storage = 0

        # Find the maximum requirements across all applications
        for app in applications:
            requirements = ApplicationSystemRequirement.objects.filter(application=app)
            for req in requirements:
                max_cpu_score = max(max_cpu_score, req.cpu_score or 0)
                max_gpu_score = max(max_gpu_score, req.gpu_score or 0)
                max_ram = max(max_ram, req.ram or 0)
                max_storage = max(max_storage, req.storage or 0)

        # Check if we have any data
        if (
            max_cpu_score == 0
            and max_gpu_score == 0
            and max_ram == 0
            and max_storage == 0
        ):
            return Response(
                {
                    "error": "No system requirements data available for the selected applications."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Build the final response
        specifications = {
            "cpu_score_minimum": max_cpu_score,
            "gpu_score_minimum": max_gpu_score,
            "ram_minimum_gb": max_ram,
            "storage_minimum_gb": max_storage,
        }

        if not request.session.session_key:
            request.session.save()

        spec = RecommendationSpecification.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=(
                request.session.session_key
                if not request.user.is_authenticated
                else None
            ),
            min_cpu_score=max_cpu_score,
            min_gpu_score=max_gpu_score,
            min_ram=max_ram,
            min_storage=max_storage,
        )

        response_data = {
            "specifications": specifications,
            "budget": budget,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ProductRecommendationView(APIView):
    """
    This view fetches vendor products matching the last saved recommendation specifications.
    """

    permission_classes = []  # AllowAny by default

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        session_id = (
            request.session.session_key if not request.user.is_authenticated else None
        )

        # Ensure session exists for anonymous users
        if not session_id:
            request.session.save()
            session_id = request.session.session_key

        # Fetch the latest RecommendationSpecification
        try:
            if user:
                spec = RecommendationSpecification.objects.filter(user=user).latest(
                    "created_at"
                )
            else:
                spec = RecommendationSpecification.objects.filter(
                    session_id=session_id
                ).latest("created_at")
        except RecommendationSpecification.DoesNotExist:
            return Response(
                {"error": "No recommendation specifications found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch products matching the spec
        products = Product.objects.filter(
            processor__benchmark_score__gte=spec.min_cpu_score,
            gpu__benchmark_score__gte=spec.min_gpu_score,
            ram__size_gb__gte=spec.min_ram,
            storage__size_gb__gte=spec.min_storage,
        )

        if not products.exists():
            return Response(
                {"error": "No products match the required specifications."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize products
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        spec_id = request.data.get("specification_id")

        if not spec_id:
            raise ValidationError("Specification ID is required.")

        spec = get_object_or_404(RecommendationSpecification, id=spec_id)

        # Fetch products matching or exceeding the specifications
        products = Product.objects.filter(
            cpu__benchmark_score__gte=spec.min_cpu_score,
            gpu__benchmark_score__gte=spec.min_gpu_score,
            ram__size_gb__gte=spec.min_ram,
            storage__size_gb__gte=spec.min_storage,
        )

        # Optional: Filter by budget if budget exists
        if spec.budget:
            products = products.filter(price__lte=spec.budget)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def migrate_guest_preferences(request):
    session_id = request.data.get("session_id")

    if not session_id:
        return Response({"error": "Session ID is required."}, status=400)

    preferences = UserPreference.objects.filter(
        session_id=session_id, user__isnull=True
    )

    if preferences.exists():
        preferences.update(user=request.user)
        return Response({"message": "Preferences migrated successfully."}, status=200)

    return Response({"message": "No guest preferences found to migrate."}, status=404)
