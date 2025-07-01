# in your_app/tasks.py
from celery import shared_task
from .models import (
    Product,
    CPUBenchmark,
    GPUBenchmark,
    find_best_benchmark_match,
)


@shared_task
def update_missing_product_scores(product_id=None):
    """
    Finds and updates cpu_score and gpu_score for products where it is missing.
    If product_id is provided, it only runs for that product.
    Otherwise, it runs for all products missing a score.
    """
    if product_id:
        products_to_check = Product.objects.filter(id=product_id)
    else:
        # Check all products where either score is null
        products_to_check = Product.objects.filter(
            Q(cpu_score__isnull=True) | Q(gpu_score__isnull=True)
        )

    updated_count = 0
    for product in products_to_check:
        updated = False
        # Check and update CPU score
        if (
            product.cpu_score is None
            and product.processor
            and product.processor.data_received
        ):
            best_match = find_best_benchmark_match(
                product.processor.data_received, CPUBenchmark
            )
            if best_match:
                product.cpu_score = best_match.score
                updated = True

        # Check and update GPU score
        if (
            product.gpu_score is None
            and product.graphic
            and product.graphic.data_received
        ):
            best_match = find_best_benchmark_match(
                product.graphic.data_received, GPUBenchmark
            )
            if best_match:
                product.gpu_score = best_match.score
                updated = True

        if updated:
            product.save(
                update_fields=["cpu_score", "gpu_score", "modified_at"]
            )  # Efficiently save only what changed
            updated_count += 1

    return f"Checked {products_to_check.count()} products and updated scores for {updated_count}."
