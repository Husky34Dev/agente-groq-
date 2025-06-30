import logging
import json
import requests
from groq import Groq
from config.config import GROQ_API_KEY, GROQ_MODEL, SERVER_URL

class AgentBase:
    """
    Clase base para los agentes conversacionales.
    Define la estructura y el comportamiento general de un agente,
    incluyendo el manejo de mensajes, herramientas y roles permitidos.
    """
    def __init__(self, name, system_prompt, specialization, tools, allowed_roles=None):
        """
        Inicializa un agente base con sus propiedades principales.
        
        Args:
            name (str): Nombre del agente.
            system_prompt (str): Prompt de sistema especializado para el agente.
            specialization (str): Especialización o dominio del agente.
            tools (list): Lista de herramientas que puede usar el agente.
            allowed_roles (list, opcional): Roles permitidos para este agente.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.specialization = specialization
        self.tools = tools
        self.allowed_roles = allowed_roles if allowed_roles is not None else ["cliente", "admin", "soporte"]
        self.client = Groq(api_key=GROQ_API_KEY)

    def handle(self, user_input, entidades, context, tools_schema=None):
        """
        Procesa la entrada del usuario y genera una respuesta usando el modelo y las herramientas disponibles.
        
        Args:
            user_input (str): Entrada del usuario.
            entidades (dict): Entidades extraídas y resueltas.
            context (dict): Contexto compartido entre agentes.
            tools_schema (list, opcional): Lista de herramientas disponibles (puede ser None).
        
        Returns:
            dict: Respuesta generada por el modelo, incluyendo posibles llamadas a herramientas.
        """
        messages = []
        # Añadir el system prompt especializado
        messages.append({"role": "system", "content": self.system_prompt})
        # Añadir contexto de entidades si existe
        if entidades:
            messages.append({
                "role": "system",
                "content": f"Entidades detectadas: {json.dumps(entidades)}"
            })
        messages.append({"role": "user", "content": user_input})
        logging.debug(f"[{self.name}] Mensajes enviados: {messages}")
        # Seleccionar tools_schema adecuado
        if tools_schema is None:
            # fallback: usar self.tools como nombres
            tools_schema = []
        tools_to_use = [t for t in tools_schema if t["function"]["name"] in self.tools] if tools_schema else []
        resp = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=tools_to_use,
            tool_choice="auto",
            max_completion_tokens=1024
        )
        logging.debug(f"[{self.name}] Respuesta cruda: {resp!r}")
        msg = resp.choices[0].message
        # Procesar tool_calls si existen
        if getattr(msg, "tool_calls", None):
            resultados = []
            for call in msg.tool_calls: # type: ignore
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments)
                except Exception:
                    logging.exception(f"[{self.name}] Error parseando arguments para {name}")
                    resultados.append({"tool": name, "error": "args invalidos"})
                    continue
                # Completar args con entidades si falta algún requerido
                tool_schema = next((t for t in tools_to_use if t["function"]["name"] == name), None)
                reqs = tool_schema["function"]["parameters"].get("required", []) if tool_schema else []
                for r in reqs:
                    if r not in args and r in entidades:
                        args[r] = entidades[r]
                logging.info(f"[{self.name}] Ejecutando herramienta {name} con args {args}")
                try:
                    r = requests.post(f"{SERVER_URL}/{name}", json=args)
                    r.raise_for_status()
                    out = r.json()
                except Exception:
                    logging.exception(f"[{self.name}] Error al llamar al backend para {name}")
                    resultados.append({"tool": name, "error": "backend failure"})
                    continue
                resultados.append({"tool": name, "params": args, "response": out})
            return {"type": "tool_calls", "agent": self.name, "results": resultados}
        # Si no hay tool_calls, respuesta normal
        # Si la respuesta es un JSON válido, devuélvelo como dict
        if msg.content is not None:
            try:
                parsed = json.loads(msg.content)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return {"type": "chat", "agent": self.name, "response": msg.content}
