# Clase base que define la estructura que deben seguir todos los comandos del asistente
class BaseComando:
    def __init__(self, voz, servicios):
        self.voz = voz  # Objeto que permite hablar y escuchar
        self.servicios = servicios  # Diccionario de servicios disponibles (como buscador, clima, etc.)

    def activar(self, comando: str) -> bool:
        # Este método debe ser implementado por cada comando.
        # Su propósito es analizar si el texto del comando activa esta clase.
        raise NotImplementedError  # Lanza un error si no se sobrescribe en la subclase

    def ejecutar(self, comando: str):
        # Este método también debe implementarse en la subclase.
        # Contiene la lógica a ejecutar cuando se activa el comando.
        raise NotImplementedError  # Lanza un error si no se sobrescribe en la subclase

    def detener(self):
        """Este método es opcional. Permite detener acciones en curso como una reproducción, lectura, etc."""
        pass  # No hace nada por defecto. Las subclases pueden redefinirlo si lo necesitan.

    def es_cancelacion(self, texto: str) -> bool:
        """Detecta si el usuario quiere cancelar el comando actual."""
        return texto.strip().lower() in ["cancelar", "salir", "finalizar", "adiós"]
