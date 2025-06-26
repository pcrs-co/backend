from ..models import CPUBenchmark, GPUBenchmark, DiskBenchmark
from decimal import Decimal, InvalidOperation
import pandas as pd
import re


def compare_requirements(requirements):
    """Returns the heaviest requirement set based on score logic"""
    if not requirements.exists():
        return {
            "cpu_name": None,
            "gpu_name": None,
            "ram": 0,
            "storage": 0,
            "cpu_score": 0,
            "gpu_score": 0,
        }

    heaviest = {
        "cpu_name": "",
        "gpu_name": "",
        "ram": 0,
        "storage": 0,
        "cpu_score": 0,
        "gpu_score": 0,
        "notes": "",
    }

    all_notes = set()

    # Find the single most demanding requirement based on a combined score
    # This is a more robust way to find the "heaviest" overall spec
    top_requirement = max(
        requirements, key=lambda r: (r.cpu_score or 0) + (r.gpu_score or 0)
    )

    all_apps = ", ".join(set(r.application.name for r in requirements))

    # We now take all specs from this single heaviest requirement
    heaviest["cpu_name"] = top_requirement.cpu
    heaviest["gpu_name"] = top_requirement.gpu
    heaviest["ram"] = top_requirement.ram
    heaviest["storage_size"] = top_requirement.storage_size
    heaviest["cpu_score"] = top_requirement.cpu_score
    heaviest["gpu_score"] = top_requirement.gpu_score
    heaviest["notes"] = f"These specs are based on the requirements for: {all_apps}."

    # for req in requirements:
    #     cpu_score = req.cpu_score or get_cpu_score(req.cpu)
    #     gpu_score = req.gpu_score or get_gpu_score(req.gpu)

    #     # CPU
    #     if cpu_score > heaviest["cpu_score"]:
    #         heaviest["cpu_score"] = cpu_score

    #     # GPU
    #     if gpu_score > heaviest["gpu_score"]:
    #         heaviest["gpu_score"] = gpu_score

    #     # RAM
    #     if req.ram > heaviest["ram"]:
    #         heaviest["ram"] = req.ram

    #     # STORAGE
    #     storage_type = "SSD" if "ssd" in (req.notes or "").lower() else "HDD"
    #     is_current_ssd = storage_type == "SSD"
    #     is_heaviest_ssd = heaviest["storage_type"] == "SSD"

    #     if is_current_ssd and not is_heaviest_ssd:
    #         heaviest["storage"] = req.storage
    #         heaviest["storage_type"] = "SSD"
    #     elif is_current_ssd == is_heaviest_ssd and req.storage > heaviest["storage"]:
    #         heaviest["storage"] = req.storage

    return heaviest


def process_benchmark_dataframe(df: pd.DataFrame, item_type: str):
    """
    Processes a benchmark DataFrame and inserts/updates benchmark records.
    This version is robust against missing data and respects NOT NULL constraints.
    """
    item_type = item_type.lower()
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    )

    # ++ FIX: Initialize counters at the top ++
    created_count, updated_count = 0, 0
    skipped_count = 0

    col_map = {}
    if item_type == "cpu":
        ModelClass = CPUBenchmark
        col_map = {
            "cpuname": "cpu",
            "cpumark": "score",
            "rank": "rank",
            "cpuvalue": "value_score",
            "price": "price",
        }
        name_col_key, score_col_key = "cpuname", "cpumark"
    elif item_type == "gpu":
        ModelClass = GPUBenchmark
        col_map = {
            "videocardname": "gpu",
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
            "diskrating": "score",  # Matches your "diskratin" column
            "size": "size_tb",
            "rank": "rank",
            "drivevalue": "value_score",  # Matches your "drivevalue" column
            "price": "price",
        }
        name_col_key, score_col_key = "drivename", "diskrating"

    if not col_map:
        raise ValueError("Invalid item_type. Must be 'cpu', 'gpu', or 'disk'.")

    required_cols = {name_col_key, score_col_key}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(
            f"Missing required columns for type '{item_type}': {missing}. Found: {list(df.columns)}"
        )

    for index, row in df.iterrows():
        component_name = row.get(name_col_key)
        score_val = row.get(score_col_key)

        # ++ ROBUSTNESS: Skip rows with no name or no score ++
        if pd.isna(component_name) or pd.isna(score_val):
            print(
                f"  - WARNING: Skipping row {index + 2} due to missing name or score."
            )
            skipped_count += 1
            continue

        component_name = str(component_name).strip()
        defaults = {}

        # --- Process all other columns ---
        for standardized_name, model_field in col_map.items():
            value = row.get(standardized_name)
            if pd.isna(value):
                # We already handled required fields, so others can be None
                defaults[model_field] = None
                continue

            try:
                if model_field in ["score", "rank"]:
                    # Clean and convert to integer
                    cleaned_val = re.sub(r"[^\d]", "", str(value))
                    if cleaned_val:
                        defaults[model_field] = int(cleaned_val)
                    else:
                        # If score is empty after cleaning, it's invalid.
                        if model_field == "score":
                            raise ValueError("Score became empty after cleaning.")
                        defaults[model_field] = None
                elif model_field in ["value_score", "size_tb"]:
                    cleaned_val = re.sub(r"[^\d.]", "", str(value))
                    defaults[model_field] = float(cleaned_val) if cleaned_val else None
                elif model_field == "price":
                    price_str = re.sub(r"[^\d.]", "", str(value))
                    defaults[model_field] = Decimal(price_str) if price_str else None

            except (ValueError, TypeError, InvalidOperation) as e:
                # If a non-essential field fails to parse, we can live with it being null
                print(
                    f"  - WARNING: Could not parse field '{model_field}' for '{component_name}' on row {index + 2}. Value: '{value}'. Setting to NULL. Error: {e}"
                )
                defaults[model_field] = None

        # If a score couldn't be parsed, `defaults` won't have it. We must skip.
        if "score" not in defaults or defaults["score"] is None:
            print(
                f"  - WARNING: Skipping row {index + 2} for '{component_name}' because score could not be parsed."
            )
            skipped_count += 1
            continue

        # Use update_or_create to insert or update the record
        lookup = {col_map[name_col_key]: component_name}
        obj, was_created = ModelClass.objects.update_or_create(
            **lookup, defaults=defaults
        )

        if was_created:
            created_count += 1
        else:
            updated_count += 1

    # Add skipped count to the results
    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
    }


def clean_and_convert_to_int(value) -> int:
    """
    Cleans a string to extract an integer, handling common cases like '8 GB'.
    Returns 0 if conversion is not possible.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Find the first sequence of digits in the string
        match = re.search(r"\d+", value)
        if match:
            try:
                return int(match.group(0))
            except (ValueError, TypeError):
                return 0
    # Handle float or other numeric types if necessary
    if isinstance(value, float):
        return int(value)

    return 0


def find_best_benchmark(raw_name: str, component_type: str):
    """
    Takes a raw string from an AI (e.g., "Intel i7-9700K or AMD Ryzen 7 2700X")
    and finds the best matching benchmark from the database.

    Args:
        raw_name: The string from the AI.
        component_type: 'cpu' or 'gpu'.

    Returns:
        The best matching benchmark model instance, or None if no match is found.
    """
    if not raw_name or raw_name.lower() in ["none", "not specified", "n/a"]:
        return None

    # 1. Split the raw string into a list of potential candidates
    # We split by "or", "/", and "," and then clean up each part.
    candidates = re.split(r"\s+or\s+|\s*/\s*|,", raw_name, flags=re.IGNORECASE)
    cleaned_candidates = [c.strip() for c in candidates if c.strip()]

    if not cleaned_candidates:
        return None

    # 2. Build a dynamic query to find all possible matches
    ModelClass = CPUBenchmark if component_type == "cpu" else GPUBenchmark
    query = Q()
    for candidate in cleaned_candidates:
        # The query will be: Q(cpu__icontains='Intel Core i7-9700K') | Q(cpu__icontains='AMD Ryzen 7 2700X')
        query |= Q(**{f"{component_type}__icontains": candidate})

    # 3. Execute the query to get all potential benchmarks
    found_benchmarks = ModelClass.objects.filter(query)

    if not found_benchmarks.exists():
        return None

    # 4. Evaluate and select the best one (based on the highest score)
    # You could change `score` to `value_score` to prioritize economy
    best_match = max(found_benchmarks, key=lambda bench: bench.score)

    return best_match
