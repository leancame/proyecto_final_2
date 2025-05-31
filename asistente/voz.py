# voz.py
import pyttsx3
import speech_recognition as sr
import threading
import time
from kivy.clock import Clock

class VozSincronizada:
    def __init__(self, animador=None, imagen_widget=None, frames=None):
        self.reconocedor = sr.Recognizer()
        self.motor_voz = pyttsx3.init()
        self.animador = animador
        self.imagen = imagen_widget
        self.frames = frames or []
        self.frame_index = 0
        self.animacion_event = None
        self._mostrar_mensaje = print

    def set_mensaje_callback(self, callback):
        self._mostrar_mensaje = callback

    def hablar(self, texto):
        self._mostrar_mensaje(f"Asistente: {texto}")

        evento_termino = threading.Event()

        def iniciar_animacion():
            if self.animador and not self.animacion_event:
                self.frame_index = 0
                self.animacion_event = Clock.schedule_interval(self.animador, 0.1)

        def detener_animacion(dt=None):
            if self.animacion_event:
                self.animacion_event.cancel()
                self.animacion_event = None
            if self.imagen and self.frames:
                self.imagen.texture = self.frames[0]
            evento_termino.set()

        Clock.schedule_once(lambda dt: iniciar_animacion())

        def reproducir():
            self.motor_voz.say(texto)
            self.motor_voz.runAndWait()
            time.sleep(0.2)
            Clock.schedule_once(detener_animacion)

        threading.Thread(target=reproducir).start()
        evento_termino.wait()

    def escuchar(self):
        with sr.Microphone() as source:
            print("🎙️ Escuchando...")
            self.reconocedor.adjust_for_ambient_noise(source)
            audio = self.reconocedor.listen(source)

        try:
            texto = self.reconocedor.recognize_google(audio, language="es-ES")
            print(f"🗣️ Entendido: {texto}")
            return texto.lower()
        except sr.UnknownValueError:
            print("No se entendió.")
        except sr.RequestError:
            print("Error en servicio de voz.")
        return None

    def escuchar_con_reintentos(self, intentos=2):
        for _ in range(intentos):
            texto = self.escuchar()
            if texto:
                return texto
        return None
