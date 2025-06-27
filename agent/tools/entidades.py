import json
import os
import re

# Cargar patrones de entidades
with open(os.path.join(os.path.dirname(__file__), "../../config/entity_patterns.json"), encoding="utf-8") as f:
    entity_patterns = json.load(f)

def extract_entities(text: str) -> dict:
    """
    Extrae entidades según patrones. Devuelve dict, p.ej. {"dni": "12345678A"}
    """
    encontrados = {}
    for nombre, patron in entity_patterns.items():
        m = re.search(patron, text)
        if m:
            encontrados[nombre] = m.group()
    return encontrados
