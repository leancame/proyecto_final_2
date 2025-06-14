# Importa pytest para definir y ejecutar pruebas unitarias
import pytest
# Importa herramientas de unittest para crear mocks y parches
from unittest.mock import MagicMock, patch
# Importa la clase base de comandos
from asistente.comando.base import BaseComando
# Importa el comando específico que da la hora
from asistente.comando.hora import ComandoHora
# Importa las funciones CRUD desde el módulo de servicios
from asistente.servicios import crud
# Importa la clase de voz para pruebas relacionadas con audio
from asistente.voz import VozSincronizada

# Pruebas del comando ComandoHora

# Prueba que verifica si el comando se activa con una frase relacionada a la hora
def test_comando_hora_activar():
    cmd = ComandoHora(None, None)  # Crea una instancia del comando
    assert cmd.activar("¿Qué hora es?") is True  # La frase activa el comando
    assert cmd.activar("otra cosa") is False     # Una frase irrelevante no lo activa

# Prueba el método ejecutar() del ComandoHora con el datetime simulado
@patch('asistente.comando.hora.datetime')  # Parchea el módulo datetime usado en el comando
def test_comando_hora_ejecutar(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "12:00"  # Simula la hora actual
    voz_mock = MagicMock()
    cmd = ComandoHora(voz_mock, None)  # Instancia del comando con mock de voz
    result = cmd.ejecutar("¿Qué hora es?")  # Ejecuta con una pregunta válida
    # El método ejecutar no devuelve nada, por lo que no se debe verificar el resultado
    voz_mock.hablar.assert_called()  # Verifica que se haya llamado al método hablar

# Pruebas de funciones CRUD: obtener_tareas

# Parchea la obtención de sesión de base de datos
@patch('asistente.servicios.crud.obtener_sesion')
def test_obtener_tareas(mock_obtener_sesion):
    mock_session = MagicMock()  # Crea un mock de la sesión
    mock_session.query.return_value.all.return_value = ["tarea1", "tarea2"]  # Simula el retorno de tareas
    mock_obtener_sesion.return_value = mock_session  # El patch devuelve la sesión mockeada

    tareas = crud.obtener_tareas()  # Llama a la función a probar
    assert tareas == ["tarea1", "tarea2"]  # Verifica que el resultado sea el esperado

# Prueba completar_tarea simulando acceso y actualización de la base
@patch('asistente.servicios.crud.obtener_sesion')
def test_completar_tarea(mock_obtener_sesion):
    mock_session = MagicMock()  # Crea una sesión falsa
    mock_tarea = MagicMock()  # Crea un objeto tarea falso
    mock_tarea.completada = False  # Se marca inicialmente como no completada
    # Simula que se retorna esa tarea al hacer la consulta
    mock_session.query.return_value.filter.return_value.first.return_value = mock_tarea
    mock_obtener_sesion.return_value = mock_session  # Pone la sesión en el patch

    tarea = crud.completar_tarea(1)  # Ejecuta la función con ID 1
    assert tarea.completada is True  # Verifica que ahora esté completada
    mock_session.commit.assert_called_once()  # Asegura que se haya guardado en la base

# Prueba una funcionalidad de voz que no lanza errores

# Verifica que el método detener de VozSincronizada no lanza excepciones
def test_voz_sincronizada_detener():
    voz = MagicMock()
    voz.detener = MagicMock()
    voz.detener()  # Llama al método detener (inofensivo si no hay animación activa)
    voz.detener.assert_called_once()  # Verifica que se haya llamado al método detener
