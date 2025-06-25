from ..models import CPUBenchmark, GPUBenchmark


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
