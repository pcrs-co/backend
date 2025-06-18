from vendor.models import Product
from ..models import RecommendationSpecification
from django.db import models


def match_products_to_recommendation(rec: RecommendationSpecification):
    products = Product.objects.all()

    # CPU
    if rec.recommended_cpu_score:
        products = products.filter(processor__cpu_score__gte=rec.recommended_cpu_score)

    # GPU
    if rec.recommended_gpu_score:
        products = products.filter(graphic__gpu_score__gte=rec.recommended_gpu_score)

    # RAM
    if rec.recommended_ram:
        products = products.filter(memory__capacity_gb__gte=rec.recommended_ram)

    # Storage (prefer SSD if available)
    if rec.recommended_storage:
        products = products.filter(
            storage__capacity_gb__gte=rec.recommended_storage
        ).order_by(
            models.Case(
                models.When(storage__type__iexact="SSD", then=0),
                default=1,
                output_field=models.IntegerField(),
            )
        )

    return products
