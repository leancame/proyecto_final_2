from .base import BaseComando  # Importa la clase base que define la estructura de los comandos
from asistente.ia.tiny_model import TinyModel  # Importa el modelo de IA liviano
from asistente.ia.big_model import BigModel  # Importa el modelo de IA más avanzado
from asistente.ia.webui_model import WebUIModel  # Importa el modelo que interactúa con una interfaz web remota

class ComandoIA(BaseComando):  # Define la clase del comando de inteligencia artificial
    def activar(self, comando: str) -> bool:  # Método que determina si este comando debe ejecutarse
        return "modelo" in comando or "charlar" in comando or "hablar con" in comando  # Se activa si se detectan estas palabras

    def ejecutar(self, comando: str):  # Método principal que ejecuta el comando
        try:
            comando = comando.lower()  # Convierte el texto a minúsculas para facilitar las comparaciones
            modelo_actual = None  # Variable para almacenar qué modelo se seleccionó

            # === Cambiar modelo IA ===
            if "modelo pequeño" in comando or "modelo tiny" in comando:  # Si el usuario pide el modelo pequeño
                self.servicios["modelo_ia"] = TinyModel()  # Carga una instancia del modelo liviano
                modelo_actual = "TinyModel"  # Guarda el nombre del modelo actual
            elif "modelo grande" in comando or "modelo big" in comando:  # Si se menciona el modelo grande
                self.servicios["modelo_ia"] = BigModel()  # Carga una instancia del modelo más potente
                modelo_actual = "BigModel"
            elif "modelo web" in comando or "modelo remoto" in comando:  # Si se quiere el modelo remoto
                self.servicios["modelo_ia"] = WebUIModel()  # Carga el modelo que accede vía web
                modelo_actual = "WebUIModel"

            if modelo_actual:  # Si se seleccionó un modelo
                self.voz.hablar(f"Modelo cambiado a {modelo_actual}.")  # Informa al usuario el cambio
                print(f"[DEBUG] Modelo actualizado: {modelo_actual}")  # Mensaje de depuración
                return  # Finaliza la ejecución, ya que no se va a charlar aún

            # === Conversar con IA ===
            modelo = self.servicios.get("modelo_ia")  # Obtiene el modelo actualmente en uso
            if not modelo:  # Si no hay modelo cargado
                self.voz.hablar("No hay modelo de inteligencia artificial cargado.")  # Informa error al usuario
                return  # Finaliza

            self.voz.hablar("Iniciando conversación con la inteligencia artificial. Di 'adiós' para salir.")  # Anuncia inicio de charla

            while True:  # Ciclo infinito para mantener la conversación
                try:
                    entrada = self.voz.escuchar()  # Escucha lo que dice el usuario
                    if entrada:  # Si se detectó entrada
                        print(f"Tú: {entrada}")  # Muestra lo que dijo el usuario
                        if "adiós" in entrada.lower():  # Si el usuario quiere terminar la charla
                            self.voz.hablar("Hasta luego, volvemos a los comandos.")  # Despide
                            break  # Sale del bucle

                        respuesta = modelo.responder(entrada)  # Pide respuesta al modelo IA
                        print(f"IA: {respuesta}")  # Muestra la respuesta en consola
                        self.voz.hablar(respuesta)  # Reproduce la respuesta con voz
                    else:
                        self.voz.hablar("No entendí, intenta de nuevo o di 'adiós' para salir.")  # Si no se entendió lo que dijo el usuario
                except Exception as e:  # Si ocurre un error dentro de la conversación
                    print(f"[ERROR Conversación IA]: {e}")  # Muestra el error
                    self.voz.hablar("Hubo un error durante la conversación con la IA.")  # Informa al usuario
        except Exception as e:  # Si ocurre un error fuera del bucle principal
            print(f"[ERROR ComandoIA]: {e}")  # Imprime el error general
            self.voz.hablar("Ocurrió un error al ejecutar el comando de inteligencia artificial.")  # Mensaje de error general

