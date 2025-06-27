from celery import shared_task
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import time
import base64
from io import BytesIO
import pandas as pd
from .models import Activity, UserPreference
from .logic.ai_discovery import discover_and_enrich_apps_for_activity


@shared_task
def process_benchmark_file(file_content_base64, file_name, item_type):
    """A Celery task to process a base64-encoded benchmark spreadsheet file."""
    from .logic.utils import process_benchmark_dataframe  # Local import

    try:
        # ... (Your file processing logic is excellent and does not need changes)
        file_content = base64.b64decode(file_content_base64)
        df = pd.read_excel(
            BytesIO(file_content)
        )  # pd.read_excel is often robust enough for xlsx, xls, ods
        results = process_benchmark_dataframe(df, item_type)
        return f"Processed '{file_name}': Created {results['created']}, Updated {results['updated']}."
    except Exception as e:
        return f"An error occurred during processing: {str(e)}"


# +++ REFACTORED to use the new "one-shot" enrichment logic +++
@shared_task
def enrich_user_preference_task(preference_id):
    """
    Orchestrates the enrichment process for a user's preference.
    It intelligently checks which activities are new and require AI discovery.
    """
    try:
        preference = UserPreference.objects.prefetch_related("activities").get(
            id=preference_id
        )
        user_activities = preference.activities.all()
    except UserPreference.DoesNotExist:
        print(f"Task Aborted: Preference with ID {preference_id} not found.")
        return

    print(f"--- Starting Enrichment for Preference {preference_id} ---")

    for activity in user_activities:
        # --- THIS IS THE KEY CONDITIONAL LOGIC ---
        # Check if the activity already has applications linked in our database.
        if activity.applications.exists():
            print(
                f"-> Activity '{activity.name}' is already enriched. Linking existing apps to preference."
            )
            # Link all of its existing apps to the current user's preference
            existing_apps = activity.applications.all()
            preference.applications.add(*existing_apps)
            continue

        # --- If the activity is NEW, then we run our powerful AI discovery ---
        print(
            f"-> Activity '{activity.name}' is new or not yet enriched. Running AI discovery..."
        )

        # This one function does everything: calls the AI, parses, and saves.
        newly_processed_apps = discover_and_enrich_apps_for_activity(activity)

        if newly_processed_apps:
            # Link the newly discovered and created apps to the current user's preference
            preference.applications.add(*newly_processed_apps)
            print(
                f"-> Successfully processed {len(newly_processed_apps)} apps for '{activity.name}'."
            )
        else:
            print(f"-> AI discovery failed or returned no apps for '{activity.name}'.")

        # Add a delay to be safe with API limits, even though we make fewer calls now.
        time.sleep(5)

    final_message = f"Enrichment task complete for preference {preference_id}."
    print(f"--- {final_message} ---")
    return final_message


@shared_task
def periodically_enrich_activities_task():
    """
    A weekly task that iterates through all known activities in the database
    and runs the AI discovery process to find and add any new, popular applications
    that may have emerged.
    """
    print(f"--- [{timezone.now()}] Starting Weekly Activity Enrichment Task ---")
    all_activities = Activity.objects.all()

    if not all_activities.exists():
        print("No activities found in the database. Task finished.")
        return "No activities to process."

    print(f"Found {all_activities.count()} activities to check for enrichment.")

    for activity in all_activities:
        print(f"\n-> Processing activity: '{activity.name}' (ID: {activity.id})")

        # The function `discover_and_enrich_apps_for_activity` is perfect for this.
        # It calls the AI, gets the current top apps, and uses get_or_create,
        # so it will only add applications that don't already exist by name.
        # It intelligently handles both new and existing apps.
        newly_processed_apps = discover_and_enrich_apps_for_activity(activity)

        if newly_processed_apps:
            print(
                f"-> Enrichment successful for '{activity.name}'. Processed {len(newly_processed_apps)} applications."
            )
        else:
            print(
                f"-> Enrichment for '{activity.name}' resulted in no new applications or failed."
            )

        # Be a good citizen to the AI API provider, even on a weekly task.
        time.sleep(10)

    final_message = f"--- Weekly Activity Enrichment Task Completed Successfully at {timezone.now()} ---"
    print(final_message)
    return final_message
