# Importa la clase Llama desde el módulo llama_cpp, necesario para cargar y usar modelos LLaMA
from llama_cpp import Llama

# Define la clase BigModel, que encapsula el uso de un modelo LLaMA para generar respuestas
class BigModel:
    
    # Método constructor de la clase, con un parámetro opcional para la ruta del modelo
    def __init__(self, modelo="modelos/mistral-7b-instruct-v0.2.Q4_K_M.gguf"):
        try:
            # Intenta cargar el modelo especificado usando llama-cpp
            # n_ctx define el número de tokens de contexto (2048)
            # verbose=False evita que se imprima información adicional
            self.llama = Llama(model_path=modelo, n_ctx=2048, verbose=False)
        except Exception as e:
            # En caso de error al cargar el modelo, se muestra un mensaje y se marca como no disponible
            print(f"[ERROR al cargar BigModel]: {e}")
            self.llama = None

    # Método para generar una respuesta a partir de un mensaje dado
    def responder(self, mensaje):
        # Verifica si el modelo fue cargado correctamente
        if not self.llama:
            # Si no está disponible, devuelve un mensaje de error
            return "El modelo no está disponible. No se pudo cargar correctamente."

        try:
            # Construye el prompt que se le pasará al modelo
            # Usa el formato de instrucciones para modelos tipo instruct, y fuerza la respuesta en español
            prompt = (
                "<<SYS>>\n"
                "Eres un asistente conversacional que RESPONDE SIEMPRE EN ESPAÑOL.\n"
                "<<SYS>>\n"
                f"[INST] {mensaje.strip()} [/INST]"
            )
            
            # Llama al modelo para generar una respuesta, con un máximo de 500 tokens
            # El parámetro 'stop' indica dónde debe detenerse la generación
            resultado = self.llama(
                prompt,
                max_tokens=500,
                stop=["</s>"]
            )

            # Extrae y devuelve el texto generado por el modelo, limpiando espacios en blanco
            return resultado["choices"][0]["text"].strip()
        except Exception as e:
            # Si ocurre un error durante la generación de texto, se informa y devuelve un mensaje de error
            print(f"[ERROR al responder con BigModel]: {e}")
            return "Ocurrió un error al generar la respuesta con el modelo."
