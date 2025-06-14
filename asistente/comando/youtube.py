import yt_dlp  # Importa la biblioteca yt_dlp para buscar y descargar videos de YouTube
import webbrowser  # Importa el módulo webbrowser para abrir URLs en el navegador
import os  # Importa el módulo os para operaciones del sistema
import tempfile  # Importa tempfile para manejar archivos temporales
import pygame  # Importa pygame para reproducir audio
import time  # Importa time para agregar demoras en la ejecución
import re  # Importa re para trabajar con expresiones regulares
from .base import BaseComando  # Importa la clase base desde otro módulo local

ffmpeg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ffmpeg/bin'))  # Obtiene la ruta absoluta al ejecutable de ffmpeg
os.environ["PATH"] += os.pathsep + ffmpeg_path  # Agrega la ruta de ffmpeg al PATH del sistema operativo

class ComandoYouTube(BaseComando):  # Define una clase que hereda de BaseComando
    def __init__(self, voz, servicios):  # Constructor de la clase
        super().__init__(voz, servicios)  # Llama al constructor de la clase base
        self.reproduciendo = False  # Variable para saber si se está reproduciendo algo

    def activar(self, comando):  # Método para determinar si el comando debe activarse
        return "buscar en youtube" in comando or "reproducir en youtube" in comando  # Devuelve True si el comando incluye estas frases

    def ejecutar(self, comando):  # Método principal que ejecuta el comando
        try:  # Manejo de excepciones
            solo_audio = "solo audio" in comando or "audio" in comando  # Verifica si el usuario quiere solo el audio
            query = comando.replace("buscar en youtube", "").replace("reproducir en youtube", "").strip()  # Limpia la consulta

            if not query:  # Si la consulta está vacía
                self.voz.hablar("¿Qué deseas buscar en YouTube?")  # Pide al usuario que diga algo
                query = self.voz.escuchar_con_reintentos()  # Escucha al usuario con reintentos

            if not query or self._es_cancelacion(query):  # Si sigue vacía o se dice cancelar
                self.voz.hablar("Cancelado.")  # Informa cancelación
                return  # Sale del método

            self.voz.hablar(f"Buscando {query} en YouTube...")  # Informa que está buscando
            videos = self.buscar_videos(query)  # Realiza la búsqueda de videos

            if not videos:  # Si no hay resultados
                self.voz.hablar("No encontré videos.")  # Informa que no se encontraron resultados
                return  # Termina ejecución

            self.voz.hablar("Aquí tienes tres opciones:")  # Anuncia las opciones al usuario
            for i, video in enumerate(videos[:3]):  # Itera sobre los primeros tres resultados
                titulo = video.get('title', 'Sin título')  # Obtiene el título del video
                canal = video.get('uploader', 'Canal desconocido')  # Obtiene el nombre del canal
                duracion = self.formatear_duracion(video.get('duration'))  # Formatea la duración
                self.voz.hablar(f"{i + 1}. {titulo}, del canal {canal}, duración {duracion}")  # Dice la información al usuario
                time.sleep(0.5)  # Pausa para que no hable muy rápido

            max_intentos = 3  # Establece cuántos intentos tiene el usuario para elegir
            for intento in range(max_intentos):  # Repite el proceso de elección
                self.voz.hablar("Dime el número del video que quieres reproducir.")  # Solicita una elección
                eleccion = self.voz.escuchar_con_reintentos(2)  # Escucha la elección con reintentos

                if not eleccion or self._es_cancelacion(eleccion):  # Si no hay respuesta o se cancela
                    self.voz.hablar("Cancelado.")  # Informa cancelación
                    return  # Termina ejecución

                modo_audio = "audio" in eleccion or "solo audio" in eleccion  # Verifica si quiere solo audio
                eleccion = eleccion.replace("audio", "").replace("solo audio", "").strip()  # Limpia la respuesta

                indice = self._convertir_a_numero(eleccion) - 1  # Convierte la respuesta a índice de lista
                if 0 <= indice < len(videos):  # Si la elección es válida
                    video_url = videos[indice].get('webpage_url')  # Obtiene la URL del video
                    if not video_url:  # Si no se puede obtener la URL
                        self.voz.hablar("No se pudo obtener el enlace del video.")  # Informa error
                        return  # Sale

                    if modo_audio or solo_audio:  # Si el usuario quiere solo audio
                        self.voz.hablar("Reproduciendo solo el audio.")  # Informa reproducción de audio
                        self.reproducir_audio(video_url)  # Llama a la función para reproducir el audio
                    else:  # Si quiere el video
                        webbrowser.open(video_url)  # Abre el video en el navegador
                        self.voz.hablar("Reproduciendo en YouTube.")  # Informa reproducción
                    return  # Termina la función

                self.voz.hablar("Número inválido.")  # Si el número es incorrecto, lo informa
            self.voz.hablar("No entendí tu elección. Intenta nuevamente más tarde.")  # Si agota los intentos
        except Exception as e:  # Captura errores
            self.voz.hablar("Ocurrió un error al procesar tu solicitud en YouTube.")  # Informa al usuario
            print(f"[ERROR en ComandoYouTube]: {e}")  # Muestra el error en consola

    def buscar_videos(self, query):  # Método para buscar videos en YouTube
        try:
            ydl_opts = {
                'quiet': True,  # Sin salida por consola
                'extract_flat': False,  # Extrae detalles completos
                'dump_single_json': True,  # Devuelve resultados en JSON
                'skip_download': True,  # No descarga el video
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Inicializa el cliente yt_dlp
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)  # Busca los primeros 5 resultados
                return info.get('entries', [])  # Devuelve la lista de resultados
        except Exception as e:  # Manejo de errores
            print(f"[ERROR al buscar videos]: {e}")  # Imprime el error
            return []  # Devuelve lista vacía

    def reproducir_audio(self, url):  # Método para reproducir solo el audio de un video
        try:
            ydl_opts = {
                'format': 'bestaudio/best',  # Selecciona el mejor audio disponible
                'quiet': True,  # Sin salida en consola
                'outtmpl': os.path.join(tempfile.gettempdir(), 'audio.%(ext)s'),  # Ruta temporal para guardar
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',  # Extrae el audio usando FFmpeg
                    'preferredcodec': 'mp3',  # Formato preferido
                    'preferredquality': '192',  # Calidad preferida
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Inicia cliente de descarga
                info = ydl.extract_info(url, download=True)  # Descarga el audio
                audio_path = os.path.join(tempfile.gettempdir(), 'audio.mp3')  # Ruta del archivo mp3

                if os.path.exists(audio_path):  # Verifica que se descargó correctamente
                    if not pygame.mixer.get_init():  # Inicializa el mixer si no lo está
                        pygame.mixer.init()
                    pygame.mixer.music.load(audio_path)  # Carga el archivo de audio
                    pygame.mixer.music.play()  # Comienza la reproducción
                    self.reproduciendo = True  # Cambia el estado
                    self.voz.hablar("Reproduciendo audio. Di 'detener' para parar.")  # Informa al usuario

                    while pygame.mixer.music.get_busy():  # Mientras se esté reproduciendo
                        comando = self.voz.escuchar_con_reintentos(1)  # Escucha comandos
                        if comando and any(p in comando for p in ["detener", "para", "parar", "finaliza", "cancelar"]):  # Si dice parar
                            self.detener()  # Detiene la reproducción
                            break
                        time.sleep(0.5)  # Espera para no saturar CPU

                    pygame.mixer.quit()  # Finaliza el mixer
                    self.reproduciendo = False  # Cambia el estado
                    if os.path.exists(audio_path):  # Borra el archivo si existe
                        os.remove(audio_path)
                else:
                    self.voz.hablar("No se pudo reproducir el audio.")  # Informa error
        except Exception as e:
            self.voz.hablar("Ocurrió un error durante la reproducción de audio.")  # Informa error
            print(f"[ERROR en reproducir_audio]: {e}")  # Imprime el error

    def detener(self):  # Método para detener el audio
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():  # Verifica si está reproduciendo
                pygame.mixer.music.stop()  # Detiene la música
                pygame.mixer.quit()  # Cierra el mixer
                self.voz.hablar("Audio detenido.")  # Informa al usuario
        except Exception as e:
            self.voz.hablar("No se pudo detener el audio correctamente.")  # Informa error
            print(f"[ERROR al detener audio]: {e}")  # Muestra el error

    def formatear_duracion(self, segundos):  # Método para convertir segundos a texto
        try:
            if segundos is None:  # Si no hay duración
                return "desconocida"  # Devuelve valor por defecto
            minutos, seg = divmod(segundos, 60)  # Convierte a minutos y segundos
            return f"{minutos} minutos y {seg} segundos" if minutos else f"{seg} segundos"  # Retorna texto
        except Exception:
            return "desconocida"  # Si ocurre error, devuelve texto genérico

    def _convertir_a_numero(self, texto):  # Convierte palabras a números
        texto = texto.strip().lower()  # Limpia el texto
        if re.search(r"\b1\b", texto): return 1  # Si contiene "1", devuelve 1
        if re.search(r"\b2\b", texto): return 2  # Si contiene "2", devuelve 2
        if re.search(r"\b3\b", texto): return 3  # Si contiene "3", devuelve 3
        mapa = {  # Diccionario de palabras equivalentes a números
            "uno": 1, "primero": 1, "el uno": 1,
            "dos": 2, "segundo": 2, "el dos": 2,
            "tres": 3, "tercero": 3, "el tres": 3
        }
        for palabra, num in mapa.items():  # Itera sobre el diccionario
            if palabra in texto:
                return num  # Devuelve el número asociado
        return -1  # Si no encuentra coincidencia, devuelve -1

    def _es_cancelacion(self, texto):  # Verifica si el usuario quiere cancelar
        texto = texto.strip().lower()  # Limpia el texto
        return texto in ["cancelar", "salir", "terminar", "adiós", "no", "ninguno"]  # Lista de palabras que indican cancelación
