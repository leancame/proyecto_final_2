# Importa el módulo os para poder establecer variables de entorno
import os
# Importa la clase Llama desde el paquete llama_cpp para interactuar con el modelo
from llama_cpp import Llama

# Define la clase TinyModel, que encapsula el uso de un modelo pequeño de lenguaje
class TinyModel:
    # Método constructor de la clase
    def __init__(
        self,
        modelo_path="modelos/tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf",  # Ruta por defecto al archivo del modelo
        n_ctx=2048,  # Número de tokens de contexto
        max_tokens=200  # Límite de tokens en la respuesta generada
    ):
        # Establece el nivel de log para evitar mensajes de depuración
        os.environ["LLAMA_CPP_LOG_LEVEL"] = "ERROR"
        # Guarda el número máximo de tokens para las respuestas
        self.max_tokens = max_tokens

        try:
            # Intenta cargar el modelo usando llama-cpp con la ruta y parámetros especificados
            self.llm = Llama(
                model_path=modelo_path,
                n_ctx=n_ctx,
                verbose=False
            )
        except Exception as e:
            # Si ocurre un error, lo muestra por consola y marca el modelo como no disponible
            print(f"[ERROR al cargar TinyModel]: {e}")
            self.llm = None

    # Método para generar una respuesta a partir de un mensaje dado
    def responder(self, mensaje):
        # Verifica si el modelo fue cargado correctamente
        if not self.llm:
            return "El modelo no está disponible. No se pudo cargar correctamente."

        try:
            # Construye el prompt con una instrucción clara y breve
            prompt = (
                "Eres un asistente de inteligencia artificial. Responde de forma breve, clara y precisa.\n"
                f"Usuario: {mensaje.strip()}\n"
                "IA:"
            )

            # Genera la respuesta del modelo, con control sobre temperatura y top_p para ajustar creatividad
            output = self.llm(
                prompt,
                max_tokens=self.max_tokens,
                temperature=0.2,     # Controla la aleatoriedad (más bajo = más determinista)
                top_p=0.30,          # Limita la probabilidad acumulada de las palabras elegidas
                stop=["\nUsuario:", "\nIA:"]  # Indica dónde detener la generación
            )

            # Extrae y devuelve el texto generado, quitando espacios innecesarios
            texto = output["choices"][0]["text"].strip()
            return texto
        except Exception as e:
            # En caso de error, se informa por consola y devuelve un mensaje de error
            print(f"[ERROR al responder con TinyModel]: {e}")
            return "Ocurrió un error al generar la respuesta con el modelo."
