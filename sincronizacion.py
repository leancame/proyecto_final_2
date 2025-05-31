# sincronizador_labial.py

from kivy.clock import Clock

class SincronizadorLabial:
    def __init__(self, app):
        self.app = app
        self.anim_event = None
        self.frame_index = 0

    def iniciar(self, texto):
        self.frame_index = 0
        duracion = max(2.0, len(texto.split()) * 0.4)

        def animar(dt):
            if not self.app.frames:
                return
            self.app.animacion.texture = self.app.frames[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.app.frames)

        self.anim_event = Clock.schedule_interval(animar, 0.1)
        Clock.schedule_once(lambda dt: self.detener(), duracion)

    def detener(self):
        if self.anim_event:
            self.anim_event.cancel()
            self.anim_event = None
        if self.app.frames:
            self.app.animacion.texture = self.app.frames[0]
