from .base import BaseComando
from datetime import datetime

class ComandoHora(BaseComando):
    def activar(self, comando):
        # Activa si el comando contiene la palabra "hora"
        return "hora" in comando.lower()

    def ejecutar(self, comando):
        try:
            # Verifica si el usuario dijo algo que indique cancelación
            if self._es_cancelacion(comando):
                self.voz.hablar("Operación cancelada.")
                return

            # Obtiene la hora actual
            hora_actual = datetime.now().strftime("%H:%M")
            self.voz.hablar(f"La hora actual es {hora_actual}")
        except Exception as e:
            self.voz.hablar("Hubo un problema al obtener la hora.")
            print(f"[ERROR en ComandoHora]: {e}")

    def _es_cancelacion(self, texto):
        texto = texto.strip().lower()
        return texto in ["cancelar", "salir", "detener", "parar", "terminar", "nada", "ninguna"]
   
class ComandoFecha(BaseComando):
    def activar(self, comando):
        # Activa si el comando contiene la palabra "fecha"
        return "fecha" in comando.lower()

    def ejecutar(self, comando):
        try:
            # Verifica si el usuario dijo algo que indique cancelación
            if self._es_cancelacion(comando):
                self.voz.hablar("Operación cancelada.")
                return

            # Obtiene la fecha actual en formato legible
            fecha_actual = datetime.now().strftime("%d de %B de %Y")
            self.voz.hablar(f"Hoy es {fecha_actual}")
        except Exception as e:
            self.voz.hablar("Hubo un problema al obtener la fecha.")
            print(f"[ERROR en ComandoFecha]: {e}")

    def _es_cancelacion(self, texto):
        texto = texto.strip().lower()
        return texto in ["cancelar", "salir", "detener", "parar", "terminar", "nada", "ninguna"]
