# Importa la clase Tarea y la función obtener_sesion desde el módulo db local
from .db import Tarea, obtener_sesion
# Importa la clase datetime para manejar fechas y horas
from datetime import datetime

# Función para crear una tarea nueva, recibe descripción, si es concreta y fecha opcional
def crear_tarea(descripcion: str, es_concreta: bool = False, fecha: datetime = None):
    session = obtener_sesion()  # Obtiene la sesión de base de datos
    try:
        # Crea una instancia de Tarea con los datos recibidos
        nueva_tarea = Tarea(descripcion=descripcion, es_concreta=es_concreta, fecha=fecha)
        session.add(nueva_tarea)  # Añade la nueva tarea a la sesión
        session.commit()  # Guarda los cambios en la base de datos
        session.refresh(nueva_tarea)  # Refresca la instancia para actualizar datos desde BD
        return nueva_tarea  # Devuelve la tarea creada
    except Exception as e:
        session.rollback()  # Revertir cambios si hay error
        raise RuntimeError(f"Error al crear la tarea: {e}")  # Lanza error específico
    finally:
        session.close()  # Cierra la sesión en cualquier caso

# Función para obtener todas las tareas en la base de datos
def obtener_tareas():
    session = obtener_sesion()  # Obtiene la sesión de base de datos
    try:
        tareas = session.query(Tarea).all()  # Consulta todas las tareas
        return tareas  # Devuelve la lista de tareas
    except Exception as e:
        raise RuntimeError(f"Error al obtener tareas: {e}")  # Lanza error específico
    finally:
        session.close()  # Cierra la sesión

# Función para obtener sólo las tareas concretas (es_concreta == True)
def obtener_tareas_concretas():
    session = obtener_sesion()  # Obtiene la sesión de base de datos
    try:
        tareas_concretas = session.query(Tarea).filter(Tarea.es_concreta == True).all()  # Consulta tareas concretas
        return tareas_concretas  # Devuelve la lista de tareas concretas
    except Exception as e:
        raise RuntimeError(f"Error al obtener tareas concretas: {e}")  # Lanza error específico
    finally:
        session.close()  # Cierra la sesión

# Función para marcar una tarea como completada dado su ID
def completar_tarea(tarea_id: int):
    session = obtener_sesion()  # Obtiene la sesión de base de datos
    try:
        tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()  # Busca la tarea por ID
        if tarea:
            tarea.completada = True  # Marca como completada
            session.commit()  # Guarda cambios
            session.refresh(tarea)  # Refresca la instancia para actualizar datos
            return tarea  # Devuelve la tarea actualizada
        return None  # Si no existe la tarea, devuelve None
    except Exception as e:
        session.rollback()  # Revertir cambios si hay error
        raise RuntimeError(f"Error al completar tarea: {e}")  # Lanza error específico
    finally:
        session.close()  # Cierra la sesión

# Función para eliminar una tarea dado su ID
def eliminar_tarea(tarea_id: int):
    session = obtener_sesion()  # Obtiene la sesión de base de datos
    try:
        tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()  # Busca la tarea por ID
        if tarea:
            session.delete(tarea)  # Elimina la tarea de la sesión
            session.commit()  # Guarda cambios
            return tarea  # Devuelve la tarea eliminada
        return None  # Si no existe la tarea, devuelve None
    except Exception as e:
        session.rollback()  # Revertir cambios si hay error
        raise RuntimeError(f"Error al eliminar tarea: {e}")  # Lanza error específico
    finally:
        session.close()  # Cierra la sesión
