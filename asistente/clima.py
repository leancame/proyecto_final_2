import requests

class Clima:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather?"

    def obtener_clima(self, ciudad):
        complete_url = f"{self.base_url}q={ciudad}&appid={self.api_key}&units=metric"
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404":
            main_data = data["main"]
            temperatura = main_data["temp"]
            descripcion = data["weather"][0]["description"]
            return f"La temperatura en {ciudad} es de {temperatura}°C con {descripcion}."
        else:
            return "Ciudad no encontrada."
