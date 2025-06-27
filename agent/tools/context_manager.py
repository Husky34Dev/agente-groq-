import json
import re
from pathlib import Path

class ContextManager:
    def __init__(self, patterns_path, reference_map_path=None):
        self.patterns = self._load_patterns(patterns_path)
        self.context = {}
        self.reference_map = self._load_reference_map(reference_map_path) if reference_map_path else {}

    def _load_patterns(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_reference_map(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_and_update(self, text):
        """Extrae entidades usando los patrones y actualiza el contexto."""
        for entity, pattern in self.patterns.items():
            match = re.search(pattern, text)
            if match:
                self.context[entity] = match.group()
        return self.context.copy()

    def resolve_reference(self, text):
        """Resuelve referencias usando patrones regex del reference_map."""
        for ref_pattern, entity in self.reference_map.items():
            if re.search(ref_pattern, text, re.IGNORECASE) and entity in self.context:
                return {entity: self.context[entity]}
        return {}

    def get_context(self):
        return self.context.copy()

    def clear_context(self):
        self.context.clear()

# Ejemplo de uso:
# patterns_path = 'config/entity_patterns.json'
# reference_map_path = 'config/reference_map.json'
# cm = ContextManager(patterns_path, reference_map_path)
# cm.extract_and_update('facturas dni 12345678A')
# cm.resolve_reference('todos los datos de este abonado')
