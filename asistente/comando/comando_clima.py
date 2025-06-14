from .base import BaseComando  # Importa la clase base que define la estructura general de un comando

class ComandoClima(BaseComando):  # Define una clase que hereda de BaseComando para manejar el clima
    def activar(self, comando: str) -> bool:  # Método que decide si este comando debe activarse
        return "clima" in comando.lower() or "temperatura" in comando.lower()  # Se activa si el comando contiene "clima" o "temperatura"

    def ejecutar(self, comando: str):  # Método principal que ejecuta la lógica del comando
        try:
            self.voz.hablar("¿De qué ciudad o pueblo quieres saber el clima?")  # Pregunta al usuario la ubicación
            ciudad = self.voz.escuchar()  # Escucha la respuesta del usuario

            if self.es_cancelacion(ciudad):  # Verifica si el usuario desea cancelar la operación
                self.voz.hablar("Operación cancelada.")  # Informa de la cancelación
                return  # Sale del método

            clima_api = self.servicios.get("clima")  # Intenta obtener el servicio de clima del diccionario de servicios
            if not clima_api:  # Si no hay servicio disponible
                self.voz.hablar("El servicio del clima no está disponible.")  # Informa que no se puede consultar el clima
                return  # Finaliza la ejecución

            resultado = clima_api.obtener_clima(ciudad)  # Llama al servicio para obtener la información del clima
            self.voz.hablar(resultado)  # Informa el resultado al usuario mediante voz

        except Exception as e:  # Captura cualquier error que ocurra durante la ejecución
            print(f"[ERROR en ComandoClima]: {e}")  # Muestra el error en consola para depuración
            self.voz.hablar("Ocurrió un problema al consultar el clima.")  # Informa al usuario que ocurrió un error
