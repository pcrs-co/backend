from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from vendor.serializers import *
from vendor.models import *
from .serializers import *
from .models import *
import pandas as pd
import uuid


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class CPUBenchmarkViewSet(viewsets.ModelViewSet):
    queryset = CPUBenchmark.objects.all()
    serializer_class = CPUBenchmarkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        return self._handle_upload(request, item_type='cpu')

    def _handle_upload(self, request, item_type):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith((".xls", ".xlsx", ".ods")):
                df = pd.read_excel(file, engine="odf" if file.name.endswith(".ods") else None)
            else:
                return Response({"error": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)

            required_columns = {"name", "score"}
            if not required_columns.issubset(df.columns):
                return Response({"error": "Missing required columns (name, score)."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for _, row in df.iterrows():
                    name = row["name"]
                    score = int(row["score"])

                    CPUBenchmark.objects.update_or_create(name=name, defaults={"benchmark_score": score})

            return Response({"message": "CPU Benchmark upload successful!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GPUBenchmarkViewSet(viewsets.ModelViewSet):
    queryset = GPUBenchmark.objects.all()
    serializer_class = GPUBenchmarkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        return self._handle_upload(request, item_type='gpu')

    def _handle_upload(self, request, item_type):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith((".xls", ".xlsx", ".ods")):
                df = pd.read_excel(file, engine="odf" if file.name.endswith(".ods") else None)
            else:
                return Response({"error": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)

            required_columns = {"name", "score"}
            if not required_columns.issubset(df.columns):
                return Response({"error": "Missing required columns (name, score)."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for _, row in df.iterrows():
                    name = row["name"]
                    score = int(row["score"])

                    GPUBenchmark.objects.update_or_create(name=name, defaults={"benchmark_score": score})

            return Response({"message": "GPU Benchmark upload successful!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class UserPreferenceView(generics.CreateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        session_id = self.request.data.get("session_id") or str(uuid.uuid4())

        preference = serializer.save(user=user, session_id=session_id)

        answers = self.request.data.get("answers", {})
        for slug, value in answers.items():
            try:
                question = Question.objects.get(slug=slug)
                UserAnswer.objects.create(preference=preference, question=question, answer=value)
            except Question.DoesNotExist:
                continue


class RecommenderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        activities = request.data.get("activities", [])
        raw_budget = request.data.get("budget")

        if not activities:
            raise ValidationError("Activities are required.")

        try:
            budget = float(raw_budget) if raw_budget is not None else None
            if budget is not None and budget < 0:
                raise ValidationError("Budget must be positive.")
        except (ValueError, TypeError):
            raise ValidationError("Budget must be a valid number.")

        applications = Application.objects.filter(activity__name__in=activities)
        if not applications.exists():
            return Response({"error": "No applications found for selected activities."}, status=status.HTTP_404_NOT_FOUND)

        max_cpu_score = max_gpu_score = max_ram = max_storage = 0

        for app in applications:
            requirements = ApplicationSystemRequirement.objects.filter(application=app)
            for req in requirements:
                max_cpu_score = max(max_cpu_score, req.cpu_score or 0)
                max_gpu_score = max(max_gpu_score, req.gpu_score or 0)
                max_ram = max(max_ram, req.ram or 0)
                max_storage = max(max_storage, req.storage or 0)

        if max_cpu_score == max_gpu_score == max_ram == max_storage == 0:
            return Response({"error": "No system requirement data available."}, status=status.HTTP_404_NOT_FOUND)

        if not request.session.session_key:
            request.session.save()

        RecommendationSpecification.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key if not request.user.is_authenticated else None,
            min_cpu_score=max_cpu_score,
            min_gpu_score=max_gpu_score,
            min_ram=max_ram,
            min_storage=max_storage,
        )

        return Response({
            "specifications": {
                "cpu_score_minimum": max_cpu_score,
                "gpu_score_minimum": max_gpu_score,
                "ram_minimum_gb": max_ram,
                "storage_minimum_gb": max_storage,
            },
            "budget": budget,
        })


class ProductRecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key

        if not session_id and not user:
            request.session.save()
            session_id = request.session.session_key

        try:
            if user:
                spec = RecommendationSpecification.objects.filter(user=user).latest("created_at")
            else:
                spec = RecommendationSpecification.objects.filter(session_id=session_id).latest("created_at")
        except RecommendationSpecification.DoesNotExist:
            return Response({"error": "No recommendation specifications found."}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(
            processor__benchmark_score__gte=spec.min_cpu_score,
            gpu__benchmark_score__gte=spec.min_gpu_score,
            ram__size_gb__gte=spec.min_ram,
            storage__size_gb__gte=spec.min_storage,
        )

        if not products.exists():
            return Response({"error": "No products match the required specifications."}, status=status.HTTP_404_NOT_FOUND)

        return Response(ProductSerializer(products, many=True).data)

    def post(self, request, *args, **kwargs):
        spec_id = request.data.get("specification_id")
        if not spec_id:
            raise ValidationError("Specification ID is required.")

        spec = get_object_or_404(RecommendationSpecification, id=spec_id)

        products = Product.objects.filter(
            processor__benchmark_score__gte=spec.min_cpu_score,
            gpu__benchmark_score__gte=spec.min_gpu_score,
            ram__size_gb__gte=spec.min_ram,
            storage__size_gb__gte=spec.min_storage,
        )

        if not products.exists():
            return Response({"error": "No products match this specification."}, status=status.HTTP_404_NOT_FOUND)

        return Response(ProductSerializer(products, many=True).data)
