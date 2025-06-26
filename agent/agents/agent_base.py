import logging
import json
import requests
from groq import Groq
from config.config import GROQ_API_KEY, GROQ_MODEL, SERVER_URL

class AgentBase:
    def __init__(self, name, system_prompt, specialization, tools):
        self.name = name
        self.system_prompt = system_prompt
        self.specialization = specialization
        self.tools = tools
        self.client = Groq(api_key=GROQ_API_KEY)

    def handle(self, user_input, entidades, context, tools_schema=None):
        """
        user_input: str
        entidades: dict (entidades extraídas y resueltas)
        context: dict (contexto compartido entre agentes)
        tools_schema: lista de tools (opcional, si no se pasa, usa self.tools)
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
            for call in msg.tool_calls:
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
        return {"type": "chat", "agent": self.name, "response": msg.content}
