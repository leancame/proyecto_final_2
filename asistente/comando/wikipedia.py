# Importa la clase base para los comandos personalizados
from .base import BaseComando

# Define una clase que hereda de BaseComando, para buscar información en Wikipedia
class ComandoWikipedia(BaseComando):
    
    # Método para verificar si el comando del usuario activa este comando
    def activar(self, comando):
        # Devuelve True si el comando contiene la frase clave "buscar en wikipedia"
        return "buscar en wikipedia" in comando.lower()

    # Método que ejecuta el flujo del comando si fue activado
    def ejecutar(self, comando):
        try:
            # Elimina la parte del comando que activa la búsqueda, dejando solo el texto a buscar
            query = comando.replace("buscar en wikipedia", "").strip()

            # Si el usuario no especificó qué buscar, se le pregunta por voz
            if not query:
                self.voz.hablar("¿Qué deseas buscar en Wikipedia?")
                # Se intenta obtener una respuesta mediante voz, con reintentos en caso de fallo
                query = self.voz.escuchar_con_reintentos()

            # Verifica si la entrada del usuario es una orden de cancelación
            if self._es_cancelacion(query):
                # Informa al usuario que la operación ha sido cancelada
                self.voz.hablar("Operación cancelada.")
                return

            # Si hay un texto válido para buscar
            if query:
                # Utiliza el servicio de búsqueda para obtener información de Wikipedia
                resultado = self.servicios['buscador'].buscar_en_wikipedia(query)
                # Si se encontró un resultado, lo comunica al usuario
                if resultado:
                    self.voz.hablar(f"En Wikipedia, {resultado}")
                else:
                    # Si no hay resultados, informa que no encontró nada relevante
                    self.voz.hablar("No encontré información relevante en Wikipedia.")
            else:
                # Si no hay texto válido, informa que no entendió la solicitud
                self.voz.hablar("No entendí qué buscar en Wikipedia.")

        # Captura cualquier excepción que ocurra durante la ejecución
        except Exception as e:
            # Informa al usuario del error y lo imprime en consola para depuración
            self.voz.hablar("Ocurrió un error al buscar en Wikipedia.")
            print(f"[ERROR en ComandoWikipedia]: {e}")

    # Método privado para verificar si el texto del usuario corresponde a una orden de cancelación
    def _es_cancelacion(self, texto):
        # Limpia y convierte el texto a minúsculas
        texto = texto.strip().lower()
        # Compara con un conjunto de palabras clave asociadas a cancelar
        return texto in ["cancelar", "salir", "detener", "parar", "terminar", "nada", "ninguna"]
