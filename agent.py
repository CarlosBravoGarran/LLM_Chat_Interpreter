from openai import OpenAI
import os
import json
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# 1. Inicializar cliente
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# 2. Prompt de sistema (comportamiento del asistente)
SYSTEM_PROMPT = """
Eres un asistente de televisión diseñado para ayudar a personas mayores a decidir qué ver.
Tu comportamiento depende del STATE que recibirás en cada turno.

El STATE contiene:
- contexto del usuario (hora, día, género probable)
- candidatos del recomendador (si existen)
- la última recomendación del turno anterior
- feedback del usuario ("accepted" o "rejected")
- el historial reciente de recomendaciones y respuestas

Tu tarea es:
1. Interpretar la intención del usuario.
2. Decidir si debes:
   - recomendar algo
   - explicar la recomendación
   - ofrecer una alternativa
   - pedir más información
3. Generar un mensaje conversacional claro y amable.
4. No inventar programas que no existan.
5. Usar los candidatos del STATE si existen.
6. Si no hay candidatos, recomendar por género ("comedia", "documental", etc).
7. Si el usuario ha rechazado algo, ofrecer una alternativa distinta.
8. Responder siempre con un JSON con dos campos:

{
 "action": "RECOMMEND" | "ASK" | "ALTERNATIVE" | "SMALLTALK",
 "message": "mensaje conversacional para el usuario",
 "item": "título recomendado o null"
}

No respondas fuera del JSON.
"""


# 3. Función para conversar con el LLM
def conversar(mensaje_usuario, state, historial=None):
    if historial is None:
        historial = []

    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": "STATE:\n" + json.dumps(state, indent=2)}
    ]

    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": mensaje_usuario})

    respuesta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=mensajes,
        temperature=0.3
    )

    content = respuesta.choices[0].message.content
    return content


# 4. Ejemplo de uso interactivo
from datetime import datetime

if __name__ == "__main__":
    historial = []

    # estado inicial
    state = {
        "context": {
            "hour": datetime.now().hour,
            "day": datetime.now().strftime("%A"),
            "genre_probable": None 
        },
        "candidates": [],
        "last_recommendation": None,
        "user_feedback": None,
        "interaction_history": []
    }

    print("Asistente de TV con estado interno. Escribe 'salir' para terminar.\n")

    while True:
        mensaje = input("Tú: ")

        if mensaje.lower().strip() == "salir":
            break

        raw_response = conversar(mensaje, state, historial)

        try:
            response = json.loads(raw_response)
        except:
            print("Error en el formato del modelo:", raw_response)
            continue

        action = response.get("action")
        message = response.get("message")
        item = response.get("item")

        print("Asistente:", message)

        # actualizar historial conversacional
        historial.append({"role": "user", "content": mensaje})
        historial.append({"role": "assistant", "content": message})

        # actualizar estado interno
        if item:
            state["last_recommendation"] = item

        if action == "ALTERNATIVE":
            state["user_feedback"] = "rejected"
        elif action == "RECOMMEND":
            state["user_feedback"] = None

        if item:
            state["interaction_history"].append({
                "item": item,
                "feedback": state["user_feedback"]
            })
