# Importa la clase base que deben seguir todos los comandos
import re
from .base import BaseComando
# Importa las bibliotecas necesarias para el procesamiento de audio y video
import yt_dlp
import webbrowser
import os
import tempfile
import pygame
import time

# Añadir la ruta de ffmpeg si la tienes configurada en el directorio
# Se agrega la ruta de FFmpeg al PATH del sistema para poder usarlo con yt-dlp
ffmpeg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ffmpeg/bin'))
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Clase que implementa el comando para buscar y reproducir videos de YouTube
class ComandoYouTube(BaseComando):
    def __init__(self, voz, servicios):
        # Inicializa el comando con la voz y servicios proporcionados
        super().__init__(voz, servicios)
        self.reproduciendo = False  # Inicializa la variable para verificar si está reproduciendo audio o video

    def activar(self, comando):
        # Activa el comando si el texto contiene "buscar en youtube" o "reproducir en youtube"
        return "buscar en youtube" in comando or "reproducir en youtube" in comando

    def ejecutar(self, comando):
        # Detectar si se menciona "solo audio" o "audio" en el comando
        solo_audio = "solo audio" in comando or "audio" in comando
        # Extrae la consulta del comando quitando "buscar en youtube" o "reproducir en youtube"
        query = comando.replace("buscar en youtube", "").replace("reproducir en youtube", "").strip()

        # Si no se proporcionó una consulta, se le pide al usuario que la ingrese
        if not query:
            self.voz.hablar_con_gui("¿Qué deseas buscar en YouTube?")
            query = self.voz.escuchar()

        # Si no se obtuvo una consulta válida, se avisa al usuario
        if not query:
            self.voz.hablar("No entendí la búsqueda.")
            return

        # Informa al usuario que está buscando el video
        self.voz.hablar_con_gui(f"Buscando {query} en YouTube...")
        # Llama a la función para buscar videos en YouTube
        videos = self.buscar_videos(query)

        # Si no se encuentran videos, informa al usuario
        if not videos:
            self.voz.hablar("No encontré videos.")
            return

        # Lee los 3 primeros videos (título, canal y duración) y los presenta al usuario
        textos = []
        for i, video in enumerate(videos[:3]):
            titulo = video.get('title', 'Sin título')
            canal = video.get('uploader', 'Canal desconocido')
            duracion = self.formatear_duracion(video.get('duration'))
            textos.append(f"{i+1}. {titulo}, del canal {canal}, duración {duracion}")
        mensaje = "Aquí tienes tres opciones:\n" + "\n".join(textos)

        # Muestra las opciones en la interfaz si existe el método
        if hasattr(self.voz, "mostrar_mensaje"):
            self.voz.mostrar_mensaje(mensaje)
        # También habla las opciones usando la función que activa la animación
        if hasattr(self.voz, "hablar_con_gui"):
            self.voz.hablar_con_gui(mensaje)
        else:
            self.voz.hablar(mensaje)

        # Bucle hasta que se obtenga una elección válida del usuario
        max_intentos = 3
        for intento in range(max_intentos):
            # Pide al usuario que elija un video por número
            self.voz.hablar("Dime el número del video que quieres reproducir.")
            # Escucha el comando del usuario y permite reintentos
            eleccion = self.voz.escuchar_con_reintentos(2)

            print(f"[DEBUG] Elección escuchada: {eleccion}")

            # Si no se entendió el comando, pide al usuario que repita
            if eleccion is None:
                self.voz.hablar("No te entendí, por favor repite.")
                continue

            # Procesa la elección del usuario para ver si mencionó "solo audio" o "audio"
            eleccion = eleccion.lower().strip()
            if "solo audio" in eleccion or "audio" in eleccion:
                modo_audio = True
                # Elimina "solo audio" o "audio" de la elección para obtener el número del video
                eleccion = eleccion.replace("solo audio", "").replace("audio", "").strip()
            else:
                modo_audio = False

            # Convierte la elección a un número y lo ajusta al índice correspondiente
            indice = self._convertir_a_numero(eleccion) - 1 if eleccion else -1

            # Si el número es válido, se obtiene el video y se reproduce
            if 0 <= indice < len(videos):
                video = videos[indice]
                video_url = video.get('webpage_url') or video.get('url')

                # Si no se encuentra la URL del video, avisa al usuario
                if not video_url:
                    self.voz.hablar("No se encontró la URL del video. Intenta con otro.")
                    return

                # Si es solo audio, reproduce el audio del video, de lo contrario abre el video en YouTube
                if modo_audio:
                    self.voz.hablar("Reproduciendo solo el audio.")
                    self.reproducir_audio(video_url)
                else:
                    webbrowser.open(video_url)
                    self.voz.hablar("Reproduciendo en YouTube.")
                return  # Éxito, salimos del método
            else:
                # Si el número es inválido, avisa al usuario
                self.voz.hablar("Número inválido.")

        # Si no se entendió la elección después de varios intentos, avisa al usuario
        self.voz.hablar("No se entendió tu elección. Intenta nuevamente más tarde.")

    def buscar_videos(self, query):
    # Configura las opciones de yt-dlp para buscar videos en YouTube
        ydl_opts = {
            'quiet': True,  # Desactiva la salida de texto detallada (para que no imprima información extra)
            'extract_flat': False,  # No extrae solo la información sin descargar (queremos los videos completos)
            'dump_single_json': True,  # Obtiene la información del primer video en formato JSON
            'skip_download': True,  # No descarga el video, solo busca y extrae información
        }
        # Usa yt-dlp para obtener la información de los videos relacionados con la consulta
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)  # Realiza la búsqueda en YouTube
            return info.get('entries', [])  # Devuelve las entradas (videos) encontrados en el resultado de la búsqueda

    def reproducir_audio(self, url):
        # Configura las opciones para descargar y reproducir solo el audio
        ydl_opts = {
            'format': 'bestaudio/best',  # Selecciona el mejor formato de audio disponible
            'quiet': True,  # Desactiva la salida detallada de información
            'outtmpl': os.path.join(tempfile.gettempdir(), 'audio.%(ext)s'),  # Define la plantilla de nombre del archivo de salida
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Usa FFmpeg para extraer solo el audio
                'preferredcodec': 'mp3',  # El formato de audio preferido es mp3
                'preferredquality': '192',  # Define la calidad del audio (192 kbps)
            }],
        }

        # Usa yt-dlp para extraer solo el audio y guardarlo temporalmente
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = os.path.join(tempfile.gettempdir(), 'audio.mp3')

            # Si el archivo de audio fue descargado, reproduce el audio
            if os.path.exists(audio_path):
                if not pygame.mixer.get_init():
                    pygame.mixer.init()  # Inicializa el mezclador de pygame si no está inicializado
                pygame.mixer.music.load(audio_path)  # Carga el archivo de audio
                pygame.mixer.music.play()  # Reproduce el audio
                self.reproduciendo = True  # Marca que se está reproduciendo audio
                self.voz.hablar("Reproduciendo audio. Di 'detener' o 'para' para detenerlo.")

                try:
                    # Mantiene la reproducción hasta que el usuario indique detener
                    while pygame.mixer.music.get_busy():
                        comando = self.voz.escuchar_con_reintentos()
                        if comando and any(p in comando for p in ["detener", "para", "parar", "finaliza"]):
                            self.detener()  # Detiene la reproducción si se dice el comando adecuado
                            break
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    self.detener()
                finally:
                    # Elimina el archivo temporal después de la reproducción
                    if os.path.exists(audio_path):
                        time.sleep(0.5)
                        os.remove(audio_path)
            else:
                self.voz.hablar("No se pudo reproducir el audio.")

    def detener(self):
        # Detiene la reproducción de audio si está en curso
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()  # Detiene el audio
            pygame.mixer.quit()  # Cierra el mezclador de pygame
            self.reproduciendo = False  # Marca que no se está reproduciendo audio
            self.voz.hablar("Audio detenido.")

    def formatear_duracion(self, segundos):
        # Convierte la duración de segundos en un formato legible (minutos y segundos)
        if segundos is None:
            return "desconocida"
        minutos, seg = divmod(segundos, 60)
        return f"{minutos} minutos y {seg} segundos" if minutos else f"{seg} segundos"

    def _convertir_a_numero(self, texto):
        texto = texto.strip().lower()

        # ✅ Detecta números explícitos del 1 al 3 en el texto
        numero_directo = re.search(r"\b([1-3])\b", texto)
        if numero_directo:
            return int(numero_directo.group(1))

        # ✅ Palabras reconocibles
        mapa = {
            "uno": 1, "primer": 1, "primero": 1, "el uno": 1, "número uno": 1, "video uno": 1, "vídeo uno": 1,
            "dos": 2, "segundo": 2, "el dos": 2, "número dos": 2, "video dos": 2, "vídeo dos": 2,
            "tres": 3, "tercero": 3, "el tres": 3, "número tres": 3, "video tres": 3, "vídeo tres": 3,
        }

        for clave, valor in mapa.items():
            if clave in texto:
                return valor

        return -1  # No se encontró número válido
