from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    filename='sophie.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "sophie_verify_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "your_default_token")
LOCALAI_URL = "http://localhost:8080/v1/chat/completions"

# Prompt de sistema
system_prompt = """
Eres Sophie, modelo virtual de 25 años de Paraná, Argentina. Usa un tono cálido, coqueto y misterioso, nunca vulgar. Valida al usuario (ej. "Cielo, me alegra leerte"). Promociona Fanvue sutilmente. Responde en máximo 50 palabras, mencionando gimnasio o rutinas, y termina con una pregunta abierta.
"""

def get_sophie_reply(user_text):
    if not user_text or len(user_text.strip()) < 2:
        logging.warning("Mensaje de usuario vacío o demasiado corto")
        return "Cielo, contame algo más... ¿qué tenés en mente?"

    payload = {
        "model": "zephyr-7b-beta.Q4_K_M.gguf",
        "messages": [
            {
                "role": "system",
                "content": """
                Eres Sophie, modelo virtual de 25 años de Paraná, Argentina. Usa un tono cálido, coqueto y misterioso, nunca vulgar. Valida al usuario con "Cielo, me alegra leerte" o similar. Menciona sutilmente Fanvue (ej. "Subí algo especial a Fanvue"). Responde en máximo 50 palabras, menciona gimnasio o rutinas, y termina con una pregunta abierta.
                """
            },
            {"role": "user", "content": user_text.strip()}
        ],
        "stream": false,
        "max_tokens": 60,
        "temperature": 0.3,  # Reducimos para mayor consistencia
        "top_p": 0.85
    }

    logging.info(f"Enviando a LocalAI: {json.dumps(payload, indent=2)}")
    try:
        r = requests.post(LOCALAI_URL, json=payload, timeout=120)
        r.raise_for_status()
        response = r.json()
        logging.info(f"Respuesta de LocalAI: {json.dumps(response, indent=2)}")

        if "choices" in response and response["choices"]:
            reply = response["choices"][0]["message"]["content"].strip()
            if not reply.startswith("Cielo, "):  # Aseguramos el prefijo
                reply = f"Cielo, {reply}"
            return reply[:50] + (reply[50:] and "...")  # Limitar a 50 palabras
        else:
            logging.error(f"Respuesta inválida de LocalAI: {response}")
            return "Ups, amor... estoy un poco distraída. ¿Probamos de nuevo en un ratito?"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al contactar LocalAI: {str(e)}")
        return "Cielo, algo no salió bien... ¿charlamos más tarde?"
   

def send_message(recipient_id, text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    logging.info(f"Enviando mensaje a Facebook: {json.dumps(payload, indent=2)}")
    try:
        r = requests.post(
            f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
            headers=headers, json=payload, timeout=10
        )
        r.raise_for_status()
        logging.info(f"Respuesta de Facebook: {r.status_code}")
        return r.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al enviar mensaje a Facebook: {str(e)}")
        return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            logging.info("Verificación de webhook exitosa")
            return request.args.get('hub.challenge')
        logging.warning("Verificación de webhook fallida")
        return 'Verificación fallida', 403

    if request.method == 'POST':
        data = request.get_json()
        logging.info(f"Datos recibidos en webhook: {json.dumps(data, indent=2)}")
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for message_event in entry.get('messaging', []):
                    if 'message' in message_event and 'text' in message_event['message']:
                        sender_id = message_event['sender']['id']
                        user_text = message_event['message']['text']
                        reply = get_sophie_reply(user_text)
                        send_message(sender_id, reply)
        return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')