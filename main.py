import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

import threading
import os

# Importa tu asistente
from asistente.core import AsistenteVirtual
from asistente.voz import Voz
from asistente.buscador import Buscador
from asistente.ia.tiny_model import TinyModel


class AsistenteApp(App):
    def build(self):
        self.title = "Asistente Virtual"
        Window.size = (600, 800)

        self.root = BoxLayout(orientation='vertical')

        # Imagen para animación (boca hablando)
        self.animacion = Image(size_hint_y=0.55, allow_stretch=True, keep_ratio=False)
        self.root.add_widget(self.animacion)

        # Cuadro de texto para mostrar mensajes
        self.output = TextInput(readonly=True, font_size=16, size_hint_y=0.30)
        self.root.add_widget(self.output)

        # Caja para botones
        button_box = BoxLayout(size_hint_y=0.15)
        self.boton_activar = Button(text="Activar asistente")
        self.boton_activar.bind(on_press=self.iniciar_asistente)
        button_box.add_widget(self.boton_activar)

        self.boton_salir = Button(text="Salir")
        self.boton_salir.bind(on_press=self.salir)
        button_box.add_widget(self.boton_salir)

        self.root.add_widget(button_box)

        self.asistente = None
        self.hilo_asistente = None

        # Variables para animación
        self.frames = []
        self.frame_index = 0
        self.animacion_event = None

        self.cargar_frames()

        # Mostrar imagen inicial (boca cerrada)
        if self.frames:
            self.animacion.texture = self.frames[0]

        return self.root

    def cargar_frames(self):
        ruta_frames = "./animacion_frames"
        if not os.path.exists(ruta_frames):
            print(f"[WARN] Carpeta {ruta_frames} no existe. No se cargan frames de animación.")
            return
        archivos = sorted([f for f in os.listdir(ruta_frames) if f.endswith(".jpg")])
        for archivo in archivos:
            frame = CoreImage(os.path.join(ruta_frames, archivo)).texture
            self.frames.append(frame)
        print(f"[INFO] {len(self.frames)} frames de animación cargados.")

    def animar_boca(self, dt):
        if not self.frames:
            return
        self.animacion.texture = self.frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.frames)

    def mostrar_mensaje(self, texto):
        def actualizar(dt):
            self.output.text += f"{texto}\n"
            self.output.cursor = (0, len(self.output.text.splitlines()))
        Clock.schedule_once(actualizar)

    def iniciar_asistente(self, instance):
        if self.hilo_asistente and self.hilo_asistente.is_alive():
            self.mostrar_mensaje("[INFO] Asistente ya está activo.")
            return

        self.mostrar_mensaje("[INFO] Iniciando asistente...")

        voz = Voz()
        voz_original = voz.hablar

        def hablar_con_gui(texto):
            self.mostrar_mensaje(f"Asistente: {texto}")

            evento_termino = threading.Event()

            def iniciar_animacion():
                self.frame_index = 0
                if self.animacion_event is None:
                    self.animacion_event = Clock.schedule_interval(self.animar_boca, 0.1)

            def detener_animacion(dt=None):
                if self.animacion_event:
                    self.animacion_event.cancel()
                    self.animacion_event = None
                if self.frames:
                    self.animacion.texture = self.frames[0]  # Boca cerrada
                evento_termino.set()  # Señala que terminó la voz y animación

            Clock.schedule_once(lambda dt: iniciar_animacion())

            def reproducir_y_esperar():
                voz_original(texto)
                time.sleep(0.5)
                Clock.schedule_once(detener_animacion)

            threading.Thread(target=reproducir_y_esperar).start()

            evento_termino.wait()

        voz.hablar = hablar_con_gui
        voz.hablar_con_gui = hablar_con_gui  # Agrega alias para llamar desde comandos






        servicios = {
            'buscador': Buscador(),
            'modelo_ia': TinyModel()
        }

        self.asistente = AsistenteVirtual(voz, servicios)

        def ejecutar():
            self.asistente.iniciar()

        self.hilo_asistente = threading.Thread(target=ejecutar)
        self.hilo_asistente.start()

    def salir(self, instance):
        self.stop()


if __name__ == "__main__":
    AsistenteApp().run()
