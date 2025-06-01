import webbrowser

class WebUIModel:
    def __init__(self, url="http://localhost:7860"):
        self.url = url

    def responder(self, mensaje=None):
        try:
            webbrowser.open(self.url)
            return f"Abriendo la interfaz web"
        except Exception as e:
            return f"Error al abrir la página: {e}"
