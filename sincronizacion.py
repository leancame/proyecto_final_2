# Importa Clock desde Kivy, utilizado para agendar funciones repetitivas o diferidas
from kivy.clock import Clock

# Define la clase SincronizadorLabial que se encarga de animar la "boca" sincronizada con el texto hablado
class SincronizadorLabial:
    # Constructor que recibe la instancia de la aplicación (app) que contiene los recursos gráficos
    def __init__(self, app):
        self.app = app                  # Referencia a la app que contiene los frames y la imagen
        self.anim_event = None          # Evento de animación programado por Clock
        self.frame_index = 0            # Índice actual del frame que se está mostrando

    # Método para iniciar la animación de labios basada en el texto a hablar
    def iniciar(self, texto):
        self.frame_index = 0            # Reinicia el índice de frames
        # Calcula la duración mínima de la animación: al menos 2 segundos o proporcional a la cantidad de palabras
        duracion = max(2.0, len(texto.split()) * 0.4)

        # Define la función que se ejecutará cada 0.1 segundos para cambiar el frame mostrado
        def animar(dt):
            if not self.app.frames:
                return                   # Si no hay frames, no se hace nada
            # Cambia la textura (imagen) del widget de animación a la del frame actual
            self.app.animacion.texture = self.app.frames[self.frame_index]
            # Avanza al siguiente frame circularmente
            self.frame_index = (self.frame_index + 1) % len(self.app.frames)

        # Programa la animación para que se ejecute cada 0.1 segundos
        self.anim_event = Clock.schedule_interval(animar, 0.1)
        # Programa una llamada a `detener` después del tiempo calculado
        Clock.schedule_once(lambda dt: self.detener(), duracion)

    # Método para detener la animación de labios
    def detener(self):
        if self.anim_event:
            self.anim_event.cancel()    # Cancela el evento de animación si está activo
            self.anim_event = None      # Limpia la referencia
        if self.app.frames:
            self.app.animacion.texture = self.app.frames[0]  # Restaura el primer frame (boca cerrada)
