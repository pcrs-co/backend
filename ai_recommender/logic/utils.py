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

    heaviest = {
        "cpu_score": 0,
        "gpu_score": 0,
        "ram": 0,
        "storage": 0,
        "storage_type": "HDD",  # Assume HDD is lighter by default
    }

    for req in requirements:
        cpu_score = req.cpu_score or get_cpu_score(req.cpu)
        gpu_score = req.gpu_score or get_gpu_score(req.gpu)

        # CPU
        if cpu_score > heaviest["cpu_score"]:
            heaviest["cpu_score"] = cpu_score

        # GPU
        if gpu_score > heaviest["gpu_score"]:
            heaviest["gpu_score"] = gpu_score

        # RAM
        if req.ram > heaviest["ram"]:
            heaviest["ram"] = req.ram

        # STORAGE
        storage_type = "SSD" if "ssd" in (req.notes or "").lower() else "HDD"
        is_current_ssd = storage_type == "SSD"
        is_heaviest_ssd = heaviest["storage_type"] == "SSD"

        if is_current_ssd and not is_heaviest_ssd:
            heaviest["storage"] = req.storage
            heaviest["storage_type"] = "SSD"
        elif is_current_ssd == is_heaviest_ssd and req.storage > heaviest["storage"]:
            heaviest["storage"] = req.storage

    return heaviest
