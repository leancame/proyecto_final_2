# main_kivy.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window

import threading

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

        self.output = TextInput(readonly=True, font_size=16, size_hint_y=0.85)
        self.root.add_widget(self.output)

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
        return self.root

    def mostrar_mensaje(self, texto):
        def actualizar(dt):
            self.output.text += f"{texto}\n"
        Clock.schedule_once(actualizar)

    def iniciar_asistente(self, instance):
        if self.hilo_asistente and self.hilo_asistente.is_alive():
            self.mostrar_mensaje("[INFO] Asistente ya está activo.")
            return

        self.mostrar_mensaje("[INFO] Iniciando asistente...")

        voz = Voz()
        voz.hablar = voz_original = voz.hablar

         # Redefinimos hablar para que también actualice la GUI
        def hablar_con_gui(texto):
            self.mostrar_mensaje(f"Asistente: {texto}")
            voz_original(texto)
        
        voz.hablar = hablar_con_gui

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
