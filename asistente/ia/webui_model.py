import requests

class WebUIModel:
    def __init__(self, url="http://localhost:5000/api/v1/generate"):
        self.url = url

    def responder(self, mensaje):
        data = {
            "prompt": mensaje,
            "max_new_tokens": 150,
            "temperature": 0.7,
        }
        try:
            respuesta = requests.post(self.url, json=data).json()
            return respuesta.get("results", [{}])[0].get("text", "").strip()
        except Exception as e:
            return f"Error al conectar con la IA: {e}"
 