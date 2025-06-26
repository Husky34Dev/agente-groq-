import json
import re
from pathlib import Path

class ContextManager:
    def __init__(self, patterns_path, reference_map=None):
        self.patterns = self._load_patterns(patterns_path)
        self.context = {}
        self.reference_map = reference_map or {}

    def _load_patterns(self, path):
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
        """Resuelve referencias como 'este abonado' usando el contexto."""
        for ref, entity in self.reference_map.items():
            if ref in text.lower() and entity in self.context:
                return {entity: self.context[entity]}
        return {}

    def get_context(self):
        return self.context.copy()

    def clear_context(self):
        self.context.clear()

# Ejemplo de uso:
# patterns_path = 'config/entity_patterns.json'
# reference_map = {'este abonado': 'dni', 'su dirección': 'direccion'}
# cm = ContextManager(patterns_path, reference_map)
# cm.extract_and_update('facturas dni 12345678A')
# cm.resolve_reference('todos los datos de este abonado')
