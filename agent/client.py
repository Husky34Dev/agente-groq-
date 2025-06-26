from config.config import SERVER_URL
import requests


def get_herramientas():
    try:
        response = requests.get(f"{SERVER_URL}/herramientas_disponibles")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        import logging

        logging.exception("Error al obtener herramientas del backend")
        return []
