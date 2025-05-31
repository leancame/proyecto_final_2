import time
import importlib
import pkgutil
from .comando.base import BaseComando

class AsistenteVirtual:
    def __init__(self, voz, servicios):
        self.voz = voz
        self.servicios = servicios
        self.comandos = self._cargar_comandos()
        print("[INFO] Asistente virtual inicializado.")

    def _cargar_comandos(self):
        comandos = []
        paquete = 'asistente.comando'

        for _, nombre, _ in pkgutil.iter_modules(__import__(paquete, fromlist=['']).__path__):
            if nombre == "base":
                continue  # Saltamos la base
            modulo = importlib.import_module(f"{paquete}.{nombre}")
            for atributo in dir(modulo):
                clase = getattr(modulo, atributo)
                if isinstance(clase, type) and issubclass(clase, BaseComando) and clase is not BaseComando:
                    comandos.append(clase(self.voz, self.servicios))
        return comandos

    def iniciar(self):
        # 🔄 Esta llamada ya está sincronizada gracias a main.py
        self.voz.hablar("¡Hola! Soy tu asistente virtual.")
        time.sleep(0.5)
        self.voz.hablar("¿En qué puedo ayudarte hoy?")

        while True:
            comando = self.voz.escuchar()
            if comando is None:
                continue
            if "salir" in comando:
                self.voz.hablar("Hasta luego.")
                break
            self._procesar_comando(comando)

    def _procesar_comando(self, comando):
        if comando in ("detener", "para", "parar", "detén", "finaliza"):
            for cmd in self.comandos:
                if hasattr(cmd, "detener"):
                    cmd.detener()
            return

        for cmd in self.comandos:
            if cmd.activar(comando):
                cmd.ejecutar(comando)
                return

        self.voz.hablar("Lo siento, no entendí ese comando.")
