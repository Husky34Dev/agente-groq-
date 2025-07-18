import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
ROUTING_MODEL = os.getenv("ROUTING_MODEL", "llama-3.3-70b-versatile")
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
