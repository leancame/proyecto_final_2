from .base import BaseComando

class ComandoWikipedia(BaseComando):
    def activar(self, comando):
        return "buscar en wikipedia" in comando.lower()

    def ejecutar(self, comando):
        try:
            # Elimina la parte del comando que activa esta acción
            query = comando.replace("buscar en wikipedia", "").strip()

            # Si no hay consulta, pregunta al usuario
            if not query:
                self.voz.hablar("¿Qué deseas buscar en Wikipedia?")
                query = self.voz.escuchar_con_reintentos()  # Mejor con reintentos

            # Cancelación
            if self._es_cancelacion(query):
                self.voz.hablar("Operación cancelada.")
                return

            # Si aún hay texto de búsqueda, proceder
            if query:
                resultado = self.servicios['buscador'].buscar_en_wikipedia(query)
                if resultado:
                    self.voz.hablar(f"En Wikipedia, {resultado}")
                else:
                    self.voz.hablar("No encontré información relevante en Wikipedia.")
            else:
                self.voz.hablar("No entendí qué buscar en Wikipedia.")
        except Exception as e:
            self.voz.hablar("Ocurrió un error al buscar en Wikipedia.")
            print(f"[ERROR en ComandoWikipedia]: {e}")

    def _es_cancelacion(self, texto):
        texto = texto.strip().lower()
        return texto in ["cancelar", "salir", "detener", "parar", "terminar", "nada", "ninguna"]
