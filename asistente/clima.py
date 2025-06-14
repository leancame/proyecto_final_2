import requests  # Importa la librería para hacer peticiones HTTP

class Clima:
    def __init__(self, api_key):
        self.api_key = api_key  # Guarda la clave API para la consulta del clima
        self.base_url = "https://my.meteoblue.com/packages/basic-1h"  # URL base de la API de meteoblue

    def obtener_coordenadas(self, ciudad):
        try:
            # Construye la URL para consultar las coordenadas de la ciudad con Nominatim (OpenStreetMap)
            url = f"https://nominatim.openstreetmap.org/search?q={ciudad}&format=json&limit=1"
            headers = {
                # User-Agent requerido por Nominatim para identificar la app que realiza la consulta
                "User-Agent": "TuAppPython/1.0 (tucorreo@example.com)"  # Cambiar con datos reales
            }
            respuesta = requests.get(url, headers=headers)  # Realiza la petición GET

            if respuesta.status_code != 200:
                print(f"[ERROR HTTP]: Código {respuesta.status_code}")  # Muestra error HTTP si no es 200
                return None  # Retorna None en caso de error

            datos = respuesta.json()  # Convierte la respuesta a JSON

            if datos:
                # Si hay datos, extrae latitud y longitud del primer resultado
                latitud = datos[0]["lat"]
                longitud = datos[0]["lon"]
                return latitud, longitud  # Devuelve las coordenadas
            else:
                print("[INFO]: No se encontraron coordenadas para la ciudad.")  # Info si no hay resultados
                return None  # Retorna None si no encontró coordenadas

        except Exception as e:
            print(f"[ERROR obtener_coordenadas]: {e}")  # Captura e imprime errores inesperados
            return None  # Retorna None en caso de excepción

    def obtener_clima(self, ciudad):
        coords = self.obtener_coordenadas(ciudad)  # Obtiene coordenadas para la ciudad dada
        if not coords:
            return "No pude encontrar la ubicación de esa ciudad."  # Mensaje si no se encuentran coords

        lat, lon = coords  # Desempaqueta latitud y longitud
        params = {
            "apikey": self.api_key,  # Clave API para autenticación
            "lat": lat,  # Latitud de la ubicación
            "lon": lon,  # Longitud de la ubicación
            "format": "json"  # Formato de respuesta JSON
        }

        try:
            response = requests.get(self.base_url, params=params)  # Realiza la petición GET a meteoblue
            data = response.json()  # Convierte la respuesta a JSON

            # Inicializa temperatura como None (por si no existe en datos)
            temperatura = None
            if "data_1h" in data and "temperature" in data["data_1h"]:
                temperatura = data["data_1h"]["temperature"][0]  # Extrae temperatura del primer dato horario

            # Inicializa probabilidad de lluvia como None
            prob_lluvia = None
            if "data_1h" in data and "precipitation_probability" in data["data_1h"]:
                prob_lluvia = data["data_1h"]["precipitation_probability"][0]  # Extrae probabilidad de lluvia

            # Extrae descripción del modelo meteorológico (opcional)
            descripcion = data.get("metadata", {}).get("modelrun_info", {}).get("text", "sin descripción")

            if temperatura is None:
                return f"No se pudo obtener la temperatura actual para {ciudad}."  # Mensaje si no hay temperatura

            if prob_lluvia is None:
                prob_lluvia = "desconocida"  # Si no hay probabilidad, pone valor desconocido

            # Retorna el resumen del clima con temperatura y probabilidad de lluvia
            return (f"Clima en {ciudad}:\n"
                    f"Temperatura: {temperatura}°C\n"
                    f"Probabilidad de lluvia: {prob_lluvia}%")

        except Exception as e:
            print(f"[ERROR obtener_clima]: {e}")  # Captura e imprime cualquier error durante la consulta
            return "Hubo un error al consultar el clima."  # Mensaje de error al usuario

