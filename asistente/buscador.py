# Importa el módulo para abrir enlaces en el navegador web predeterminado
import webbrowser
# Importa la librería para consultar Wikipedia
import wikipedia

# Clase que encapsula distintos métodos de búsqueda en la web
class Buscador:
    @staticmethod
    def buscar_en_google(query):
        """Re aliza una búsqueda en Google con el texto proporcionado."""
        webbrowser.open(f"https://www.google.com/search?q={query}")  # Abre la búsqueda en el navegador

    @staticmethod
    def buscar_en_wikipedia(query):
        """Busca un resumen del término en Wikipedia en español."""
        wikipedia.set_lang("es")  # Establece el idioma a español
        try:
            resultado = wikipedia.summary(query)  # Obtiene el resumen del artículo
            return resultado
        except wikipedia.exceptions.DisambiguationError as e:
            # Si hay múltiples resultados posibles, pide más precisión
            return f"La búsqueda es ambigua. ¿Puedes ser más específico? Ejemplos: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            # Si no se encuentra ningún resultado
            return "No encontré nada en Wikipedia con ese término."
        except Exception as e:
            # Cualquier otro error que pueda ocurrir
            return f"Ocurrió un error buscando en Wikipedia: {e}"

    @staticmethod
    def buscar_en_youtube(query):
        """Realiza una búsqueda en YouTube con el texto proporcionado."""
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")  # Abre la búsqueda en YouTube

