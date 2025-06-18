from rest_framework.permissions import IsAuthenticated, AllowAny
from ai_recommender.logic.recommendation_engine import generate_recommendation
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework import status, viewsets, generics
from ai_recommender.logic.enrich_app_data import enrich_application
from vendor.serializers import ProductSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, F
from django.db import transaction
from vendor.serializers import *
from vendor.models import *
from .serializers import *
from .models import *
import pandas as pd
import uuid


class CPUBenchmarkViewSet(viewsets.ModelViewSet):
    queryset = CPUBenchmark.objects.all()
    serializer_class = CPUBenchmarkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        return self._handle_upload(request, item_type="cpu")

    def _handle_upload(self, request, item_type):
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST
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

                    CPUBenchmark.objects.update_or_create(
                        name=name, defaults={"benchmark_score": score}
                    )

            return Response(
                {"message": "CPU Benchmark upload successful!"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GPUBenchmarkViewSet(viewsets.ModelViewSet):
    queryset = GPUBenchmark.objects.all()
    serializer_class = GPUBenchmarkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        return self._handle_upload(request, item_type="gpu")

    def _handle_upload(self, request, item_type):
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST
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

                    GPUBenchmark.objects.update_or_create(
                        name=name, defaults={"benchmark_score": score}
                    )

            return Response(
                {"message": "GPU Benchmark upload successful!"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class UserPreferenceView(APIView):
    def post(self, request):
        serializer = UserPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        preference = serializer.save()

        return Response(
            {"message": "Preference saved and applications enriched."},
            status=status.HTTP_201_CREATED,
        )


class GenerateRecommendationView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.data.get("session_id")

        recommendation = generate_recommendation(user=user, session_id=session_id)
        if not recommendation:
            return Response({"error": "No preferences found"}, status=400)

        return Response(
            {
                "min_cpu_score": recommendation.min_cpu_score,
                "min_gpu_score": recommendation.min_gpu_score,
                "min_ram": recommendation.min_ram,
                "min_storage": recommendation.min_storage,
            }
        )


class ProductRecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get("session_id")

        # Get latest recommendation spec
        rec = (
            (
                RecommendationSpecification.objects.filter(user=user)
                if user
                else RecommendationSpecification.objects.filter(session_id=session_id)
            )
            .order_by("-created_at")
            .first()
        )

        if not rec:
            return Response({"error": "No recommendation found."}, status=404)

        # Filter products that meet or exceed recommended specs
        products = Product.objects.filter(
            cpu_score__gte=rec.recommended_cpu_score,
            gpu_score__gte=rec.recommended_gpu_score,
            memory__capacity_gb__gte=rec.recommended_ram,
            storage__capacity_gb__gte=rec.recommended_storage,
        ).order_by("price")

        # Paginate response
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductRecommendationSerializer(paginated_products, many=True)

        return paginator.get_paginated_response(serializer.data)
