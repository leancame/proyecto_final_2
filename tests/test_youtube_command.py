import pytest
from unittest.mock import MagicMock, patch
from asistente.comando.youtube import ComandoYouTube

def test_activar():
    cmd = ComandoYouTube(None, None)
    assert cmd.activar("buscar en youtube algo") is True
    assert cmd.activar("reproducir en youtube algo") is True
    assert cmd.activar("otra cosa") is False

@patch('asistente.comando.youtube.webbrowser.open')
@patch('asistente.comando.youtube.time.sleep', return_value=None)
def test_ejecutar_cancelacion(mock_sleep, mock_web_open):
    voz_mock = MagicMock()
    voz_mock.escuchar_con_reintentos.side_effect = ["cancelar"]
    cmd = ComandoYouTube(voz_mock, None)
    cmd.buscar_videos = MagicMock(return_value=[{'title': 'Video1', 'uploader': 'Canal1', 'duration': 120, 'webpage_url': 'url1'}])
    cmd.ejecutar("buscar en youtube test")
    voz_mock.hablar.assert_any_call("Cancelado.")
    mock_web_open.assert_not_called()

@patch('asistente.comando.youtube.webbrowser.open')
@patch('asistente.comando.youtube.time.sleep', return_value=None)
def test_ejecutar_reproducir_video(mock_sleep, mock_web_open):
    voz_mock = MagicMock()
    voz_mock.escuchar_con_reintentos.side_effect = ["1"]
    cmd = ComandoYouTube(voz_mock, None)
    videos = [
        {'title': 'Video1', 'uploader': 'Canal1', 'duration': 120, 'webpage_url': 'url1'},
        {'title': 'Video2', 'uploader': 'Canal2', 'duration': 150, 'webpage_url': 'url2'}
    ]
    cmd.buscar_videos = MagicMock(return_value=videos)
    cmd.reproducir_audio = MagicMock()
    cmd.ejecutar("buscar en youtube test")
    voz_mock.hablar.assert_any_call("Buscando test en YouTube...")
    mock_web_open.assert_called_once_with('url1')
    cmd.reproducir_audio.assert_not_called()

@patch('asistente.comando.youtube.webbrowser.open')
@patch('asistente.comando.youtube.time.sleep', return_value=None)
def test_ejecutar_reproducir_audio(mock_sleep, mock_web_open):
    voz_mock = MagicMock()
    voz_mock.escuchar_con_reintentos.side_effect = ["audio 1"]
    cmd = ComandoYouTube(voz_mock, None)
    videos = [
        {'title': 'Video1', 'uploader': 'Canal1', 'duration': 120, 'webpage_url': 'url1'},
    ]
    cmd.buscar_videos = MagicMock(return_value=videos)
    cmd.reproducir_audio = MagicMock()
    cmd.ejecutar("reproducir en youtube solo audio test")
    voz_mock.hablar.assert_any_call("Buscando solo audio test en YouTube...")
    cmd.reproducir_audio.assert_called_once_with('url1')
    mock_web_open.assert_not_called()
