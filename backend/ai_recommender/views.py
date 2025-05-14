from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework import status, viewsets, generics
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Q, F
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
                UserAnswer.objects.create(
                    preference=preference, question=question, answer=value
                )
            except Question.DoesNotExist:
                continue


class RecommenderView(APIView):
    def post(self, request):
        # Step 1: Determine if user is logged in
        user = request.user if request.user.is_authenticated else None
        session_id = request.data.get("session_id")  # For guest users

        if not user and not session_id:
            return Response(
                {"error": "User not logged in and session_id missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 2: Fetch the latest UserPreference (based on user or session_id)
        try:
            if user:
                preference = UserPreference.objects.filter(user=user).latest(
                    "created_at"
                )
            else:
                preference = UserPreference.objects.filter(
                    session_id=session_id
                ).latest("created_at")
        except UserPreference.DoesNotExist:
            return Response(
                {"error": "No user preferences found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Step 3: Get all applications linked to selected activities
        applications = Application.objects.filter(
            activity__in=preference.activities.all()
        )

        # Step 4: Gather all "recommended" requirements from those applications
        all_requirements = ApplicationSystemRequirement.objects.filter(
            application__in=applications, type="recommended"
        )

        if not all_requirements.exists():
            return Response(
                {"error": "No system requirements found for the selected activities."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Step 5: Aggregate the highest values across all requirements
        max_cpu_score = max(req.cpu_score for req in all_requirements)
        max_gpu_score = max(req.gpu_score for req in all_requirements)
        max_ram = max(req.ram for req in all_requirements)
        max_storage = max(req.storage for req in all_requirements)

        # Get best-matching CPU and GPU objects from benchmark
        best_cpu = CPUBenchmark.objects.filter(score=max_cpu_score).first()
        best_gpu = GPUBenchmark.objects.filter(score=max_gpu_score).first()

        # Step 6: Save the aggregated recommendation
        rec_spec = RecommendationSpecification.objects.create(
            user=user if user else None,
            session_id=str(session_id) if not user else None,
            min_cpu_score=max_cpu_score,
            min_gpu_score=max_gpu_score,
            min_ram=max_ram,
            min_storage=max_storage,
        )

        # Build response
        return Response(
            {
                "recommendation_id": rec_spec.id,
                "cpu": {
                    "name": best_cpu.cpu if best_cpu else "Unknown",
                    "score": max_cpu_score,
                },
                "gpu": {
                    "name": best_gpu.cpu if best_gpu else "Unknown",
                    "score": max_gpu_score,
                },
                "min_ram": max_ram,
                "min_storage": max_storage,
            },
            status=status.HTTP_201_CREATED,
        )


class ProductRecommendationView(APIView):
    permission_classes = [AllowAny]

    def get_recommendation_spec(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get("session_id")

        return (
            RecommendationSpecification.objects.filter(
                user=user if user else None,
                session_id=None if user else session_id,
            )
            .order_by("-created_at")
            .first()
        )

    def parse_storage_values(self, value):
        try:
            return int(value.replace("GB", "").strip())
        except:
            return None

    def get(self, request):
        spec = self.get_recommendation_spec(request)
        if not spec:
            return Response(
                {"error": "No recommendation specification found."}, status=404
            )

        cpu_required = spec.min_cpu_score
        gpu_required = spec.min_gpu_score
        ram_required = spec.min_ram
        storage_required = spec.min_storage

        fallback = False
        fallback_margin = 0.85  # 85% of required score

        matched_products = []
        products = Product.objects.all()

        for product in products:
            cpu = CPUBenchmark.objects.filter(
                cpu__icontains=product.processor.data_received
            ).first()
            gpu = GPUBenchmark.objects.filter(
                cpu__icontains=product.graphic.data_received
            ).first()

            if not cpu or not gpu:
                continue

            ram = self.parse_storage_values(product.memory.data_received)
            storage = self.parse_storage_values(product.storage.data_received)

            if ram is None or storage is None:
                continue

            cpu_ok = cpu.score >= cpu_required
            gpu_ok = gpu.score >= gpu_required
            ram_ok = ram >= ram_required
            storage_ok = storage >= storage_required

            if cpu_ok and gpu_ok and ram_ok and storage_ok:
                product.cpu_score = cpu.score
                product.gpu_score = gpu.score
                product.match_strength = (
                    "Exceeds"
                    if cpu.score > cpu_required + 1000
                    and gpu.score > gpu_required + 1000
                    else "Meets"
                )
                matched_products.append(product)

        # Fallback logic if no matching products
        if not matched_products:
            fallback = True
            for product in products:
                cpu = CPUBenchmark.objects.filter(
                    cpu__icontains=product.processor.data_received
                ).first()
                gpu = GPUBenchmark.objects.filter(
                    cpu__icontains=product.graphic.data_received
                ).first()
                if not cpu or not gpu:
                    continue

                ram = self.parse_storage_values(product.memory.data_received)
                storage = self.parse_storage_values(product.storage.data_received)
                if ram is None or storage is None:
                    continue

                cpu_ok = cpu.score >= cpu_required * fallback_margin
                gpu_ok = gpu.score >= gpu_required * fallback_margin
                ram_ok = ram >= ram_required
                storage_ok = storage >= storage_required

                if cpu_ok and gpu_ok and ram_ok and storage_ok:
                    product.cpu_score = cpu.score
                    product.gpu_score = gpu.score
                    product.match_strength = "Fallback"
                    matched_products.append(product)

        # Optional: top CPUs/GPUs
        top_cpus = CPUBenchmark.objects.order_by("-score")[:5]
        top_gpus = GPUBenchmark.objects.order_by("-score")[:5]

        return Response(
            {
                "recommendation": RecommendationSpecificationDetailedSerializer(
                    spec
                ).data,
                "products": ProductSerializer(matched_products, many=True).data,
                "top_cpus": CPUBenchmarkSerializer(top_cpus, many=True).data,
                "top_gpus": GPUBenchmarkSerializer(top_gpus, many=True).data,
                "is_fallback": fallback,
                "message": (
                    "Fallback products suggested."
                    if fallback
                    else "Filtered products based on main spec components."
                ),
            }
        )

    def post(self, request, *args, **kwargs):
        spec_id = request.data.get("specification_id")
        if not spec_id:
            raise ValidationError("Specification ID is required.")

        spec = get_object_or_404(RecommendationSpecification, id=spec_id)

        cpu_required = spec.min_cpu_score
        gpu_required = spec.min_gpu_score
        ram_required = spec.min_ram
        storage_required = spec.min_storage
        fallback = False
        fallback_margin = 0.85

        matched_products = []
        products = Product.objects.all()

        for product in products:
            cpu = CPUBenchmark.objects.filter(
                cpu__icontains=product.processor.data_received
            ).first()
            gpu = GPUBenchmark.objects.filter(
                cpu__icontains=product.graphic.data_received
            ).first()
            if not cpu or not gpu:
                continue

            ram = self.parse_storage_values(product.memory.data_received)
            storage = self.parse_storage_values(product.storage.data_received)
            if ram is None or storage is None:
                continue

            cpu_ok = cpu.score >= cpu_required
            gpu_ok = gpu.score >= gpu_required
            ram_ok = ram >= ram_required
            storage_ok = storage >= storage_required

            if cpu_ok and gpu_ok and ram_ok and storage_ok:
                matched_products.append(product)

        if not matched_products:
            fallback = True
            for product in products:
                cpu = CPUBenchmark.objects.filter(
                    cpu__icontains=product.processor.data_received
                ).first()
                gpu = GPUBenchmark.objects.filter(
                    cpu__icontains=product.graphic.data_received
                ).first()
                if not cpu or not gpu:
                    continue

                ram = self.parse_storage_values(product.memory.data_received)
                storage = self.parse_storage_values(product.storage.data_received)
                if ram is None or storage is None:
                    continue

                cpu_ok = cpu.score >= cpu_required * fallback_margin
                gpu_ok = gpu.score >= gpu_required * fallback_margin
                ram_ok = ram >= ram_required
                storage_ok = storage >= storage_required

                if cpu_ok and gpu_ok and ram_ok and storage_ok:
                    matched_products.append(product)

        return Response(
            {
                "recommendation": RecommendationSpecificationDetailedSerializer(
                    spec
                ).data,
                "products": ProductSerializer(matched_products, many=True).data,
                "is_fallback": fallback,
                "message": (
                    "Fallback products suggested."
                    if fallback
                    else "Filtered products based on main spec components."
                ),
            }
        )
