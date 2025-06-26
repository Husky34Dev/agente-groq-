import logging
import os
import json
import requests
from config.config import GROQ_API_KEY, GROQ_MODEL, SERVER_URL
from backend.entidades import extract_entities
from agent.context_manager import ContextManager
from agent.agents.agent_base import AgentBase

# Asegurar que la carpeta logs existe
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "agent_debug.log")
logging.basicConfig(filename=log_path, level=logging.DEBUG)

from groq import Groq
client = Groq(api_key=GROQ_API_KEY)

ROUTING_MODEL = "llama-3.3-70b-versatile"
GENERAL_MODEL = "llama-3.3-70b-versatile"


# Cargar tools desde archivo local
with open("agent/tools_schema.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

# Inicializar el ContextManager con los paths de los JSON
patterns_path = os.path.join(os.path.dirname(__file__), "..", "config", "entity_patterns.json")
reference_map_path = os.path.join(os.path.dirname(__file__), "..", "config", "reference_map.json")
context_manager = ContextManager(patterns_path, reference_map_path)

# Cargar agentes dinámicamente desde config/agents_config.json
agents_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "agents_config.json")
def load_agents_from_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    return [AgentBase(**cfg) for cfg in configs]
agents = load_agents_from_config(agents_config_path)

# Identificar router_agent y agentes normales
router_agent = next((a for a in agents if a.name == "router_agent"), None)
user_agents = [a for a in agents if a.name != "router_agent"]

class Coordinator:
    def __init__(self, agents, tools_schema):
        self.agents = agents
        self.tools_schema = tools_schema
        self.context = {}

    def route(self, user_input, entidades, agent_name=None):
        # Si se especifica un agente, delegar directamente
        if agent_name:
            agent = next((a for a in self.agents if a.name == agent_name), None)
            if agent:
                return agent.handle(user_input, entidades, self.context, self.tools_schema)
            else:
                raise Exception(f"Agente '{agent_name}' no encontrado")
        # ...fallback legacy...
        for agent in self.agents:
            for tool in getattr(agent, 'tools', []):
                if tool.replace('_', ' ') in user_input.lower():
                    return agent.handle(user_input, entidades, self.context, self.tools_schema)
        return self.agents[0].handle(user_input, entidades, self.context, self.tools_schema)

coordinator = Coordinator(user_agents, tools)

def responder(user_input: str) -> dict:
    # --- Routing LLM: preguntar SIEMPRE al router_agent ---
    router_prompt = f"Usuario: {user_input}\nRespuesta:"
    resp = client.chat.completions.create(
        model=ROUTING_MODEL,
        messages=[
            {"role": "system", "content": router_agent.system_prompt},
            {"role": "user", "content": router_prompt}
        ],
        max_completion_tokens=10
    )
    agent_name = resp.choices[0].message.content.strip()
    logging.debug(f"[router_agent] Seleccionado: {agent_name}")
    # Si el router_agent responde con un agente válido, delegar
    if agent_name in [a.name for a in user_agents]:
        entidades = context_manager.extract_and_update(user_input)
        for entidad in context_manager.patterns.keys():
            if entidad not in entidades:
                referencia = context_manager.resolve_reference(user_input)
                if entidad in referencia:
                    entidades[entidad] = referencia[entidad]
        logging.debug(f"Entidades extraídas: {entidades}")
        try:
            respuesta = coordinator.route(user_input, entidades, agent_name=agent_name)
        except Exception as e:
            logging.exception("Error en la coordinación de agentes")
            return {"type": "error", "error": str(e)}
        return respuesta
    # Si no, usar el modelo generalista
    else:
        resp = client.chat.completions.create(
            model=GENERAL_MODEL,
            messages=[
                {"role": "system", "content": "Eres un asistente general útil."},
                {"role": "user", "content": user_input}
            ]
        )
        return {"type": "chat", "response": resp.choices[0].message.content}
