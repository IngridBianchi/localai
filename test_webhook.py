import pytest
import requests

WEBHOOK_URL = "http://localhost:5000/webhook"

def test_webhook_message():
    payload = {
        "object": "page",
        "entry": [
            {
                "messaging": [
                    {
                        "sender": {"id": "12345"},
                        "message": {"text": "Hola, ¿cómo estás?"}
                    }
                ]
            }
        ]
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    assert response.status_code == 200
    assert response.text == "OK"