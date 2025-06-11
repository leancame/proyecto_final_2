import pytest
from unittest.mock import MagicMock, patch
from asistente.comando.base import BaseComando
from asistente.comando.hora import ComandoHora
from asistente.servicios import crud
from asistente.voz import VozSincronizada

# Pruebas para un comando específico: ComandoHora
def test_comando_hora_activar():
    cmd = ComandoHora(None, None)
    assert cmd.activar("¿Qué hora es?") is True
    assert cmd.activar("otra cosa") is False

@patch('asistente.comando.hora.datetime')
def test_comando_hora_ejecutar(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "12:00"
    cmd = ComandoHora(None, None)
    # Aquí se podría probar que cmd.ejecutar devuelve o llama a la función esperada
    # Como ejemplo simple:
    result = cmd.ejecutar("¿Qué hora es?")
    assert result is not None

# Pruebas para otras funciones CRUD
@patch('asistente.servicios.crud.obtener_sesion')
def test_obtener_tareas(mock_obtener_sesion):
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = ["tarea1", "tarea2"]
    mock_obtener_sesion.return_value = mock_session

    tareas = crud.obtener_tareas()
    assert tareas == ["tarea1", "tarea2"]

@patch('asistente.servicios.crud.obtener_sesion')
def test_completar_tarea(mock_obtener_sesion):
    mock_session = MagicMock()
    mock_tarea = MagicMock()
    mock_tarea.completada = False
    mock_session.query.return_value.filter.return_value.first.return_value = mock_tarea
    mock_obtener_sesion.return_value = mock_session

    tarea = crud.completar_tarea(1)
    assert tarea.completada is True
    mock_session.commit.assert_called_once()

# Pruebas para funcionalidades de voz
def test_voz_sincronizada_detener():
    voz = VozSincronizada()
    # Se puede probar que el método detener no lanza errores
    voz.detener()
