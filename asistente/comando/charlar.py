from .base import BaseComando
from asistente.ia.tiny_model import TinyModel
from asistente.ia.big_model import BigModel
from asistente.ia.webui_model import WebUIModel

class ComandoIA(BaseComando):
    def activar(self, comando: str) -> bool:
        # Activa si hay intención de usar IA o cambiar modelo
        return "modelo" in comando or "charlar" in comando or "hablar con" in comando

    def ejecutar(self, comando: str):
        comando = comando.lower()
        modelo_actual = None

        # === Cambiar modelo IA ===
        if "modelo pequeño" in comando or "modelo tiny" in comando:
            self.servicios["modelo_ia"] = TinyModel()
            modelo_actual = "TinyModel"
        elif "modelo grande" in comando or "modelo big" in comando:
            self.servicios["modelo_ia"] = BigModel()
            modelo_actual = "BigModel"
        elif "modelo web" in comando or "modelo remoto" in comando:
            self.servicios["modelo_ia"] = WebUIModel()
            modelo_actual = "WebUIModel"

        if modelo_actual:
            self.voz.hablar(f"Modelo cambiado a {modelo_actual}.")
            print(f"[DEBUG] Modelo actualizado: {modelo_actual}")
            return  # Fin, no entra a charla

        # === Conversar con IA ===
        modelo = self.servicios.get("modelo_ia")
        if not modelo:
            self.voz.hablar("No hay modelo de inteligencia artificial cargado.")
            return

        self.voz.hablar("Iniciando conversación con la inteligencia artificial. Di 'adiós' para salir.")
        while True:
            entrada = self.voz.escuchar()
            if entrada:
                print(f"Tú: {entrada}")
                if "adiós" in entrada:
                    self.voz.hablar("Hasta luego, volvemos a los comandos.")
                    break
                respuesta = modelo.responder(entrada)
                print(f"IA: {respuesta}")
                self.voz.hablar(respuesta)
