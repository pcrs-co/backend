import re
import json


def extract_requirements_from_response(response: str):
    try:
        data = json.loads(response)
        return data  # Already structured!
    except json.JSONDecodeError:
        pass

    # Fallback regex parsing
    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', response)
    cpu_match = re.findall(r'"cpu"\s*:\s*"([^"]+)"', response)
    gpu_match = re.findall(r'"gpu"\s*:\s*"([^"]+)"', response)
    ram_match = re.findall(r'"ram"\s*:\s*(\d+)', response)
    storage_match = re.findall(r'"storage"\s*:\s*(\d+)', response)

    return {
        "name": name_match.group(1) if name_match else "Unknown App",
        "requirements": [
            {
                "type": "minimum",
                "cpu": cpu_match[0] if len(cpu_match) > 0 else None,
                "gpu": gpu_match[0] if len(gpu_match) > 0 else None,
                "ram": int(ram_match[0]) if len(ram_match) > 0 else 4,
                "storage": int(storage_match[0]) if len(storage_match) > 0 else 10,
            },
            {
                "type": "recommended",
                "cpu": cpu_match[1] if len(cpu_match) > 1 else None,
                "gpu": gpu_match[1] if len(gpu_match) > 1 else None,
                "ram": int(ram_match[1]) if len(ram_match) > 1 else 8,
                "storage": int(storage_match[1]) if len(storage_match) > 1 else 20,
            },
        ],
    }
