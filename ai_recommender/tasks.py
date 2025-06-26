from datetime import timedelta
from .logic.ai_discovery import (
    discover_applications_for_activity,
    discover_and_save_requirements,
)
from .models import Activity, Application, CPUBenchmark, GPUBenchmark
from django.db import transaction
from django.utils import timezone
from celery import shared_task
from io import BytesIO
import pandas as pd
import base64


MODEL_MAP = {
    "cpu": CPUBenchmark,
    "gpu": GPUBenchmark,
}

from ai_recommender.logic.utils import process_benchmark_dataframe


@shared_task
def process_benchmark_file(file_content_base64, file_name, item_type):
    """
    A Celery task to process a base64-encoded benchmark spreadsheet file.
    Wraps the central processing logic.
    """
    try:
        file_content = base64.b64decode(file_content_base64)
        file_stream = BytesIO(file_content)

        file_name_lower = file_name.lower()
        if file_name_lower.endswith(".csv"):
            df = pd.read_csv(file_stream)
        elif file_name_lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_stream, engine=None)
        elif file_name_lower.endswith(".ods"):
            df = pd.read_excel(file_stream, engine="odf")
        else:
            raise ValueError(f"Unsupported file format: {file_name}")

        with transaction.atomic():
            results = process_benchmark_dataframe(df, item_type)

        result_message = f"Processed '{file_name}': Created {results['created']}, Updated {results['updated']}."
        print(result_message)
        return result_message

    except Exception as e:
        error_message = f"An error occurred during processing: {str(e)}"
        print(error_message)
        return error_message


@shared_task
def enrich_new_activity_task(activity_id):
    """
    A targeted background task to discover and enrich applications for a *single*, newly created activity.
    """
    try:
        activity = Activity.objects.get(id=activity_id)
        print(f"Starting enrichment task for newly created activity: '{activity.name}'")
    except Activity.DoesNotExist:
        print(f"Activity with ID {activity_id} not found. Aborting enrichment task.")
        return f"Task failed: Activity ID {activity_id} not found."

    # Step 1: Discover a list of applications for the activity using AI
    print(f"Discovering applications for '{activity.name}'...")
    discovered_app_names = discover_applications_for_activity(activity)

    if not discovered_app_names:
        print(f"No applications discovered for '{activity.name}'. Task finished.")
        return f"No applications found for {activity.name}."

    print(
        f"Discovered {len(discovered_app_names)} potential apps: {', '.join(discovered_app_names)}"
    )

    # Step 2: For each discovered application, find its system requirements
    enriched_count = 0
    for app_name in discovered_app_names:
        # We only enrich if the app is truly new or lacks requirements.
        # This prevents redundant AI calls if an app like 'Blender' is found for multiple activities.
        app = Application.objects.filter(name__iexact=app_name).first()
        if app and app.requirements.exists():
            print(
                f"Skipping enrichment for '{app_name}' as it already has requirements in the DB."
            )
            # Optional: You could still associate this existing app with the new activity here if needed.
            # app.activity.add(activity)
            continue

        print(f"Enriching '{app_name}' with system requirements...")
        try:
            # This function calls the AI and saves the requirements to the DB
            discover_and_save_requirements(app_name=app_name, activity=activity)
            enriched_count += 1
            print(f"Successfully enriched '{app_name}'.")
        except Exception as e:
            print(f"ERROR: Failed to enrich '{app_name}'. Reason: {e}")
            # Continue to the next app even if one fails.

    final_message = f"Enrichment task for '{activity.name}' complete. Enriched {enriched_count} new applications."
    print(final_message)
    return final_message


@shared_task
def enrich_all_activities_task():
    """
    Celery task to find new applications for EVERY activity in the database.
    """
    from .models import Activity, Application  # Local import

    activities = Activity.objects.all()
    print(f"Starting application discovery for {activities.count()} activities.")

    for activity in activities:
        print(f"Discovering apps for: {activity.name}")
        discovered_app_names = discover_applications_for_activity(activity)

        for app_name in discovered_app_names:
            # Check if we already have this application for this activity
            if not Application.objects.filter(
                name__iexact=app_name, activity=activity
            ).exists():
                print(
                    f"Found new potential application '{app_name}'. Enriching its requirements."
                )
                # This will create the app and its requirements if it doesn't exist at all
                discover_and_save_requirements(app_name, activity)

    return f"Activity enrichment complete."


@shared_task
def update_stale_system_requirements_task():
    """
    Finds applications with old requirements and re-runs the AI discovery to update them.
    This replaces the previous 'update_stale_applications' task.
    """
    from .models import Application  # Local import

    # Define "stale" as requirements not updated in the last 30 days
    stale_period = timezone.now() - timedelta(days=30)

    # We look at the Application's modified_at timestamp
    stale_apps = Application.objects.filter(modified_at__lt=stale_period)

    print(f"Found {stale_apps.count()} applications with stale requirements to update.")
    updated_count = 0
    for app in stale_apps:
        try:
            print(f"Updating requirements for: {app.name}")
            discover_and_save_requirements(app.name, app.activity)
            updated_count += 1
        except Exception as e:
            print(f"Failed to update {app.name}: {e}")
            continue

    return f"Requirement update task complete. Refreshed {updated_count} applications."
