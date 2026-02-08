import re

def normalize(name: str) -> str:
    """
    Normalize party names by removing common estate prefixes
    and extra whitespace, and capitalize properly.
    """
    if not name:
        return ""

    # Remove common words like DECD, ESTATE, PETITIONER, PR
    name = re.sub(r'\b(DECD|ESTATE|PETITIONER|PR)\b', '', name.upper())

    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)

    # Capitalize each word
    return name.title().strip()
