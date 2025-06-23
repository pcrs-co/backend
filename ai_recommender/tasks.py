# ai_recommender/tasks.py

from celery import shared_task
from django.db import transaction
import pandas as pd
import base64
from io import BytesIO
from .models import CPUBenchmark, GPUBenchmark

MODEL_MAP = {
    "cpu": CPUBenchmark,
    "gpu": GPUBenchmark,
}


@shared_task
def process_benchmark_file(file_content_base64, file_name, item_type):
    """
    A Celery task to process an uploaded benchmark spreadsheet asynchronously.
    """
    try:
        file_content = base64.b64decode(file_content_base64)
        file_stream = BytesIO(file_content)

        if file_name.endswith(".csv"):
            df = pd.read_csv(file_stream)
        else:  # Handles .xls, .xlsx, .ods
            df = pd.read_excel(
                file_stream,
                engine=None if file_name.endswith((".xls", ".xlsx")) else "odf",
            )

        required_columns = {"name", "score"}
        if not required_columns.issubset(df.columns):
            print("Task failed: Missing required columns (name, score).")
            return "Missing required columns."

        model_class = MODEL_MAP.get(item_type)
        if not model_class:
            print(f"Task failed: Invalid item_type '{item_type}'.")
            return "Invalid item type."

        items_created, items_updated = 0, 0
        with transaction.atomic():
            for _, row in df.iterrows():
                if pd.isna(row.get("name")) or pd.isna(row.get("score")):
                    continue
                _, created = model_class.objects.update_or_create(
                    name=row["name"], defaults={"benchmark_score": int(row["score"])}
                )
                if created:
                    items_created += 1
                else:
                    items_updated += 1

        result_message = (
            f"Processing complete. Created: {items_created}, Updated: {items_updated}."
        )
        print(result_message)
        return result_message

    except Exception as e:
        print(f"An error occurred during benchmark file processing: {e}")
        return f"An error occurred: {str(e)}"
