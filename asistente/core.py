import time  # Importa el módulo time para manejar pausas y temporizadores
import importlib  # Importa importlib para importar módulos de forma dinámica
import pkgutil  # Importa pkgutil para iterar sobre módulos en un paquete
from .comando.base import BaseComando  # Importa la clase base para comandos desde el paquete comando

class AsistenteVirtual:
    def __init__(self, voz, servicios):
        self.voz = voz  # Guarda la instancia del sistema de voz para interacción
        self.servicios = servicios  # Guarda la instancia de servicios que el asistente puede usar
        self.comandos = self._cargar_comandos()  # Carga dinámicamente los comandos disponibles
        self._detener = False  # Variable para controlar la detención del asistente
        print("[INFO] Asistente virtual inicializado.")  # Mensaje informativo de inicialización

    def _cargar_comandos(self):
        comandos = []  # Lista para almacenar las instancias de comandos cargados
        paquete = 'asistente.comando'  # Nombre del paquete donde están los comandos

        for _, nombre, _ in pkgutil.iter_modules(__import__(paquete, fromlist=['']).__path__):
            if nombre == "base":
                continue  # Ignora el módulo base.py que contiene la clase BaseComando
            modulo = importlib.import_module(f"{paquete}.{nombre}")  # Importa el módulo dinámicamente
            for atributo in dir(modulo):  # Itera sobre los atributos del módulo importado
                clase = getattr(modulo, atributo)  # Obtiene el atributo (posible clase)
                # Verifica si el atributo es una clase que hereda de BaseComando y no es BaseComando
                if isinstance(clase, type) and issubclass(clase, BaseComando) and clase is not BaseComando:
                    comandos.append(clase(self.voz, self.servicios))  # Instancia y añade el comando a la lista
        return comandos  # Devuelve la lista de comandos cargados

    def iniciar(self):
        # 🔄 Esta llamada ya está sincronizada gracias a main.py
        self.voz.hablar("¡Hola! Soy tu asistente virtual.")  # Saludo inicial del asistente
        time.sleep(0.5)  # Pausa breve para mejorar la interacción
        self.voz.hablar("¿En qué puedo ayudarte hoy?")  # Pregunta inicial para el usuario

        while not self._detener:  # Bucle principal que se ejecuta hasta que se detenga el asistente
            comando = self.voz.escuchar()  # Escucha el comando de voz del usuario
            if comando is None:
                continue  # Si no se detecta comando, continúa esperando
            if "salir" in comando:  # Si el usuario dice "salir", termina la ejecución
                self.voz.hablar("Hasta luego.")  # Despedida del asistente
                break  # Sale del bucle y termina la función
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

    def stop(self):
        self._detener = True
