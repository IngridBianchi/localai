import requests
from sophie_prompt import get_sophie_prompt

class SophieBot:
    def __init__(self):
        self.url = "http://localai:8080/v1/chat/completions"
        self.model = "phi3"
        self.history = [
            {
                "role": "system",
                "content": get_sophie_prompt()
            }
        ]

    def enviar_mensaje(self, user_input):
        self.history.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": False,
            "max_tokens": 70,
            "temperature": 0.3,
            "top_p": 0.85
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            respuesta = data['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": respuesta})
            return respuesta
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return "Cielo, algo no salió bien... ¿charlamos más tarde?"