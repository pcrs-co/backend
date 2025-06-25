from ..models import CPUBenchmark, GPUBenchmark
from decimal import Decimal, InvalidOperation
import pandas as pd
import re


def get_cpu_score(cpu_name):
    bench = (
        CPUBenchmark.objects.filter(cpu__icontains=cpu_name).order_by("-score").first()
    )
    return bench.score if bench else None


def get_gpu_score(gpu_name):
    bench = (
        GPUBenchmark.objects.filter(cpu__icontains=gpu_name).order_by("-score").first()
    )
    return bench.score if bench else None


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
    heaviest["storage"] = top_requirement.storage
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
    Processes a benchmark DataFrame and inserts/updates CPU or GPU benchmark records.
    """
    item_type = item_type.lower()

    if item_type == "cpu":
        ModelClass = CPUBenchmark
        name_field = "cpu"
        mark_field = "cpu_mark"
        mark_column = "cpu mark"
    elif item_type == "gpu":
        ModelClass = GPUBenchmark
        name_field = "gpu"
        mark_field = "gpu_mark"
        mark_column = "gpu mark"
    else:
        raise ValueError("Invalid item_type. Must be 'cpu' or 'gpu'.")

    df.columns = df.columns.str.strip().str.lower()
    required_cols = {"name", "score", mark_column, "price"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(
            f"Missing required columns: {missing}. Found: {list(df.columns)}"
        )

    created, updated = 0, 0
    for _, row in df.iterrows():
        if pd.isna(row["name"]) or pd.isna(row["score"]):
            continue

        component_name = str(row["name"]).strip()

        # Clean and parse score
        try:
            score_value = int(re.sub(r"[^\d]", "", str(row["score"])))
        except (ValueError, TypeError):
            print(f"Warning: Invalid score format for {component_name}. Skipping row.")
            continue

        # Clean and parse price
        price = None
        if pd.notna(row["price"]):
            try:
                cleaned_price_str = re.sub(r"[^\d.]", "", str(row["price"]))
                if cleaned_price_str:
                    price = Decimal(cleaned_price_str)
            except InvalidOperation:
                print(f"Warning: Invalid price format for {component_name}")

        lookup = {name_field: component_name}
        defaults = {
            "score": score_value,
            mark_field: str(row[mark_column]).strip(),
            "price": price,
        }

        _, was_created = ModelClass.objects.update_or_create(
            **lookup, defaults=defaults
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {"created": created, "updated": updated}
