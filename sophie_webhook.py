from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import logging
import sqlite3
from sophie_prompt import get_sophie_prompt

logging.basicConfig(
    filename='sophie.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "sophie_verify_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "your_default_token")
LLAMA_SERVER_URL = "http://localhost:8080/completion"

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
    if not user_text or len(user_text.strip()) < 2:
        return "Cielo, contame algo más... ¿qué tenés en mente?"

    prompt = get_sophie_prompt(user_text.strip())

    payload = {
        "prompt": prompt,
        "n_predict": 100,
        "temperature": 0.4,
        "top_p": 0.9
    }

    try:
        r = requests.post(LLAMA_SERVER_URL, json=payload, timeout=30)
        r.raise_for_status()
        response = r.json()
        reply = response.get("content", "").strip()
        if not reply.startswith("Cielo"):
            reply = f"Cielo, {reply}"
        save_message(sender_id, "assistant", reply)
        return reply
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al contactar llama-server: {str(e)}")
        return "Cielo, estoy un poco ocupada en el gym... ¿me escribís en unos minutos?"

def send_message(recipient_id, text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(
            f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
            headers=headers, json=payload, timeout=15
        )
        r.raise_for_status()
        return r.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al enviar mensaje a Facebook: {str(e)}")
        return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verificación fallida', 403

    if request.method == 'POST':
        data = request.get_json()
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for message_event in entry.get('messaging', []):
                    if 'message' in message_event and 'text' in message_event['message']:
                        sender_id = message_event['sender'].get('id', 'default_sender')
                        user_text = message_event['message']['text']
                        reply = get_sophie_reply(sender_id, user_text)
                        send_message(sender_id, reply)
        return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
