from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent.agent import responder
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

app = FastAPI()

# Permitir CORS para desarrollo (ajusta origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(data: ChatRequest):
    try:
        result = responder(data.message)
        # El resultado puede ser dict o string, normalizamos la respuesta
        if isinstance(result, dict):
            # Si es un dict, serializar como JSON válido para el frontend
            reply = result.get("response") or result.get("respuesta") or json.dumps(result, ensure_ascii=False)
        else:
            reply = str(result)
        return {"reply": reply}
    except Exception as e:
        logging.exception("Error en el endpoint /api/chat")
        return {"reply": f"❌ Error procesando la solicitud: {str(e)}"}
