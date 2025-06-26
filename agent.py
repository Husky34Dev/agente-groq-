import logging
import json
import requests
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SERVER_URL
from backend.entidades import extract_entities

logging.basicConfig(filename="agent_debug.log", level=logging.DEBUG)

client = Groq(api_key=GROQ_API_KEY)

# Cargar tools desde archivo local
with open("tools_schema.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

def responder(user_input: str) -> dict:
    entidades = extract_entities(user_input)
    logging.debug(f"Entidades extraídas: {entidades}")

    messages = []
    if entidades:
        messages.append({
            "role": "system",
            "content": f"Entidades detectadas: {json.dumps(entidades)}"
        })
    messages.append({"role": "user", "content": user_input})

    def enviar(tool_choice="auto"):
        logging.debug(f"Llamando al modelo con tool_choice={tool_choice}")
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            max_completion_tokens=1024
        )
        logging.debug(f"Respuesta cruda del modelo: {resp!r}")
        return resp

    # 1) Intento normal
    resp = enviar("auto")
    msg = resp.choices[0].message

    # 2) Forzar si no invocó
    if not getattr(msg, "tool_calls", None):
        logging.warning("No se detectó tool_call → reintentando required")
        resp = enviar("required")
        msg = resp.choices[0].message

    # 3) Si aún no hay tool_calls → chat plano
    if not getattr(msg, "tool_calls", None):
        return {"type": "chat", "response": msg.content}

    resultados = []
    # 4) Para cada llamada a herramienta
    for call in msg.tool_calls:
        name = call.function.name
        # parsear args JSON
        try:
            args = json.loads(call.function.arguments)
        except:
            logging.exception("Error parseando arguments")
            resultados.append({"tool": name, "error": "args invalidos"})
            continue

        # Buscar el esquema de la herramienta correspondiente
        tool_schema = next((t for t in tools if t["function"]["name"] == name), None)
        reqs = tool_schema["function"]["parameters"].get("required", []) if tool_schema else []
        for r in reqs:
            if r not in args and r in entidades:
                args[r] = entidades[r]

        logging.info(f"Ejecutando herramienta {name} con args {args}")
        try:
            r = requests.post(f"{SERVER_URL}/{name}", json=args)
            r.raise_for_status()
            out = r.json()
        except:
            logging.exception("Error al llamar al backend")
            resultados.append({"tool": name, "error": "backend failure"})
            continue

        # añadir al diálogo
        messages.append({"role": "assistant", "tool_calls": [call]})
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(out)
        })
        resultados.append({"tool": name, "params": args, "response": out})

    return {"type": "tool_calls", "raw_input": user_input, "results": resultados}
