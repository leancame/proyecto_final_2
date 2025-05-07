# Importa la clase base de comandos desde el mismo paquete
from .base import BaseComando

# Comando que permite realizar búsquedas en Google mediante voz
class ComandoGoogle(BaseComando):
    def activar(self, comando):
        # Activa este comando si el texto incluye "buscar en google"
        return "buscar en google" in comando

    def ejecutar(self, comando):
        # Extrae el término de búsqueda eliminando la frase de activación
        query = comando.replace("buscar en google", "").strip()

        # Si no se especificó qué buscar, pregunta al usuario
        if not query:
            self.voz.hablar("¿Qué deseas buscar en Google?")
            query = self.voz.escuchar()  # Espera a que el usuario responda

        # Si finalmente tiene una consulta válida, realiza la búsqueda
        if query:
            self.servicios['buscador'].buscar_en_google(query)  # Usa el servicio de búsqueda
            self.voz.hablar(f"Buscando {query} en Google.")  # Confirma al usuario lo que está haciendo
