# Importa la clase base de comandos desde el mismo paquete
from .base import BaseComando

# Comando que permite realizar búsquedas en Google mediante voz
class ComandoGoogle(BaseComando):
    def activar(self, comando):
        # Activa este comando si el texto incluye "buscar en google"
        return "buscar en google" in comando

    def ejecutar(self, comando):
        try:
            # Extrae el término de búsqueda eliminando la frase de activación
            query = comando.replace("buscar en google", "").strip()

            # Si no se especificó qué buscar, pregunta al usuario
            if not query:
                self.voz.hablar("¿Qué deseas buscar en Google?")
                query = self.voz.escuchar_con_reintentos()
            
            # Verifica si el usuario canceló
            if not query or self._es_cancelacion(query):
                self.voz.hablar("Búsqueda cancelada.")
                return

            # Realiza la búsqueda usando el servicio
            self.servicios['buscador'].buscar_en_google(query)
            self.voz.hablar(f"Buscando {query} en Google.")
        except Exception as e:
            self.voz.hablar("Ocurrió un error al realizar la búsqueda.")
            print(f"[ERROR en ComandoGoogle]: {e}")

    def _es_cancelacion(self, texto):
        texto = texto.strip().lower()
        return texto in ["cancelar", "salir", "terminar", "no", "nada", "ninguno", "adiós"]
