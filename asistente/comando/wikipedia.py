# Importa la clase base que deben seguir todos los comandos
from .base import BaseComando

# Comando para buscar información en Wikipedia
class ComandoWikipedia(BaseComando):
    def activar(self, comando):
        # Activa el comando si se menciona "buscar en wikipedia" en el comando
        return "buscar en wikipedia" in comando

    def ejecutar(self, comando):
        # Elimina la parte "buscar en wikipedia" del comando y extrae la consulta de búsqueda
        query = comando.replace("buscar en wikipedia", "").strip()
        
        # Si no se proporciona una consulta, pregunta al usuario qué buscar
        if not query:
            self.voz.hablar("¿Qué deseas buscar en Wikipedia?")
            query = self.voz.escuchar()  # Escucha la respuesta del usuario

        if query:
            # Llama al servicio de búsqueda en Wikipedia, pasando la consulta
            resultado = self.servicios['buscador'].buscar_en_wikipedia(query)
            # Informa al usuario sobre el resultado de la búsqueda
            self.voz.hablar(f"En Wikipedia, {resultado}")
