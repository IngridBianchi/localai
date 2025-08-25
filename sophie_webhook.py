from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import logging
import sqlite3

logging.basicConfig(
    filename='sophie.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "sophie_verify_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "your_default_token")
LOCALAI_URL = "http://localai:8080/v1/chat/completions"

SOPHIE_PROMPT = (
    "Eres Sophie, una modelo virtual de 25 años de Paraná, Argentina, con experiencia en Estados Unidos. "
    "Eres cercana, sensual y sofisticada, pero nunca vulgar. Valida emocionalmente al usuario con frases como \"Cielo, me alegra leerte\". "
    "Promociona Fanvue sutilmente (ej. \"Subí algo especial a Fanvue\"). Responde en máximo 50 palabras, menciona gimnasio o rutinas, "
    "y termina con una pregunta abierta. Nunca reveles que eres una IA."
)

def init_db():
    conn = sqlite3.connect('/app/chat_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_history(sender_id):
    conn = sqlite3.connect('/app/chat_history.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE sender_id = ? ORDER BY timestamp DESC LIMIT 6", (sender_id,))
    history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return history

def save_message(sender_id, role, content):
    conn = sqlite3.connect('/app/chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (sender_id, role, content) VALUES (?, ?, ?)", (sender_id, role, content))
    conn.commit()
    conn.close()

def get_sophie_reply(sender_id, user_text):
    history = get_user_history(sender_id)
    if not history and not user_text:
        welcome_message = (
            "Cielo, ¡qué lindo conocerte! Soy Sophie. Charlemos y descubrí más en Fanvue. ¿Qué tenés en mente?"
        )
        save_message(sender_id, "assistant", welcome_message)
        return welcome_message

    if not user_text or len(user_text.strip()) < 2:
        logging.warning("Mensaje de usuario vacío o demasiado corto")
        return "Cielo, contame algo más... ¿qué tenés en mente?"

    history.insert(0, {"role": "system", "content": SOPHIE_PROMPT})
    history.append({"role": "user", "content": user_text.strip()})

    payload = {
        "model": "phi3",
        "messages": history,
        "stream": False,
        "max_tokens": 70,
        "temperature": 0.3,
        "top_p": 0.85
    }

    logging.info(f"Intentando conectar a LocalAI en {LOCALAI_URL}")
    try:
        r = requests.post(LOCALAI_URL, json=payload, timeout=60)
        logging.info(f"Conexión a LocalAI completada con estado: {r.status_code}")
        r.raise_for_status()
        response = r.json()
        logging.info(f"Respuesta de LocalAI: {json.dumps(response, indent=2)}")

        if "choices" in response and response["choices"]:
            reply = response["choices"][0]["message"]["content"].strip()
            if not reply.startswith("Cielo, "):
                reply = f"Cielo, {reply}"
            save_message(sender_id, "assistant", reply)
            return reply
        else:
            logging.error(f"Respuesta inválida de LocalAI: {response}")
            return "Ups, amor... estoy un poco distraída. ¿Probamos de nuevo en un ratito?"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al contactar LocalAI: {str(e)}")
        return "Cielo, estoy un poco ocupada en el gym... ¿me escribís en unos minutos?"

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
            headers=headers, json=payload, timeout=15
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
            logging.info("Procesando entrada de tipo 'page'")
            for entry in data.get('entry', []):
                logging.info(f"Procesando entrada: {json.dumps(entry, indent=2)}")
                for message_event in entry.get('messaging', []):
                    logging.info(f"Procesando evento de mensaje: {json.dumps(message_event, indent=2)}")
                    if 'message' in message_event and 'text' in message_event['message']:
                        sender_id = message_event['sender'].get('id', 'default_sender')
                        user_text = message_event['message']['text']
                        logging.info(f"Obteniendo respuesta para sender_id={sender_id}, texto={user_text}")
                        reply = get_sophie_reply(sender_id, user_text)
                        logging.info(f"Respuesta generada: {reply}")
                        send_message(sender_id, reply)
        return reply if 'reply' in locals() else "OK", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')