import pytest
from unittest.mock import MagicMock, patch
from asistente.comando.base import BaseComando
from asistente.servicios import crud
from asistente.ia.big_model import BigModel

# Ejemplo 1: Prueba para BaseComando - verificar NotImplementedError
class TestBaseComando(BaseComando):
    pass

def test_activar_not_implemented():
    cmd = TestBaseComando(None, None)
    with pytest.raises(NotImplementedError):
        cmd.activar("comando")

def test_ejecutar_not_implemented():
    cmd = TestBaseComando(None, None)
    with pytest.raises(NotImplementedError):
        cmd.ejecutar("comando")

# Ejemplo 2: Prueba para función crear_tarea con mock de sesión
@patch('asistente.servicios.crud.obtener_sesion')
def test_crear_tarea_success(mock_obtener_sesion):
    mock_session = MagicMock()
    mock_obtener_sesion.return_value = mock_session
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    mock_session.close.return_value = None

    tarea = crud.crear_tarea("Test tarea", False, None)
    assert tarea is not None
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    mock_session.close.assert_called_once()

# Ejemplo 3: Prueba para BigModel - simular carga y respuesta del modelo
@patch('asistente.ia.big_model.Llama')
def test_big_model_responder(mock_llama_class):
    mock_llama = MagicMock()
    mock_llama.return_value = {"choices": [{"text": "respuesta"}]}
    mock_llama_class.return_value = mock_llama

    model = BigModel()
    response = model.responder("Hola")
    assert response == "respuesta"
