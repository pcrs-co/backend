# ai_recommender/extractor/extractor_utils.py
import logging

logger = logging.getLogger(__name__)


def compare_extractions(regex_data, llm_data):
    """
    Compares the parsed regex output with LLM output.
    Returns a dict of fields where regex extraction is missing or differs.
    """
    diffs = {}
    for idx, (regex, llm) in enumerate(zip(regex_data, llm_data)):
        for field in ["cpu", "gpu", "ram", "storage"]:
            regex_val = regex.get(field)
            llm_val = llm.get(field)
            if regex_val != llm_val:
                diffs.setdefault(idx, {})[field] = {
                    "regex": regex_val,
                    "llm": llm_val,
                }
    return diffs


def log_differences(app_name, diffs):
    """
    Logs differences in a structured way.
    """
    if not diffs:
        logger.info(f"No differences for '{app_name}' – regex matches LLM.")
        return

    logger.info(f"Differences for '{app_name}':")
    for idx, fields in diffs.items():
        logger.info(f"  Requirement set {idx + 1}:")
        for field, values in fields.items():
            logger.info(f"    Field: {field}")
            logger.info(f"      Regex: {values['regex']}")
            logger.info(f"      LLM: {values['llm']}")
