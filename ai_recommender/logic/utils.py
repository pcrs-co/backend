# ai_recommender/logic/utils.py

from sentence_transformers import util
import json
import pandas as pd
import re
import difflib
from decimal import Decimal, InvalidOperation
from django.db.models import Q  # This import is only needed here
import numpy as np


def process_benchmark_dataframe(df: pd.DataFrame, item_type: str):
    """
    Processes a benchmark DataFrame and inserts/updates benchmark records.
    This function is fully compatible with the new models that auto-parse 'name'.
    """
    from ..models import CPUBenchmark, GPUBenchmark, DiskBenchmark

    item_type = item_type.lower()
    # Sanitize column headers for consistency
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    )

    created_count, updated_count, skipped_count = 0, 0, 0
    col_map = {}

    if item_type == "cpu":
        ModelClass = CPUBenchmark
        col_map = {
            "cpuname": "cpu",  # The 'name' field in the model
            "cpumark": "score",
            "rank": "rank",
            "cpuvalue": "value_score",
            "price": "price",
        }
        name_col_key, score_col_key = "cpuname", "cpumark"

    elif item_type == "gpu":
        ModelClass = GPUBenchmark
        col_map = {
            "videocardname": "gpu",  # The 'name' field in the model
            "g3dmark": "score",
            "rank": "rank",
            "videocardvalue": "value_score",
            "price": "price",
        }
        name_col_key, score_col_key = "videocardname", "g3dmark"

    elif item_type == "disk":
        ModelClass = DiskBenchmark
        col_map = {
            "drivename": "drive_name",
            "diskrating": "score",
            "size": "size_tb",
            "rank": "rank",
            "drivevalue": "value_score",
            "price": "price",
        }
        name_col_key, score_col_key = "drivename", "diskrating"

    else:
        raise ValueError("Invalid item_type. Must be 'cpu', 'gpu', or 'disk'.")

    required_cols = {name_col_key, score_col_key}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(
            f"Missing required columns for type '{item_type}': {missing}. Found: {list(df.columns)}"
        )

    # Use a list to bulk_create/update later for efficiency
    objects_to_update = []
    objects_to_create = []

    for index, row in df.iterrows():
        component_name = row.get(name_col_key)
        score_val = row.get(score_col_key)

        if (
            pd.isna(component_name)
            or pd.isna(score_val)
            or not str(component_name).strip()
        ):
            skipped_count += 1
            continue

        component_name = str(component_name).strip()
        defaults = {}

        for standardized_name, model_field in col_map.items():
            value = row.get(standardized_name)
            if pd.isna(value):
                defaults[model_field] = None
                continue

            try:
                if model_field in ["score", "rank"]:
                    cleaned_val = re.sub(r"[^\d]", "", str(value))
                    defaults[model_field] = int(cleaned_val) if cleaned_val else None
                elif model_field in ["value_score", "size_tb"]:
                    cleaned_val = re.sub(r"[^\d.]", "", str(value))
                    defaults[model_field] = float(cleaned_val) if cleaned_val else None
                elif model_field == "price":
                    price_str = re.sub(r"[^\d.]", "", str(value))
                    defaults[model_field] = Decimal(price_str) if price_str else None
                elif model_field == "name" or model_field == "drive_name":
                    defaults[model_field] = str(value).strip()

            except (ValueError, TypeError, InvalidOperation) as e:
                defaults[model_field] = None
                print(
                    f"Warning: Could not parse field '{model_field}' for '{component_name}'. Setting to NULL."
                )

        if defaults.get("score") is None:
            skipped_count += 1
            continue

        # Using update_or_create is fine for smaller datasets and ensures the custom .save() is called.
        # This is the simplest and most robust approach.
        lookup_key_for_model = col_map[name_col_key]
        lookup = {lookup_key_for_model: component_name}

        obj, was_created = ModelClass.objects.update_or_create(
            **lookup, defaults=defaults
        )

        if was_created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
    }


def _find_match_for_single_component(requirement_str: str, benchmark_model):
    """
    (HELPER) Finds the best single benchmark OBJECT for a single requirement string.
    This is the core logic engine that matches one component name.
    """
    if not requirement_str:
        return None
    clean_str = requirement_str.strip().lower()

    # Strategy 1: For CPUs, check for clock speed first as it's a strong indicator.
    if benchmark_model == CPUBenchmark:
        speed_match = re.search(r"(\d\.?\d*)\s*ghz", clean_str)
        if speed_match:
            speed = float(speed_match.group(1))
            # Find the best-scoring CPU that meets or exceeds the specified speed
            candidates = CPUBenchmark.objects.filter(clock_speed_ghz__gte=speed)
            if candidates.exists():
                return candidates.order_by("-score").first()

    # Strategy 2: Fuzzy String Match against the `model_name` for all component types.
    all_benchmarks = benchmark_model.objects.all()
    if not all_benchmarks:
        return None

    best_similarity, best_matches = 0.0, []
    # Use the structured `model_name` for matching, not the raw `name`.
    for bench in all_benchmarks:
        similarity = difflib.SequenceMatcher(
            None, clean_str, bench.model_name.lower()
        ).ratio()
        if similarity > best_similarity:
            best_similarity, best_matches = similarity, [bench]
        elif similarity == best_similarity:
            best_matches.append(bench)

    SIMILARITY_THRESHOLD = 0.7
    if best_similarity < SIMILARITY_THRESHOLD:
        return None

    # From the best string matches, return the one with the highest performance score.
    return max(best_matches, key=lambda b: b.score)


# --- NEW HELPER FUNCTIONS ---
_model = None  # Global cache for the sentence transformer model


def get_sentence_model():
    """Lazily loads and caches the SentenceTransformer model to save memory."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        print("Loading Sentence-BERT model for matching...")
        _model = SentenceTransformer("all-mpnet-base-v2")
    return _model


def _find_match_with_embeddings(requirement_str: str, benchmark_model_class):
    """
    (HELPER) Finds the best benchmark OBJECT for a single requirement string
    using pre-computed vector embeddings.
    """
    if not requirement_str:
        return None

    model = get_sentence_model()

    # 1. Get all pre-computed embeddings from the database
    benchmarks_with_embeddings = list(
        benchmark_model_class.objects.exclude(embedding__isnull=True)
    )
    if not benchmarks_with_embeddings:
        print(
            f"WARNING: No pre-computed embeddings found for {benchmark_model_class.__name__}. Matching will fail."
        )
        return None

    # --- FIX: Ensure a consistent data type (float32) for all embeddings ---
    corpus_embeddings = np.array(
        [json.loads(b.embedding) for b in benchmarks_with_embeddings],
        dtype=np.float32,  # Enforce float32
    )

    # 2. Create an embedding for the new requirement string
    query_embedding = model.encode(requirement_str, convert_to_tensor=False).astype(
        np.float32
    )  # Enforce float32

    # 3. Compute cosine similarities
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    # 4. Find the index of the highest score
    best_match_index = np.argmax(cos_scores)

    # 5. Check if the match is good enough
    SIMILARITY_THRESHOLD = 0.5
    if cos_scores[best_match_index] < SIMILARITY_THRESHOLD:
        print(
            f"  -> Match found, but score {cos_scores[best_match_index]:.2f} is below threshold {SIMILARITY_THRESHOLD}."
        )
        return None

    # 6. Return the corresponding benchmark object
    return benchmarks_with_embeddings[best_match_index]


# --- THIS REPLACES YOUR OLD `find_best_benchmark_object` ---
def find_best_benchmark_object(raw_name: str, component_type: str):
    """
    Takes a raw string from the AI (e.g., "Intel i7-9700K or AMD Ryzen 7 2700X")
    and finds the single best matching benchmark OBJECT from the database using embeddings.
    """
    from ..models import CPUBenchmark, GPUBenchmark

    if not raw_name or raw_name.lower() in ["none", "not specified", "n/a"]:
        return None

    candidates = re.split(r"\s+or\s+|\s*/\s*|,", raw_name, flags=re.IGNORECASE)
    cleaned_candidates = [c.strip() for c in candidates if c.strip()]

    if not cleaned_candidates:
        return None

    ModelClass = CPUBenchmark if component_type.lower() == "cpu" else GPUBenchmark

    found_benchmarks = []
    for candidate in cleaned_candidates:
        match = _find_match_with_embeddings(candidate, ModelClass)
        if match:
            found_benchmarks.append(match)

    if not found_benchmarks:
        return None

    # From all the valid matches, select the one with the highest performance score.
    return max(found_benchmarks, key=lambda bench: bench.score)


def find_similar_activities(activity_name):
    """
    Utility function to find and print activities similar to a given one.
    """
    from ..models import Activity

    try:
        target_activity = Activity.objects.get(name__iexact=activity_name)
    except Activity.DoesNotExist:
        print(f"Activity '{activity_name}' not found.")
        return

    all_other_activities = Activity.objects.exclude(pk=target_activity.pk)

    similarities = []
    for other in all_other_activities:
        similarity_data = target_activity.get_similarity_with(other)
        similarities.append((other.name, similarity_data))

    # Sort by the combined score, highest first
    similarities.sort(key=lambda x: x[1]["combined_score"], reverse=True)

    print(f"\nActivities most similar to '{target_activity.name}':")
    for name, data in similarities[:5]:  # Print top 5
        print(
            f"  - {name}: "
            f"Combined Score: {data['combined_score']:.3f} "
            f"(Apps: {data['jaccard_similarity']:.3f}, "
            f"Reqs: {data['requirement_similarity']:.3f})"
        )
