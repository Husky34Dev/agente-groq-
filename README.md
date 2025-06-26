# agente-groq-

Agente conversacional basado en Groq API, con integración de herramientas y backend propio.

## Estructura del proyecto
- `agent.py`, `main.py`: scripts principales
- `agent/`, `backend/`, `config/`: módulos internos
- `.gitignore`: ignora archivos sensibles y temporales

## Instalación
1. Clona el repositorio
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura tus variables en `.env`

## Uso
Ejecuta el agente con:
```bash
python main.py
```

## Notas
- No subas archivos `.env`, logs, ni bases de datos locales.
- Consulta `.gitignore` para detalles.
