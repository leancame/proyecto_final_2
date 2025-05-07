# Importa el modelo Tarea y la función para obtener una sesión de base de datos desde el módulo db
from .db import Tarea, obtener_sesion
# Importa el tipo datetime para manejar fechas
from datetime import datetime

# Función para crear una nueva tarea
def crear_tarea(descripcion: str, es_concreta: bool = False, fecha: datetime = None):
    session = obtener_sesion()  # Obtiene una nueva sesión de base de datos
    # Crea una nueva instancia del modelo Tarea con los datos proporcionados
    nueva_tarea = Tarea(descripcion=descripcion, es_concreta=es_concreta, fecha=fecha)
    session.add(nueva_tarea)  # Agrega la nueva tarea a la sesión
    session.commit()  # Guarda los cambios en la base de datos
    session.refresh(nueva_tarea)  # Refresca el objeto para obtener su estado final desde la base de datos
    session.close()  # Cierra la sesión
    return nueva_tarea  # Retorna la tarea creada

# Función para obtener todas las tareas de la base de datos
def obtener_tareas():
    session = obtener_sesion()  # Abre una nueva sesión
    tareas = session.query(Tarea).all()  # Consulta todas las instancias de Tarea
    session.close()  # Cierra la sesión
    return tareas  # Devuelve la lista de tareas

# Función para obtener solo las tareas marcadas como concretas
def obtener_tareas_concretas():
    session = obtener_sesion()  # Inicia sesión de base de datos
    # Filtra las tareas donde es_concreta sea True
    tareas_concretas = session.query(Tarea).filter(Tarea.es_concreta == True).all()
    session.close()  # Cierra la sesión
    return tareas_concretas  # Retorna la lista de tareas concretas

# Función para marcar una tarea como completada usando su ID
def completar_tarea(tarea_id: int):
    session = obtener_sesion()  # Abre sesión
    # Busca la tarea por su ID
    tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()
    if tarea:  # Si se encuentra la tarea
        tarea.completada = True  # Marca como completada
        session.commit()  # Guarda cambios
        session.refresh(tarea)  # Refresca el objeto
        session.close()  # Cierra la sesión
        return tarea  # Devuelve la tarea actualizada
    session.close()  # Cierra la sesión si no se encontró la tarea
    return None  # Devuelve None si no se encontró la tarea

# Función para eliminar una tarea según su ID
def eliminar_tarea(tarea_id: int):
    session = obtener_sesion()  # Abre sesión
    # Busca la tarea por ID
    tarea = session.query(Tarea).filter(Tarea.id == tarea_id).first()
    if tarea:  # Si la tarea existe
        session.delete(tarea)  # Elimina la tarea de la sesión
        session.commit()  # Guarda los cambios en la base de datos
        session.close()  # Cierra la sesión
        return tarea  # Devuelve la tarea eliminada
    session.close()  # Cierra la sesión si no se encontró la tarea
    return None  # Retorna None si no se encontró la tarea

