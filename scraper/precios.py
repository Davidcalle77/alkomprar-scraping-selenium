import re

def a_numero(texto):
    """Convierte '$1.079.050' en 1079050."""
    solo = re.sub(r"[^0-9]", "", texto or "")
    return int(solo) if solo else None
