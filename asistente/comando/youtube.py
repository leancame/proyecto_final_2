import yt_dlp
import webbrowser
import os
import tempfile
import pygame
import time
import re
from .base import BaseComando

ffmpeg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ffmpeg/bin'))
os.environ["PATH"] += os.pathsep + ffmpeg_path

class ComandoYouTube(BaseComando):
    def __init__(self, voz, servicios):
        super().__init__(voz, servicios)
        self.reproduciendo = False

    def activar(self, comando):
        return "buscar en youtube" in comando or "reproducir en youtube" in comando

    def ejecutar(self, comando):
        solo_audio = "solo audio" in comando or "audio" in comando
        query = comando.replace("buscar en youtube", "").replace("reproducir en youtube", "").strip()

        if not query:
            self.voz.hablar("¿Qué deseas buscar en YouTube?")
            query = self.voz.escuchar_con_reintentos()
        if not query:
            self.voz.hablar("No entendí la búsqueda.")
            return

        self.voz.hablar(f"Buscando {query} en YouTube...")
        videos = self.buscar_videos(query)

        if not videos:
            self.voz.hablar("No encontré videos.")
            return

        # Leer las 3 opciones
        self.voz.hablar("Aquí tienes tres opciones:")
        for i, video in enumerate(videos[:3]):
            titulo = video.get('title', 'Sin título')
            canal = video.get('uploader', 'Canal desconocido')
            duracion = self.formatear_duracion(video.get('duration'))
            self.voz.hablar(f"{i + 1}. {titulo}, del canal {canal}, duración {duracion}")
            time.sleep(0.5)  # Pequeña pausa entre frases

        # Elegir una opción
        max_intentos = 3
        for intento in range(max_intentos):
            self.voz.hablar("Dime el número del video que quieres reproducir.")
            eleccion = self.voz.escuchar_con_reintentos(2)

            if not eleccion:
                self.voz.hablar("No te entendí, intenta de nuevo.")
                continue

            modo_audio = "audio" in eleccion or "solo audio" in eleccion
            eleccion = eleccion.replace("audio", "").replace("solo audio", "").strip()

            indice = self._convertir_a_numero(eleccion) - 1
            if 0 <= indice < len(videos):
                video_url = videos[indice].get('webpage_url')
                if not video_url:
                    self.voz.hablar("No se pudo obtener el enlace del video.")
                    return

                if modo_audio:
                    self.voz.hablar("Reproduciendo solo el audio.")
                    self.reproducir_audio(video_url)
                else:
                    webbrowser.open(video_url)
                    self.voz.hablar("Reproduciendo en YouTube.")
                return

            self.voz.hablar("Número inválido.")
        
        self.voz.hablar("No entendí tu elección. Intenta nuevamente más tarde.")

    def buscar_videos(self, query):
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,
            'dump_single_json': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            return info.get('entries', [])

    def reproducir_audio(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': os.path.join(tempfile.gettempdir(), 'audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = os.path.join(tempfile.gettempdir(), 'audio.mp3')

            if os.path.exists(audio_path):
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                self.reproduciendo = True
                self.voz.hablar("Reproduciendo audio. Di 'detener' para parar.")

                while pygame.mixer.music.get_busy():
                    comando = self.voz.escuchar_con_reintentos(1)
                    if comando and any(p in comando for p in ["detener", "para", "parar", "finaliza"]):
                        self.detener()
                        break
                    time.sleep(0.5)

                pygame.mixer.quit()
                self.reproduciendo = False
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            else:
                self.voz.hablar("No se pudo reproducir el audio.")

    def detener(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.voz.hablar("Audio detenido.")

    def formatear_duracion(self, segundos):
        if segundos is None:
            return "desconocida"
        minutos, seg = divmod(segundos, 60)
        return f"{minutos} minutos y {seg} segundos" if minutos else f"{seg} segundos"

    def _convertir_a_numero(self, texto):
        texto = texto.strip().lower()
        if re.search(r"\b1\b", texto): return 1
        if re.search(r"\b2\b", texto): return 2
        if re.search(r"\b3\b", texto): return 3
        mapa = {
            "uno": 1, "primero": 1, "el uno": 1,
            "dos": 2, "segundo": 2, "el dos": 2,
            "tres": 3, "tercero": 3, "el tres": 3
        }
        for palabra, num in mapa.items():
            if palabra in texto:
                return num
        return -1
