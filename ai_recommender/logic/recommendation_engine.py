# ai_recommender/logic/recommendation_engine.py

# We no longer need F, Sum, etc. here, simplifying imports
from .ai_scraper import get_ai_response
import json

# The old helper functions (get_heaviest_requirement, _populate_spec_defaults) are no longer needed and can be deleted.


def generate_recommendation(user=None, session_id=None):
    """
    Generates a complete RecommendationSpecification by asking the AI to synthesize
    user needs into a final, structured output in a single step.
    """
    from ..models import (
        RecommendationFeedback,
        RecommendationLog,
        UserPreference,
        RecommendationSpecification,
    )

    # 1. Get the user's most recent preference
    pref_filter = {}
    if user and user.is_authenticated:
        pref_filter["user"] = user
    elif session_id:
        pref_filter["session_id"] = session_id
    else:
        return None

    pref = UserPreference.objects.filter(**pref_filter).order_by("-created_at").first()

    if not pref:
        print(f"No preferences found for user/session.")
        return None

    # 2. Construct the new, all-in-one AI prompt
    # This prompt asks the AI to perform the synthesis itself.

    activity_names = list(pref.activities.values_list("name", flat=True))

    prompt = f"""
    You are an expert PC hardware analyst. Your task is to act as a complete recommendation engine.
    Analyze the user's needs and generate a complete, structured JSON response containing the final PC hardware specification.

    **USER'S STATED NEEDS:**
    - Primary Activities: {", ".join(activity_names)}
    - Other Considerations: {pref.considerations or "None provided."}

    **YOUR REQUIRED STEPS:**
    1.  **Identify Key Software:** Mentally identify 3-5 key software titles or games relevant to the user's needs. Do NOT include these in the final output.
    2.  **Determine Requirements:** For each software, determine its minimum and recommended system requirements.
    3.  **Synthesize the Final Specification:**
        - For CPU and GPU, select the name and score of the single MOST demanding "recommended" requirement.
        - For RAM, select the highest "recommended" RAM value.
        - For Storage Size, SUM the storage requirements of ALL identified software to get a total or provide a reasonable estimate.
        - For Storage Type, choose 'SSD' if any recommended spec requires it, otherwise 'HDD'.
    4.  **Write a Summary:** Based on the user's needs and the specs you just synthesized, write a friendly, encouraging "ai_title" and "ai_summary" for the recommendation.
    5.  **Format Output:** Your entire response MUST be a single, valid JSON object with the exact structure below.

    **CRITICAL FORMATTING RULES:**
    - All `_score` and `_ram` fields MUST be integers.
    - `storage_size` MUST be an integer representing the total GB.
    - The JSON must be complete and valid.

    **FINAL JSON STRUCTURE:**
    {{
      "ai_title": "The 4K Gaming & Streaming Powerhouse",
      "ai_summary": "This build is designed to handle modern gaming at high settings while streaming. The CPU and GPU are top-tier for performance, and there's plenty of fast storage for all your games and recordings.",
      "min_cpu_name": "Intel Core i5-8400",
      "min_gpu_name": "Nvidia GeForce GTX 1060",
      "min_cpu_score": 9226,
      "min_gpu_score": 9088,
      "min_ram": 8,
      "min_storage_size": 250,
      "min_storage_type": "SSD",
      "recommended_cpu_name": "Intel Core i7-12700K",
      "recommended_gpu_name": "Nvidia GeForce RTX 3070",
      "recommended_cpu_score": 34571,
      "recommended_gpu_score": 21509,
      "recommended_ram": 16,
      "recommended_storage_size": 500,
      "recommended_storage_type": "SSD"
    }}
    """

    # 3. Get the AI's response
    raw_response = get_ai_response(prompt)
    if not raw_response:
        print("AI failed to return a recommendation response.")
        return None

    try:
        # The AI's response IS the data for our new object
        ai_generated_data = json.loads(raw_response)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON from AI recommendation response: {raw_response}")
        return None

    # 4. Create the RecommendationSpecification directly from the AI's output
    # The **ai_generated_data unpacks the dictionary to fill the model fields.
    rec_spec = RecommendationSpecification.objects.create(
        user=pref.user,
        session_id=str(pref.session_id) if not pref.user else None,
        source_preference=pref,
        **ai_generated_data,
    )
    print(
        f"Created new AI-generated recommendation {rec_spec.id} for preference {pref.id}."
    )

    # 5. Create associated log and feedback objects (this logic is still useful)
    RecommendationFeedback.objects.create(recommendation=rec_spec)
    RecommendationLog.objects.create(
        source_preference=pref,
        final_recommendation=rec_spec,
        activities_json=activity_names,
        # We can't log individual apps anymore, but we can log the AI's raw output for debugging
        applications_json=ai_generated_data,
    )

    return rec_spec
