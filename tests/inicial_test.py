# Importa pytest para escribir y ejecutar pruebas
import pytest
# Importa MagicMock y patch para simular objetos y funciones
from unittest.mock import MagicMock, patch
# Importa la clase base de comandos para probar métodos abstractos
from asistente.comando.base import BaseComando
# Importa el módulo CRUD para operar con la base de datos
from asistente.servicios import crud
# Importa la clase del modelo de IA para simular su comportamiento
from asistente.ia.big_model import BigModel

# Ejemplo 1: Prueba de BaseComando para asegurar que lanza NotImplementedError si no se implementan los métodos

# Se crea una clase de prueba que hereda de BaseComando pero no implementa sus métodos
class TestBaseComando(BaseComando):
    pass

# Prueba que el método activar() lanza NotImplementedError
def test_activar_not_implemented():
    cmd = TestBaseComando(None, None)  # Se crea una instancia con argumentos None
    with pytest.raises(NotImplementedError):  # Se espera que este error se lance
        cmd.activar("comando")  # Se llama al método que no fue implementado

# Prueba que el método ejecutar() lanza NotImplementedError
def test_ejecutar_not_implemented():
    cmd = TestBaseComando(None, None)  # Instancia de la clase no implementada
    with pytest.raises(NotImplementedError):  # Se espera el error
        cmd.ejecutar("comando")  # Llamada al método sin implementación

# Ejemplo 2: Prueba unitaria para crear_tarea utilizando mocks para la sesión de base de datos

# Se parchea la función obtener_sesion para que devuelva un objeto simulado
@patch('asistente.servicios.crud.obtener_sesion')
def test_crear_tarea_success(mock_obtener_sesion):
    mock_session = MagicMock()  # Se crea un mock de la sesión
    mock_obtener_sesion.return_value = mock_session  # Se hace que obtener_sesion devuelva el mock
    mock_session.add.return_value = None  # Configura el mock para add
    mock_session.commit.return_value = None  # Configura el mock para commit
    mock_session.refresh.return_value = None  # Configura el mock para refresh
    mock_session.close.return_value = None  # Configura el mock para close

    # Se llama a la función crear_tarea, que debería funcionar con la sesión simulada
    tarea = crud.crear_tarea("Test tarea", False, None)
    assert tarea is not None  # Verifica que se devuelva una tarea

    # Verifica que cada método fue llamado una vez en la sesión simulada
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    mock_session.close.assert_called_once()

# Ejemplo 3: Prueba para BigModel - simula la carga del modelo y su respuesta

# Se parchea la clase Llama del módulo big_model para reemplazarla por un mock
@patch('asistente.ia.big_model.Llama')
def test_big_model_responder(mock_llama_class):
    mock_llama = MagicMock()  # Crea un objeto mock para simular el modelo
    mock_llama.return_value = {"choices": [{"text": "respuesta"}]}  # Define lo que debe retornar el modelo simulado
    mock_llama_class.return_value = mock_llama  # Llama a la clase simulada

    model = BigModel()  # Crea una instancia de BigModel que usará el mock
    response = model.responder("Hola")  # Llama al método responder
    assert response == "respuesta"  # Verifica que la respuesta sea la esperada
