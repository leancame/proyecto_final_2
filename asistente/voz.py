# Importa la librería para sintetizar voz (Text-to-Speech)
import pyttsx3
# Importa la librería para reconocimiento de voz
import speech_recognition as sr

# Clase que maneja la entrada y salida de voz
class Voz:
    def __init__(self):
        # Inicializa el reconocedor de voz
        self.reconocedor = sr.Recognizer()
        # Inicializa el motor de texto a voz
        self.motor_voz = pyttsx3.init()

    def hablar(self, texto):
        """Convierte el texto en voz y lo reproduce."""
        self.motor_voz.say(texto)  # Agrega el texto a la cola de reproducción
        self.motor_voz.runAndWait()  # Reproduce el texto en voz alta

    def escuchar(self):
        """Escucha un comando por el micrófono y lo convierte en texto."""
        with sr.Microphone() as source:  # Usa el micrófono como fuente de audio
            print("Escuchando...")
            # Ajusta para ruido de fondo
            self.reconocedor.adjust_for_ambient_noise(source)
            # Escucha lo que se diga
            audio = self.reconocedor.listen(source)

            try:
                # Usa Google Speech Recognition para convertir el audio en texto
                texto = self.reconocedor.recognize_google(audio, language="es-ES")
                print(f"Lo que dijiste: {texto}")
                return texto.lower()  # Devuelve el texto en minúsculas
            except sr.UnknownValueError:
                # Si no entiende lo que se dijo
                print("No te entendí, por favor repite.")
            except sr.RequestError:
                # Si hay un error con la API de Google
                print("Error al conectarse al servicio de reconocimiento de voz.")
    
    def escuchar_con_reintentos(self, intentos=2):
        """Intenta escuchar varias veces si no entiende a la primera."""
        for _ in range(intentos):
            texto = self.escuchar()
            if texto:
                return texto  # Devuelve el texto si se entendió
        return None  # Devuelve None si no se entendió en los intentos dados

