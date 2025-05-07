# Importa la librería de tiempo para pausas
import time
# Importa herramientas para cargar módulos dinámicamente
import importlib
# Importa utilidades para iterar sobre módulos de un paquete
import pkgutil
# Importa la clase base que todos los comandos deben extender
from .comando.base import BaseComando

# Clase principal del asistente virtual
class AsistenteVirtual:
    def __init__(self, voz, servicios):
        self.voz = voz  # Instancia del sistema de voz (hablar/escuchar)
        self.servicios = servicios  # Diccionario o conjunto de servicios disponibles (DB, Google, etc.)
        self.comandos = self._cargar_comandos()  # Carga dinámica de comandos personalizados
        print("[INFO] Asistente virtual inicializado.")

    # Método privado para cargar dinámicamente los comandos disponibles
    def _cargar_comandos(self):
        comandos = []  # Lista para guardar instancias de comandos válidos
        paquete = 'asistente.comando'  # Ruta del paquete de comandos

        # Itera sobre todos los módulos del paquete
        for _, nombre, _ in pkgutil.iter_modules(__import__(paquete, fromlist=['']).__path__):
            if nombre == "base":
                continue  # Omite la clase base de comandos

            # Importa el módulo del comando
            modulo = importlib.import_module(f"{paquete}.{nombre}")

            # Busca clases dentro del módulo
            for atributo in dir(modulo):
                clase = getattr(modulo, atributo)
                # Verifica si es una subclase válida de BaseComando y no es la clase base misma
                if isinstance(clase, type) and issubclass(clase, BaseComando) and clase is not BaseComando:
                    # Crea una instancia del comando y la agrega a la lista
                    comandos.append(clase(self.voz, self.servicios))

        return comandos  # Retorna la lista de comandos cargados

    # Método para iniciar el asistente
    def iniciar(self):
        self.voz.hablar("¡Hola! Soy tu asistente virtual.")  # Saludo inicial
        time.sleep(1)
        self.voz.hablar("¿En qué puedo ayudarte hoy?")  # Pregunta al usuario

        while True:
            comando = self.voz.escuchar()  # Escucha un comando
            if comando is None:
                continue  # Si no entendió nada, vuelve a escuchar
            if "salir" in comando:
                self.voz.hablar("Hasta luego.")  # Despedida
                break  # Sale del bucle
            self._procesar_comando(comando)  # Procesa el comando

    # Método para procesar comandos dados por voz
    def _procesar_comando(self, comando):
        # Si el comando es de tipo "detener", intenta ejecutar el método detener de todos los comandos
        if comando in ("detener", "para", "parar", "detén", "finaliza"):
            for cmd in self.comandos:
                if hasattr(cmd, "detener"):  # Verifica si el comando tiene método detener
                    cmd.detener()
            return

        # Intenta activar y ejecutar el comando correspondiente
        for cmd in self.comandos:
            if cmd.activar(comando):  # Si el comando reconoce la orden
                cmd.ejecutar(comando)  # Ejecuta la acción correspondiente
                return

        # Si ningún comando reconoce la orden, avisa al usuario
        self.voz.hablar("Lo siento, no entendí ese comando.")

