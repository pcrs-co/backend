# ai_recommender/management/commands/import_benchmarks.py

import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from ai_recommender.logic.utils import process_benchmark_dataframe
from ai_recommender.models import (
    CPUBenchmark,
    GPUBenchmark,
    DiskBenchmark,
)  # ++ ADDED DiskBenchmark


class Command(BaseCommand):
    help = "Imports CPU, GPU, or Disk benchmark data from spreadsheet files in the 'data' folder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            # ++ IMPROVED: Use choices for automatic validation ++
            choices=["cpu", "gpu", "disk"],
            help='The type of benchmark to import. Must be "cpu", "gpu", or "disk".',
            required=True,
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Deletes all existing records for the specified type before importing.",
        )
        parser.add_argument(
            "--file",
            type=str,
            help="Optional: a specific filename within the data directory to use.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        item_type = options["type"].lower()
        truncate = options["truncate"]
        override_file = options["file"]
        supported_extensions = (".csv", ".xlsx", ".xls", ".ods")

        # ++ CLEANER: Use a dictionary to map type strings to Django models ++
        MODEL_MAP = {
            "cpu": CPUBenchmark,
            "gpu": GPUBenchmark,
            "disk": DiskBenchmark,
        }
        ModelClass = MODEL_MAP[item_type]

        # --- 1. Locate the file ---
        data_dir = os.path.join(settings.BASE_DIR, "ai_recommender", "data")
        filepath = None

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
            # Auto-discovery logic will now work for 'disk' automatically
            for filename in os.listdir(data_dir):
                if filename.lower().startswith(item_type) and filename.lower().endswith(
                    supported_extensions
                ):
                    filepath = os.path.join(data_dir, filename)
                    break

            if not filepath:
                self.stdout.write(
                    self.style.ERROR(
                        f"No suitable file for '{item_type}' found in '{data_dir}'."
                    )
                )
                return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found file for '{item_type}': {os.path.basename(filepath)}"
            )
        )

        # --- 2. Truncate old records if requested ---
        if truncate:
            # This now works for any type thanks to the MODEL_MAP
            count, _ = ModelClass.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Truncated {count} existing '{item_type}' records.")
            )

        # --- 3. Read and process the spreadsheet ---
        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(filepath)
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(
                    filepath
                )  # Pandas can auto-detect the engine for xls/xlsx
            elif ext == ".ods":
                df = pd.read_excel(filepath, engine="odf")
            else:
                # This case is unlikely due to the file search, but good for safety
                raise ValueError(f"Unsupported file format: {ext}")

            # --- 4. Call central processing logic (already updated to handle 'disk') ---
            self.stdout.write("Processing records...")
            results = process_benchmark_dataframe(df, item_type)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import complete for '{item_type}'. Created: {results['created']}, Updated: {results['updated']}, Skipped: {results['skipped']}."
                )
            )

            if results["skipped"] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        "Some rows were skipped due to missing names or scores. Please check the warnings above."
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File could not be found at path: {filepath}")
            )
        except Exception as e:
            # General exception handler for pandas errors or other issues
            self.stdout.write(
                self.style.ERROR(f"An unexpected error occurred during processing: {e}")
            )
