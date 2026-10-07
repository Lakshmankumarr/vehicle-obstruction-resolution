"""
Vehicle number format validation, normalization, and privacy masking utilities.
Supports standard Indian registration formats, Bharat (BH) Series, and regional variations.
"""
import re
from typing import List

# Valid Indian license plate regex patterns
VEHICLE_PATTERNS: List[str] = [
    r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$",  # Standard: DL01AB1234, MH12DE1433, KA05MB9999
    r"^[A-Z]{2}[0-9]{1}[A-Z]{1,2}[0-9]{4}$",  # Variation: TN8F4089, DL1C1234
    r"^[0-9]{2}BH[0-9]{4}[A-Z]{1,2}$",       # Bharat (BH) Series: 22BH1234AA
    r"^[A-Z]{2}[0-9]{6}$",                    # Commercial/Govt 6-digit: DL123456
    r"^[A-Z]{3}[0-9]{4}$",                    # Vintage / short: ABC1234
    r"^[0-9]{2}[A-Z]{2}[0-9]{4}$",            # 12AB3456
    r"^[A-Z]{2}[0-9]{4}[A-Z]{2}$",            # DL1234AB
]

# Recognizable Indian State & Union Territory prefixes
VALID_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DD", "DL", "DN",
    "GA", "GJ", "HR", "HP", "JH", "JK", "KA", "KL", "LA", "LD",
    "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "PB", "PY", "RJ",
    "SK", "TN", "TS", "TR", "UP", "UK", "WB", "BH"
}


def normalize_vehicle_number(vehicle_number: str) -> str:
    """
    Normalizes vehicle number by removing all whitespace, dashes, dots,
    and converting to uppercase.
    Example: 'mh-12 ab 1234' -> 'MH12AB1234'
    """
    if not vehicle_number:
        return ""
    # Strip any punctuation, spaces, dashes
    return re.sub(r"[^A-Za-z0-9]", "", vehicle_number).upper()


def validate_vehicle_format(vehicle_number: str) -> bool:
    """
    Validates whether a vehicle number matches valid Indian license plate formats.
    """
    normalized = normalize_vehicle_number(vehicle_number)
    if len(normalized) < 6 or len(normalized) > 12:
        return False

    for pattern in VEHICLE_PATTERNS:
        if re.match(pattern, normalized):
            return True

    return False


def mask_vehicle_number(vehicle_number: str) -> str:
    """
    Masks vehicle number for privacy.
    Preserves state code prefix and last 4 digits, masking middle digits.
    Example: 'DL01AB1234' -> 'DL01•••1234'
    """
    if not vehicle_number:
        return ""
    normalized = normalize_vehicle_number(vehicle_number)
    length = len(normalized)
    
    if length <= 4:
        return normalized[0] + "*" * (length - 2) + normalized[-1] if length > 2 else normalized
    elif length <= 7:
        return normalized[:2] + "*" * (length - 4) + normalized[-2:]
    else:
        # Standard 10-char: show first 4 and last 3 or first 2 and last 4
        # e.g., MH12****1234
        masked_chars = length - 6
        return normalized[:2] + "**" + "*" * (masked_chars) + normalized[-4:]


def get_format_requirements() -> str:
    """Returns human-readable instructions for plate formatting."""
    return (
        "Vehicle number must be 6-11 characters, e.g. MH12AB1234 (standard), "
        "DL01A1234, or 22BH1234AA (Bharat Series)."
    )
