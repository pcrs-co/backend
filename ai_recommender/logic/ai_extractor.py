# ai_recommender/logic/ai_extractor.py

import json
from collections import Counter

def extract_requirements_from_response(response: str):
    """
    Safely attempts to parse a single JSON string.
    """
    try:
        # The AI might still wrap the response in markdown
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        return data
    except (json.JSONDecodeError, AttributeError):
        # Return None if parsing fails, so we can filter it out
        return None

def find_consensus_response(responses: list[str]):
    """
    Parses multiple AI responses and finds the best one through consensus.
    """
    if not responses:
        raise ValueError("No valid AI responses provided to find consensus.")

    # Step 1: Parse all responses into structured Python objects
    parsed_data = [extract_requirements_from_response(resp) for resp in responses]
    valid_data = [d for d in parsed_data if d and 'requirements' in d and len(d['requirements']) == 2]

    if not valid_data:
        raise ValueError("None of the AI responses could be parsed into a valid structure.")

    # Step 2: Vote on the most common values for key fields
    # We use tuples to make dicts hashable for the Counter
    
    # Vote on the "recommended" specs as they are most important
    rec_specs_tuples = []
    for data in valid_data:
        # Find the 'recommended' dictionary
        rec_dict = next((item for item in data['requirements'] if item.get('type') == 'recommended'), None)
        if rec_dict:
            # Create a stable, hashable representation of the specs
            spec_tuple = (
                rec_dict.get('cpu', '').strip(),
                rec_dict.get('gpu', '').strip(),
                rec_dict.get('ram'),
            )
            rec_specs_tuples.append(spec_tuple)

    if not rec_specs_tuples:
         # Fallback to the first valid response if voting fails
        return valid_data[0]

    # Find the most common spec set
    most_common_spec, _ = Counter(rec_specs_tuples).most_common(1)[0]
    
    # Step 3: Find the full original dictionary that matches the winning vote
    for data in valid_data:
        rec_dict = next((item for item in data['requirements'] if item.get('type') == 'recommended'), None)
        if rec_dict:
            spec_tuple = (
                rec_dict.get('cpu', '').strip(),
                rec_dict.get('gpu', '').strip(),
                rec_dict.get('ram'),
            )
            if spec_tuple == most_common_spec:
                print(f"Consensus found. Choosing response with recommended specs: {spec_tuple}")
                return data # Return the entire JSON object from the "winner"
    
    # Fallback to the first valid response if no match is found (should be rare)
    return valid_data[0]