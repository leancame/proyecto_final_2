# Importaciones de Kivy necesarias para construir la interfaz gráfica
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

# Importaciones estándar
import threading
import os

# Importa módulos del asistente
from asistente.clima import Clima
from asistente.core import AsistenteVirtual
from asistente.buscador import Buscador
from asistente.ia.tiny_model import TinyModel
from asistente.voz import VozSincronizada  # Clase para hablar y animar boca

# Clase principal de la aplicación que hereda de Kivy App
class AsistenteApp(App):
    def build(self):
        self.title = "Asistente Virtual"            # Título de la ventana
        Window.size = (600, 600)                    # Tamaño de la ventana

        self.root = BoxLayout(orientation='vertical')  # Layout principal vertical

        # Imagen de animación (boca) en la parte superior
        self.animacion = Image(size_hint_y=0.55, allow_stretch=True, keep_ratio=False)
        self.root.add_widget(self.animacion)

        # Cuadro de texto para salida de mensajes
        self.output = TextInput(readonly=True, font_size=16, size_hint_y=0.30)
        self.root.add_widget(self.output)

        # Botones (activar y salir)
        button_box = BoxLayout(size_hint_y=0.15)
        self.boton_activar = Button(text="Activar asistente")
        self.boton_activar.bind(on_press=self.iniciar_asistente)
        button_box.add_widget(self.boton_activar)

        self.boton_salir = Button(text="Salir")
        self.boton_salir.bind(on_press=self.salir)
        button_box.add_widget(self.boton_salir)

        self.root.add_widget(button_box)

        # Inicialización de animación de boca
        self.frames = []                # Lista de frames de animación
        self.frame_index = 0            # Índice del frame actual
        self.animacion_event = None     # Evento programado de animación

        self.cargar_frames()            # Cargar imágenes desde carpeta
        if self.frames:
            self.animacion.texture = self.frames[0]  # Mostrar primer frame

        return self.root

    # Carga los frames (texturas) de la animación desde disco
    def cargar_frames(self):
        ruta_frames = "./animacion_frames"
        if not os.path.exists(ruta_frames):
            print(f"[WARN] Carpeta {ruta_frames} no existe.")
            return
        archivos = sorted([f for f in os.listdir(ruta_frames) if f.endswith(".jpg")])
        for archivo in archivos:
            frame = CoreImage(os.path.join(ruta_frames, archivo)).texture
            self.frames.append(frame)

    # Función para animar la boca, se ejecuta periódicamente
    def animar_boca(self, dt):
        if not self.frames:
            return
        self.animacion.texture = self.frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.frames)

    # Muestra un mensaje en el cuadro de texto, de forma segura desde otros hilos
    def mostrar_mensaje(self, texto):
        def actualizar(dt):
            self.output.text += f"{texto}\n"
            self.output.cursor = (0, len(self.output.text.splitlines()))
        Clock.schedule_once(actualizar)

    # Inicia el asistente virtual en un hilo independiente
    def iniciar_asistente(self, instance):
        if hasattr(self, 'hilo_asistente') and self.hilo_asistente.is_alive():
            self.mostrar_mensaje("[INFO] Asistente ya está activo.")
            return

        self.mostrar_mensaje("[INFO] Iniciando asistente...")

        # Crea la instancia de voz sincronizada con animador, imagen y frames
        voz = VozSincronizada(animador=self.animar_boca, imagen_widget=self.animacion, frames=self.frames)
        voz.set_mensaje_callback(self.mostrar_mensaje)  # Define cómo mostrar mensajes en la interfaz

        API_KEY_METEOBLUE = "Y3PlHAaROkU6qm4d"  # API key para servicio del clima

        # Diccionario de servicios usados por el asistente
        servicios = {
            'buscador': Buscador(),
            'modelo_ia': TinyModel(),
            'clima': Clima(API_KEY_METEOBLUE)
        }

        # Instancia del asistente con voz y servicios configurados
        self.asistente = AsistenteVirtual(voz, servicios)

        # Ejecuta el asistente en un hilo separado para no bloquear la UI
        def ejecutar():
            self.asistente.iniciar()

        self.hilo_asistente = threading.Thread(target=ejecutar)
        self.hilo_asistente.start()

    # Detiene el asistente y la aplicación
    def salir(self, instance):
        if hasattr(self, 'asistente'):
            self.asistente.stop()
        if hasattr(self, 'hilo_asistente') and self.hilo_asistente.is_alive():
            self.hilo_asistente.join()  # Espera a que el hilo termine
        self.stop()  # Cierra la app de Kivy

# Punto de entrada principal de la aplicación
if __name__ == "__main__":
    AsistenteApp().run()
