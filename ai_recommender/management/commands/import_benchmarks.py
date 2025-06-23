import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from ai_recommender.logic.utils import process_benchmark_dataframe
from ai_recommender.models import CPUBenchmark, GPUBenchmark


class Command(BaseCommand):
    help = (
        "Imports CPU or GPU benchmark data from spreadsheet files in the 'data' folder."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--type", type=str, help='Must be "cpu" or "gpu".', required=True
        )
        parser.add_argument(
            "--truncate", action="store_true", help="Deletes all existing records."
        )
        parser.add_argument(
            "--file",
            type=str,
            help="Optional specific filename to override auto-discovery.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        item_type = options["type"].lower()
        truncate = options["truncate"]
        override_file = options["file"]
        supported_extensions = (".csv", ".xlsx", ".xls", ".ods")

        # Resolve the data directory
        app_name = "ai_recommender"
        data_dir = os.path.join(settings.BASE_DIR, app_name, "data")
        filepath = None

        # --- 1. Locate the file ---
        if not os.path.isdir(data_dir):
            self.stdout.write(self.style.ERROR(f"Data directory not found: {data_dir}"))
            return

        if override_file:
            filepath = os.path.join(data_dir, override_file)
            if not os.path.isfile(filepath):
                self.stdout.write(
                    self.style.ERROR(f"Specified file not found: {filepath}")
                )
                return
        else:
            for filename in os.listdir(data_dir):
                if filename.lower().startswith(item_type) and filename.lower().endswith(
                    supported_extensions
                ):
                    filepath = os.path.join(data_dir, filename)
                    break

            if not filepath:
                self.stdout.write(
                    self.style.ERROR(
                        f"No suitable file for '{item_type}' found in '{data_dir}' with extensions: {supported_extensions}"
                    )
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f"Found file: {os.path.basename(filepath)}")
        )

        # --- 2. Truncate old records if requested ---
        if truncate:
            ModelClass = CPUBenchmark if item_type == "cpu" else GPUBenchmark
            count, _ = ModelClass.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Truncated {count} records."))

        # --- 3. Read the spreadsheet ---
        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(filepath)
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(filepath, engine=None)
            elif ext == ".ods":
                df = pd.read_excel(filepath, engine="odf")
            else:
                raise ValueError(f"Unsupported file format: {filepath}")

            # --- 4. Call central processing logic ---
            results = process_benchmark_dataframe(df, item_type)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import finished. Created: {results['created']}, Updated: {results['updated']}."
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Processing failed: {e}"))
