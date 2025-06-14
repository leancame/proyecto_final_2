# voz.py
import pyttsx3  # Librería para síntesis de voz (texto a voz)
import speech_recognition as sr  # Librería para reconocimiento de voz
import threading  # Para manejo de hilos
import time  # Para funciones de tiempo (sleep)
from kivy.clock import Clock  # Para programación de eventos en Kivy (UI)

class VozSincronizada:
    def __init__(self, animador=None, imagen_widget=None, frames=None):
        self.reconocedor = sr.Recognizer()  # Inicializa el reconocedor de voz
        self.motor_voz = pyttsx3.init()  # Inicializa el motor de síntesis de voz
        self.animador = animador  # Función para animar la imagen mientras habla
        self.imagen = imagen_widget  # Widget de imagen para mostrar animación
        self.frames = frames or []  # Lista de frames para la animación (texturas)
        self.frame_index = 0  # Índice para llevar control del frame actual
        self.animacion_event = None  # Evento programado para animación
        self._mostrar_mensaje = print  # Función callback para mostrar mensajes (por defecto print)

    def set_mensaje_callback(self, callback):
        self._mostrar_mensaje = callback  # Permite establecer una función para mostrar mensajes

    def hablar(self, texto):
        self._mostrar_mensaje(f"Asistente: {texto}")  # Muestra el texto que se va a hablar

        evento_termino = threading.Event()  # Evento para esperar que termine la síntesis de voz

        def iniciar_animacion():
            # Inicia la animación si hay animador y no hay animación corriendo
            if self.animador and not self.animacion_event:
                self.frame_index = 0  # Reinicia el índice de frames
                # Programa la función animador para que corra cada 0.1 segundos en el hilo principal
                self.animacion_event = Clock.schedule_interval(self.animador, 0.1)

        def detener_animacion(dt=None):
            # Detiene la animación si está corriendo
            if self.animacion_event:
                self.animacion_event.cancel()  # Cancela el evento de animación
                self.animacion_event = None  # Limpia el evento
            # Si hay imagen y frames, pone la imagen al primer frame (estático)
            if self.imagen and self.frames:
                self.imagen.texture = self.frames[0]
            evento_termino.set()  # Señala que terminó la reproducción de voz

        Clock.schedule_once(lambda dt: iniciar_animacion())  # Programa iniciar_animacion para que se ejecute pronto

        def reproducir():
            self.motor_voz.say(texto)  # Pasa el texto al motor de voz
            self.motor_voz.runAndWait()  # Ejecuta la síntesis y reproducción
            time.sleep(0.2)  # Pequeña pausa para evitar cortar la animación antes de tiempo
            Clock.schedule_once(detener_animacion)  # Programa detener animación en hilo principal

        threading.Thread(target=reproducir).start()  # Ejecuta la función reproducir en un hilo separado
        evento_termino.wait()  # Espera hasta que la síntesis termine (evento seteado)

    def escuchar(self):
        with sr.Microphone() as source:
            print("🎙️ Escuchando...")  # Mensaje en consola indicando que escucha
            self.reconocedor.adjust_for_ambient_noise(source,duration=0.5)  # Ajusta ruido ambiente para mejor reconocimiento
            try:
                # Escucha audio con timeout de 4 segundos y límite de frase de 4 segundos
                audio = self.reconocedor.listen(source, timeout=4, phrase_time_limit=4)
            except sr.WaitTimeoutError:
                print("Tiempo de espera agotado para escuchar.")  # Timeout si no hay entrada
                return None  # Retorna None si no detectó nada

        try:
            # Usa reconocimiento de Google para convertir audio en texto en español de España
            texto = self.reconocedor.recognize_google(audio, language="es-ES")
            print(f"🗣️ Entendido: {texto}")  # Muestra el texto reconocido
            return texto.lower()  # Devuelve el texto en minúsculas
        except sr.UnknownValueError:
            print("No se entendió.")  # No pudo reconocer el audio
        except sr.RequestError:
            print("Error en servicio de voz.")  # Error en conexión al servicio Google
        return None  # Retorna None en caso de error

    def escuchar_con_reintentos(self, intentos=2):
        # Intenta escuchar varias veces (por defecto 2)
        for _ in range(intentos):
            texto = self.escuchar()
            if texto:
                return texto  # Retorna el texto si se entiende correctamente
        return None  # Retorna None si no se logró entender en los intentos
