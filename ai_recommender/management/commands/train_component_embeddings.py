# ai_recommender/management/commands/train_component_embeddings.py

import json
import time
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from sentence_transformers import SentenceTransformer
from ai_recommender.models import CPUBenchmark, GPUBenchmark


def process_in_batches(model_class, sentence_model, batch_size=100):
    """
    Helper function to process a model's objects in batches to prevent
    database timeouts and memory issues.
    """
    # Get the name of the text field ('cpu' or 'gpu')
    text_field_name = "cpu" if model_class == CPUBenchmark else "gpu"

    # Get total count for progress tracking
    queryset = model_class.objects.all()
    total_count = queryset.count()

    if total_count == 0:
        return 0

    updated_count = 0
    # Process the queryset in batches
    for i in range(0, total_count, batch_size):
        # Ensure the database connection is alive before each batch
        connection.ensure_connection()

        batch_qs = list(queryset[i : i + batch_size])

        # Get the names to be encoded
        names_to_encode = [getattr(b, "model_name") for b in batch_qs]

        print(
            f"\nProcessing batch {i//batch_size + 1} for {model_class.__name__} (items {i+1}-{min(i+batch_size, total_count)}/{total_count})..."
        )

        # Encode the batch of names
        embeddings = sentence_model.encode(names_to_encode, show_progress_bar=True)

        # Assign the new embeddings to the objects
        for benchmark, embedding in zip(batch_qs, embeddings):
            benchmark.embedding = json.dumps(embedding.tolist())

        # Bulk update the current batch
        model_class.objects.bulk_update(batch_qs, ["embedding"])
        updated_count += len(batch_qs)

        # A small sleep can also help prevent overwhelming the system
        time.sleep(0.5)

    return updated_count


class Command(BaseCommand):
    help = "Generates and stores vector embeddings for CPU and GPU benchmarks."

    # We don't need a single transaction for the whole command,
    # as we are processing in independent batches.
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("--- Starting Component Embedding Training ---")
        )

        # 1. Load the sentence transformer model once
        self.stdout.write("Loading Sentence-BERT model (this may take a moment)...")
        try:
            sentence_model = SentenceTransformer("all-mpnet-base-v2")
            self.stdout.write(self.style.SUCCESS("Model loaded successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to load model. Error: {e}"))
            return

        # 2. Process CPUs using the batching helper
        self.stdout.write("\n--- Processing CPU Benchmarks ---")
        try:
            cpu_updated = process_in_batches(CPUBenchmark, sentence_model)
            if cpu_updated > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully updated embeddings for {cpu_updated} CPUs."
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("No CPUs found to process."))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An error occurred during CPU processing: {e}")
            )

        # 3. Process GPUs using the batching helper
        self.stdout.write("\n--- Processing GPU Benchmarks ---")
        try:
            gpu_updated = process_in_batches(GPUBenchmark, sentence_model)
            if gpu_updated > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully updated embeddings for {gpu_updated} GPUs."
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("No GPUs found to process."))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An error occurred during GPU processing: {e}")
            )

        self.stdout.write(
            self.style.SUCCESS("\n--- Component Embedding Training Complete! ---")
        )
