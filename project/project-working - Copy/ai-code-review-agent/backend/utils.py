import json
from typing import Any, Dict


import re

def safe_parse_json(s: str) -> Any:
    """
    Cleans model output (removes markdown blocks and fixes formatting)
    before parsing JSON.
    """
    if not s:
        raise ValueError("Empty model output")

    s = s.strip()

    # Remove markdown ```json ``` wrappers
    s = re.sub(r"^```json", "", s)
    s = re.sub(r"^```", "", s)
    s = re.sub(r"```$", "", s)

    s = s.strip()

    # Try normal parse first
    try:
        return json.loads(s)
    except Exception:
        # Try extracting JSON between first { and last }
        start = s.find('{')
        end = s.rfind('}')
        if start != -1 and end != -1 and end > start:
            snippet = s[start:end+1]
            try:
                return json.loads(snippet)
            except Exception as e:
                raise ValueError(f"Failed to parse JSON from model output: {e}")

        raise ValueError("No JSON found in model output")

def calculate_improvement_percentage(old_score: float, new_score: float) -> float:
    """Return improvement percentage from old_score to new_score. Values 0-100."""
    try:
        old = float(old_score)
        new = float(new_score)
    except Exception:
        return 0.0
    if old <= 0:
        # if old is 0, treat improvement as new*100
        return round(max(0.0, min(100.0, new)), 2)
    change = ((new - old) / old) * 100.0
    return round(change, 2)
