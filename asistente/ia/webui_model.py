import webbrowser

class WebUIModel:
    def __init__(self, url="http://localhost:7860"):
        self.url = url

    def responder(self, mensaje=None):
        try:
            webbrowser.open(self.url)
            return "Abriendo la interfaz web del modelo de inteligencia artificial."
        except webbrowser.Error as e:
            return f"No se pudo abrir el navegador: {e}"
        except Exception as e:
            return f"Ocurrió un error inesperado al abrir la página: {e}"
