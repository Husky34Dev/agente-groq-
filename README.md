# agente-groq-

Agente conversacional multi-agente basado en Groq API, con orquestador, agentes especializados y herramientas integradas vía backend.

## Estructura del proyecto

- `agent/`
  - `agent.py`: Punto de entrada, inicialización y wiring del sistema.
  - `orchestrator.py`: Orquestador principal, gestiona el flujo, routing y delegación entre agentes.
  - `agents/`: Clases base y especializaciones de agentes (`agent_base.py`).
  - `tools/`: Utilidades y helpers como extracción de entidades (`entidades.py`) y gestión de contexto (`context_manager.py`).
  - `tools_schema.json`: Definición de herramientas disponibles para los agentes.
- `backend/`: Backend para la ejecución de herramientas vía API REST.
- `config/`: Configuración de agentes, patrones de entidades, referencias, etc.
- `frontend/`: (Opcional) Interfaz web.
- `logs/`: Logs de depuración y ejecución.

## Instalación
1. Clona el repositorio
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura tus variables en `.env` o en `config/config.py` según corresponda.

## Uso

1. Levanta el backend de herramientas:
   ```bash
   python backend/server.py
   ```
2. Levanta el agente conversacional:
   ```bash
   python agent_server.py
   ```

Esto pondrá en marcha tanto el backend de herramientas como el orquestador multi-agente para recibir y procesar consultas.

## Flujo de trabajo
1. El usuario envía una consulta.
2. El orquestador pregunta al `router_agent` qué agente debe responder.
3. Se extraen entidades y referencias relevantes.
4. El orquestador delega la consulta al agente especializado.
5. El agente puede invocar herramientas vía backend si es necesario.
6. Se devuelve la respuesta final al usuario.

## Notas
- No subas archivos `.env`, logs, ni bases de datos locales.
- Consulta `.gitignore` para detalles.
- El sistema es modular y fácilmente extensible: puedes añadir nuevos agentes o herramientas editando los archivos de configuración y el backend.
