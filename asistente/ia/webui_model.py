# Importa el módulo webbrowser para controlar el navegador web predeterminado
import webbrowser

# Define la clase WebUIModel que representa un modelo accesible vía interfaz web
class WebUIModel:
    # Método constructor que recibe una URL para la interfaz web (por defecto localhost)
    def __init__(self, url="http://localhost:7860"):
        self.url = url  # Guarda la URL como atributo de instancia

    # Método para "responder" que en realidad abre la interfaz web del modelo
    def responder(self, mensaje=None):
        try:
            # Intenta abrir la URL en el navegador web predeterminado
            webbrowser.open(self.url)
            # Devuelve un mensaje confirmando la acción
            return "Abriendo la interfaz web del modelo de inteligencia artificial."
        # Captura errores específicos relacionados con el navegador
        except webbrowser.Error as e:
            # Devuelve un mensaje indicando que no se pudo abrir el navegador
            return f"No se pudo abrir el navegador: {e}"
        # Captura cualquier otro error inesperado
        except Exception as e:
            # Devuelve un mensaje genérico de error
            return f"Ocurrió un error inesperado al abrir la página: {e}"
