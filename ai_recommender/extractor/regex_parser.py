import re


def parse_system_requirements(text):
    def extract(patterns):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def parse_numeric(value):
        match = re.search(r"(\d+)\s*(GB|gb)", value) if value else None
        return int(match.group(1)) if match else None

    return [
        {
            "type": "minimum",
            "cpu": extract([r"Minimum.*?CPU.*?:\s*(.+)", r"Processor.*?:\s*(.+)"]),
            "gpu": extract([r"Minimum.*?GPU.*?:\s*(.+)", r"Graphics.*?:\s*(.+)"]),
            "ram": parse_numeric(
                extract([r"Minimum.*?RAM.*?:\s*(.+)", r"Memory.*?:\s*(.+)"])
            ),
            "storage": parse_numeric(extract([r"Minimum.*?(Disk|Storage).*?:\s*(.+)"])),
            "notes": "Parsed via regex",
        },
        {
            "type": "recommended",
            "cpu": extract([r"Recommended.*?CPU.*?:\s*(.+)"]),
            "gpu": extract([r"Recommended.*?GPU.*?:\s*(.+)"]),
            "ram": parse_numeric(extract([r"Recommended.*?RAM.*?:\s*(.+)"])),
            "storage": parse_numeric(
                extract([r"Recommended.*?(Disk|Storage).*?:\s*(.+)"])
            ),
            "notes": "Parsed via regex",
        },
    ]
