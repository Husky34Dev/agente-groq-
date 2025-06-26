import sys
from agent.agent import responder

def main():
    print("Agente CLI. Escribe tu consulta o 'salir' para terminar.")
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break
        if user_input.lower() in ("salir", "exit", "quit"): 
            print("Adiós!")
            break
        if not user_input:
            continue
        respuesta = responder(user_input)
        print("\nRespuesta:")
        print(respuesta)

if __name__ == "__main__":
    main()
