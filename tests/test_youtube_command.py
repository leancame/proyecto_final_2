# Importa la biblioteca de pruebas pytest
import pytest
# Importa herramientas para simular objetos y funciones desde unittest.mock
from unittest.mock import MagicMock, patch
# Importa la clase ComandoYouTube que será probada
from asistente.comando.youtube import ComandoYouTube

# Prueba unitaria para verificar que el comando se activa correctamente con frases específicas
def test_activar():
    # Crea una instancia del comando con None como argumentos simulados
    cmd = ComandoYouTube(None, None)
    # Verifica que se activa con "buscar en youtube algo"
    assert cmd.activar("buscar en youtube algo") is True
    # Verifica que se activa con "reproducir en youtube algo"
    assert cmd.activar("reproducir en youtube algo") is True
    # Verifica que no se activa con una frase que no corresponde
    assert cmd.activar("otra cosa") is False

# Parchea la función webbrowser.open para evitar que se abra el navegador durante la prueba
@patch('asistente.comando.youtube.webbrowser.open')
# Parchea la función time.sleep para que no retrase la ejecución durante la prueba
@patch('asistente.comando.youtube.time.sleep', return_value=None)
def test_ejecutar_cancelacion(mock_sleep, mock_web_open):
    # Crea un objeto simulado para la voz
    voz_mock = MagicMock()
    # Configura el reconocimiento de voz para simular que el usuario dice "cancelar"
    voz_mock.escuchar_con_reintentos.side_effect = ["cancelar"]
    # Crea una instancia del comando con el mock de voz
    cmd = ComandoYouTube(voz_mock, None)
    # Simula la búsqueda de un video retornando una lista con un video
    cmd.buscar_videos = MagicMock(return_value=[{'title': 'Video1', 'uploader': 'Canal1', 'duration': 120, 'webpage_url': 'url1'}])
    # Ejecuta el comando con una frase de búsqueda
    cmd.ejecutar("buscar en youtube test")
    # Verifica que el asistente diga "Cancelado."
    voz_mock.hablar.assert_any_call("Cancelado.")
    # Verifica que NO se haya abierto el navegador
    mock_web_open.assert_not_called()

# Parchea webbrowser.open y time.sleep como antes
@patch('asistente.comando.youtube.webbrowser.open')
@patch('asistente.comando.youtube.time.sleep', return_value=None)
def test_ejecutar_reproducir_video(mock_sleep, mock_web_open):
    # Crea el mock de voz
    voz_mock = MagicMock()
    # Simula que el usuario dice "1" como selección del video
    voz_mock.escuchar_con_reintentos.side_effect = ["1"]
    # Crea una instancia del comando
    cmd = ComandoYouTube(voz_mock, None)
    # Lista simulada de videos encontrados
    videos = [
        {'title': 'Video1', 'uploader': 'Canal1', 'duration': 120, 'webpage_url': 'url1'},
        {'title': 'Video2', 'uploader': 'Canal2', 'duration': 150, 'webpage_url': 'url2'}
    ]
    # Simula la búsqueda devolviendo los videos
    cmd.buscar_videos = MagicMock(return_value=videos)
    # Simula la función de reproducir solo audio
    cmd.reproducir_audio = MagicMock()
    # Ejecuta el comando con frase de búsqueda
    cmd.ejecutar("buscar en youtube test")
    # Verifica que el asistente diga que está buscando
    voz_mock.hablar.assert_any_call("Buscando test en YouTube...")
    # Verifica que se abrió el navegador con la URL del primer video
    mock_web_open.assert_called_once_with('url1')
    # Verifica que NO se haya llamado a reproducir_audio (porque es reproducción normal)
    cmd.reproducir_audio.assert_not_called()

# Parchea nuevamente webbrowser.open y time.sleep
@patch('asistente.comando.youtube.webbrowser.open')
@patch('asistente.comando.youtube.time.sleep', return_value=None)
def test_ejecutar_reproducir_audio(mock_sleep, mock_web_open):
    # Crea el mock de voz
    voz_mock = MagicMock()
    # Simula que el usuario dice "audio 1" (indica que quiere solo audio del video 1)
    voz_mock.escuchar_con_reintentos.side_effect = ["audio 1"]
    # Crea una instancia del comando
    cmd = ComandoYouTube(voz_mock, None)
    # Simula la búsqueda devolviendo un video
    videos = [
        {'title': 'Video1', 'uploader': 'Canal1', 'duration': 120, 'webpage_url': 'url1'},
    ]
    # Mockea la búsqueda de videos
    cmd.buscar_videos = MagicMock(return_value=videos)
    # Mockea la función de reproducir solo audio
    cmd.reproducir_audio = MagicMock()
    # Ejecuta el comando con frase para reproducir solo audio
    cmd.ejecutar("reproducir en youtube solo audio test")
    # Verifica que diga que está buscando solo audio
    voz_mock.hablar.assert_any_call("Buscando solo audio test en YouTube...")
    # Verifica que se llamó a reproducir_audio con la URL correspondiente
    cmd.reproducir_audio.assert_called_once_with('url1')
    # Verifica que NO se haya abierto el navegador
    mock_web_open.assert_not_called()
