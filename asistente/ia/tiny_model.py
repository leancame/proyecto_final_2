import os
from llama_cpp import Llama

class TinyModel:
    def __init__(
        self,
        modelo_path="modelos/tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf",
        n_ctx=2048,
        max_tokens=200
    ):
        os.environ["LLAMA_CPP_LOG_LEVEL"] = "ERROR"
        self.max_tokens = max_tokens

        try:
            self.llm = Llama(
                model_path=modelo_path,
                n_ctx=n_ctx,
                verbose=False
            )
        except Exception as e:
            print(f"[ERROR al cargar TinyModel]: {e}")
            self.llm = None

    def responder(self, mensaje):
        if not self.llm:
            return "El modelo no está disponible. No se pudo cargar correctamente."

        try:
            prompt = (
                "Eres un asistente de inteligencia artificial. Responde de forma breve, clara y precisa.\n"
                f"Usuario: {mensaje.strip()}\n"
                "IA:"
            )

            output = self.llm(
                prompt,
                max_tokens=self.max_tokens,
                temperature=0.2,
                top_p=0.30,
                stop=["\nUsuario:", "\nIA:"]
            )
            texto = output["choices"][0]["text"].strip()
            return texto
        except Exception as e:
            print(f"[ERROR al responder con TinyModel]: {e}")
            return "Ocurrió un error al generar la respuesta con el modelo."
