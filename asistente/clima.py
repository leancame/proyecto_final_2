import requests

class Clima:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://my.meteoblue.com/packages/basic-1h"

    def obtener_coordenadas(self, ciudad):
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={ciudad}&format=json&limit=1"
            headers = {
                "User-Agent": "TuAppPython/1.0 (tucorreo@example.com)"  # Cambia esto por tus datos reales
            }
            respuesta = requests.get(url, headers=headers)

            if respuesta.status_code != 200:
                print(f"[ERROR HTTP]: Código {respuesta.status_code}")
                return None

            datos = respuesta.json()

            if datos:
                latitud = datos[0]["lat"]
                longitud = datos[0]["lon"]
                return latitud, longitud
            else:
                print("[INFO]: No se encontraron coordenadas para la ciudad.")
                return None

        except Exception as e:
            print(f"[ERROR obtener_coordenadas]: {e}")
            return None

    def obtener_clima(self, ciudad):
        coords = self.obtener_coordenadas(ciudad)
        if not coords:
            return "No pude encontrar la ubicación de esa ciudad."

        lat, lon = coords
        params = {
            "apikey": self.api_key,
            "lat": lat,
            "lon": lon,
            "format": "json"
        }

        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()

            # DEBUG: Muestra el JSON completo recibido (opcional, puedes comentar luego)
            # print("[DEBUG] JSON de respuesta de Meteoblue:")
            # print(data)

            # Extraer la temperatura del primer valor horario
            temperatura = None
            if "data_1h" in data and "temperature" in data["data_1h"]:
                temperatura = data["data_1h"]["temperature"][0]

            # Extraer la probabilidad de precipitación del primer valor horario
            prob_lluvia = None
            if "data_1h" in data and "precipitation_probability" in data["data_1h"]:
                prob_lluvia = data["data_1h"]["precipitation_probability"][0]

            # Texto descriptivo del modelo meteorológico (opcional)
            descripcion = data.get("metadata", {}).get("modelrun_info", {}).get("text", "sin descripción")

            if temperatura is None:
                return f"No se pudo obtener la temperatura actual para {ciudad}."

            if prob_lluvia is None:
                prob_lluvia = "desconocida"

            return (f"Clima en {ciudad}:\n"
                    f"Temperatura: {temperatura}°C\n"
                    f"Probabilidad de lluvia: {prob_lluvia}%")

        except Exception as e:
            print(f"[ERROR obtener_clima]: {e}")
            return "Hubo un error al consultar el clima."

