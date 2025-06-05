from .db import Tarea, obtener_sesion
from datetime import datetime

def crear_tarea(descripcion: str, es_concreta: bool = False, fecha: datetime = None):
    session = obtener_sesion()
    try:
        nueva_tarea = Tarea(descripcion=descripcion, es_concreta=es_concreta, fecha=fecha)
        session.add(nueva_tarea)
        session.commit()
        session.refresh(nueva_tarea)
        return nueva_tarea
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Error al crear la tarea: {e}")
    finally:
        session.close()

def obtener_tareas():
    session = obtener_sesion()
    try:
        tareas = session.query(Tarea).all()
        return tareas
    except Exception as e:
        raise RuntimeError(f"Error al obtener tareas: {e}")
    finally:
        session.close()

def obtener_tareas_concretas():
    session = obtener_sesion()
    try:
        tareas_concretas = session.query(Tarea).filter(Tarea.es_concreta == True).all()
        return tareas_concretas
    except Exception as e:
        raise RuntimeError(f"Error al obtener tareas concretas: {e}")
    finally:
        session.close()

def completar_tarea(tarea_id: int):
    session = obtener_sesion()
    try:
        tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()
        if tarea:
            tarea.completada = True
            session.commit()
            session.refresh(tarea)
            return tarea
        return None
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Error al completar tarea: {e}")
    finally:
        session.close()

def eliminar_tarea(tarea_id: int):
    session = obtener_sesion()
    try:
        tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()
        if tarea:
            session.delete(tarea)
            session.commit()
            return tarea
        return None
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Error al eliminar tarea: {e}")
    finally:
        session.close()
