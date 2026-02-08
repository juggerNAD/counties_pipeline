import re

def normalize_name(raw_name: str) -> str:
    """
    Normalizes names extracted from Case.net
    - Removes excessive whitespace
    - Fixes casing
    - Removes trailing roles (DECD, PET, etc.)
    """

    if not raw_name:
        return ""

    name = raw_name.upper()

    # Remove role annotations
    name = re.sub(
        r'\b(DECD|DECEDENT|PETITIONER|FIDUCIARY|PR|ESTATE)\b',
        '',
        name
    )

    # Remove punctuation noise
    name = re.sub(r'[^\w\s\-]', '', name)

    # Normalize spaces
    name = re.sub(r'\s+', ' ', name).strip()

    # Convert to Title Case
    return name.title()
