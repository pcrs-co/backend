# ai_recommender/scripts/fetch_applications.py

from ai_recommender.models import Activity, Application, ApplicationSystemRequirement

example_data = {
    "video editing": [
        {
            "name": "Adobe Premiere Pro",
            "source": "https://www.adobe.com/products/premiere.html",
            "intensity_level": "high",
            "requirements": [
                {
                    "type": "minimum",
                    "cpu": "Intel 6th Gen or AMD Ryzen 1000",
                    "gpu": "NVIDIA GTX 1050 / AMD RX 560",
                    "ram": 8,
                    "storage": 8,
                    "notes": "Runs best with SSD. Needs Windows 10.",
                },
                {
                    "type": "recommended",
                    "cpu": "Intel 10th Gen / Ryzen 3000",
                    "gpu": "NVIDIA RTX 2060 / AMD RX 6700",
                    "ram": 16,
                    "storage": 20,
                    "notes": "Ideal on Windows 11 with GPU acceleration.",
                },
            ],
        },
        # You can add more apps and activities here...
    ]
}


def populate_apps():
    for activity_name, apps in example_data.items():
        activity, _ = Activity.objects.get_or_create(name=activity_name)
        for app in apps:
            application = Application.objects.create(
                activity=activity,
                name=app["name"],
                source=app["source"],
                intensity_level=app["intensity_level"],
            )
            for req in app["requirements"]:
                ApplicationSystemRequirement.objects.create(
                    application=application,
                    type=req["type"],
                    cpu=req["cpu"],
                    gpu=req["gpu"],
                    ram=req["ram"],
                    storage=req["storage"],
                    notes=req.get("notes", ""),
                )
