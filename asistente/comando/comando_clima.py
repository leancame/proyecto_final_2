from .base import BaseComando

class ComandoClima(BaseComando):
    def activar(self, comando: str) -> bool:
        return "clima" in comando.lower() or "temperatura" in comando.lower()

    def ejecutar(self, comando: str):
        try:
            self.voz.hablar("¿De qué ciudad o pueblo quieres saber el clima?")
            ciudad = self.voz.escuchar()

            if self.es_cancelacion(ciudad):
                self.voz.hablar("Operación cancelada.")
                return

            clima_api = self.servicios.get("clima")
            if not clima_api:
                self.voz.hablar("El servicio del clima no está disponible.")
                return

            resultado = clima_api.obtener_clima(ciudad)
            self.voz.hablar(resultado)

        except Exception as e:
            print(f"[ERROR en ComandoClima]: {e}")
            self.voz.hablar("Ocurrió un problema al consultar el clima.")
