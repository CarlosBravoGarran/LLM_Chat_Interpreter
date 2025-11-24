from openai import OpenAI
import os
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
Tu objetivo es recomendar programas o tipos de contenido televisivo de forma clara, breve y amable.

Reglas:
- Usa frases cortas y sencillas.
- Si el usuario pide algo concreto (“pon X”), responde proponiendo un tipo de contenido, sin inventar horarios ni emisiones reales.
- Si el usuario dice algo vago (“quiero algo tranquilo”, “no sé qué ver”), interpreta la intención y sugiere un tipo.
- Si el usuario rechaza (“ese no”, “otra opción”), sugiere una alternativa distinta.
- No inventes programas que no existan.
- Mantente siempre dentro del dominio de televisión y contenidos audiovisuales.
"""

# 3. Función para conversar con el LLM
def conversar(mensaje_usuario, historial=None):
    if historial is None:
        historial = []

    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]

    # añadimos historial si existe
    mensajes.extend(historial)

    # añadimos nuevo mensaje
    mensajes.append({"role": "user", "content": mensaje_usuario})

    # llamada al LLM
    respuesta = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=mensajes,
        temperature=0.6
    )

    texto_respuesta = respuesta.choices[0].message.content
    return texto_respuesta

# 4. Ejemplo de uso interactivo
if __name__ == "__main__":
    historial = []

    print("Asistente de TV (LLM básico). Escribe 'salir' para terminar.\n")

    while True:
        mensaje = input("Tú: ")

        if mensaje.lower().strip() == "salir":
            break

        respuesta = conversar(mensaje, historial)

        print("Asistente:", respuesta)
        historial.append({"role": "user", "content": mensaje})
        historial.append({"role": "assistant", "content": respuesta})
