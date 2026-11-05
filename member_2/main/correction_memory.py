import json
from pathlib import Path

MEMORY_FILE = Path("correction_memory.json")


def load_corrections():
    """
    Load previously saved SQL corrections.
    """

    if not MEMORY_FILE.exists():
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_correction(original_sql, corrected_sql, error_message):
    """
    Save a successful SQL correction to memory.
    Avoid storing duplicate corrections.
    """

    corrections = load_corrections()

    correction = {
        "original_sql": original_sql,
        "corrected_sql": corrected_sql,
        "error_message": error_message,
    }

    # Check whether this correction already exists
    if correction not in corrections:
        corrections.append(correction)

        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(corrections, file, indent=4)


def get_corrections():
    """
    Return all saved corrections.
    """

    return load_corrections()
