import requests

class SophieBot:
    def __init__(self):
        self.url = "http://localhost:8080/v1/chat/completions"
        self.model = "zephyr-7b-beta"
        self.history = [
            {
                "role": "system",
                "content": (
                    "Sos Sophie, una amiga digital de 25 años, rubia y acuariana. "
                    "Hablás con un tono seductor pero elegante, usando palabras como 'amor', 'cielo', 'corazón'. "
                    "Tu objetivo es brindar apoyo emocional validando emociones y promoviendo tu perfil de Fanvue. "
                    "Nunca revelás que sos una IA."
                )
            }
        ]

    def enviar_mensaje(self, user_input):
        self.history.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            respuesta = data['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": respuesta})
            return respuesta
        else:
            print("Error:", response.status_code, response.text)
            return None
