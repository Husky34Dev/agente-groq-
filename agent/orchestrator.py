import logging
import json
from groq import Groq
from config.config import GROQ_API_KEY, GROQ_MODEL, ROUTING_MODEL, SERVER_URL
from agent.agents.agent_base import AgentBase
from agent.tools.context_manager import ContextManager

class Orchestrator:
    def __init__(self, agents, router_agent, tools_schema, context_manager):
        self.agents = agents
        self.router_agent = router_agent
        self.tools_schema = tools_schema
        self.context_manager = context_manager
        self.context = {}
        self.client = Groq(api_key=GROQ_API_KEY)

    def route(self, user_input, entidades, agent_name=None):
        if agent_name:
            agent = next((a for a in self.agents if a.name == agent_name), None)
            if agent:
                return agent.handle(user_input, entidades, self.context, self.tools_schema)
            else:
                raise Exception(f"Agente '{agent_name}' no encontrado")
        for agent in self.agents:
            for tool in getattr(agent, 'tools', []):
                if tool.replace('_', ' ') in user_input.lower():
                    return agent.handle(user_input, entidades, self.context, self.tools_schema)
        return self.agents[0].handle(user_input, entidades, self.context, self.tools_schema)

    def responder(self, user_input: str) -> dict:
        router_prompt = f"Usuario: {user_input}\nRespuesta:"
        resp = self.client.chat.completions.create(
            model=ROUTING_MODEL,
            messages=[
                {"role": "system", "content": self.router_agent.system_prompt},
                {"role": "user", "content": router_prompt}
            ],
            max_completion_tokens=10
        )
        agent_name = resp.choices[0].message.content.strip() # type: ignore
        logging.debug(f"[router_agent] Seleccionado: {agent_name}")
        if agent_name in [a.name for a in self.agents]:
            entidades = self.context_manager.extract_and_update(user_input)
            for entidad in self.context_manager.patterns.keys():
                if entidad not in entidades:
                    referencia = self.context_manager.resolve_reference(user_input)
                    if entidad in referencia:
                        entidades[entidad] = referencia[entidad]
            logging.debug(f"Entidades extraídas: {entidades}")
            try:
                respuesta = self.route(user_input, entidades, agent_name=agent_name)
            except Exception as e:
                logging.exception("Error en la coordinación de agentes")
                return {"type": "error", "error": str(e)}
            return respuesta
        else:
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un asistente general útil."},
                    {"role": "user", "content": user_input}
                ]
            )
            return {"type": "chat", "response": resp.choices[0].message.content}
