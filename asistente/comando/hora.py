# Importa la clase base que deben seguir todos los comandos
from .base import BaseComando
# Importa datetime para obtener la hora actual
from datetime import datetime

# Comando para informar la hora actual
class ComandoHora(BaseComando):
    def activar(self, comando):
        # Activa el comando si la palabra "hora" está presente en el texto
        return "hora" in comando

    def ejecutar(self, comando):
        # Obtiene la hora actual en formato HH:MM
        hora_actual = datetime.now().strftime("%H:%M")
        # Informa la hora al usuario mediante voz
        self.voz.hablar(f"La hora actual es {hora_actual}")
