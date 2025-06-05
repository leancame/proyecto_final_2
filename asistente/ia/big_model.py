from llama_cpp import Llama

class BigModel:
    def __init__(self, modelo="modelos/mistral-7b-instruct-v0.2.Q4_K_M.gguf"):
        try:
            # Carga el modelo .gguf con llama-cpp
            self.llama = Llama(model_path=modelo, n_ctx=2048, verbose=False)
        except Exception as e:
            print(f"[ERROR al cargar BigModel]: {e}")
            self.llama = None

    def responder(self, mensaje):
        if not self.llama:
            return "El modelo no está disponible. No se pudo cargar correctamente."

        try:
            prompt = (
                "<<SYS>>\n"
                "Eres un asistente conversacional que RESPONDE SIEMPRE EN ESPAÑOL.\n"
                "<<SYS>>\n"
                f"[INST] {mensaje.strip()} [/INST]"
            )
            resultado = self.llama(
                prompt,
                max_tokens=500,
                stop=["</s>"]
            )
            return resultado["choices"][0]["text"].strip()
        except Exception as e:
            print(f"[ERROR al responder con BigModel]: {e}")
            return "Ocurrió un error al generar la respuesta con el modelo."
