# Importa funciones y clases necesarias de SQLAlchemy para manejar la base de datos
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Importa datetime para manejar fechas
from datetime import datetime

# Crea una clase base para declarar modelos con SQLAlchemy ORM
Base = declarative_base()

# Define el modelo Tarea que representa la tabla 'tareas' en la base de datos
class Tarea(Base):
    __tablename__ = 'tareas'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True)  # Columna ID, clave primaria auto-incremental
    descripcion = Column(String(255), nullable=False)  # Descripción, cadena de texto, no nula
    es_concreta = Column(Boolean, default=False)  # Campo booleano que indica si la tarea es concreta, por defecto False
    fecha = Column(DateTime, nullable=True)  # Fecha asociada, puede ser nula
    completada = Column(Boolean, default=False)  # Estado de completado, booleano, por defecto False

    # Método para mostrar una representación legible del objeto Tarea
    def __repr__(self):
        return (f"Tarea(id={self.id}, descripcion={self.descripcion}, "
                f"es_concreta={self.es_concreta}, fecha={self.fecha}, completada={self.completada})")

# Función para obtener una sesión de conexión a la base de datos
def obtener_sesion():
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    try:
        # Primero, crear un engine sin base de datos para crear la base de datos si no existe
        engine_sin_db = create_engine('mysql+mysqlconnector://root:@localhost/')
        with engine_sin_db.connect() as conn:
            conn.execute(text("CREATE DATABASE IF NOT EXISTS tareas_db"))
        engine_sin_db.dispose()

        # Ahora crear el engine con la base de datos ya creada
        engine = create_engine('mysql+mysqlconnector://root:@localhost/tareas_db')
        Base.metadata.create_all(engine)  # Crea las tablas en la base de datos si no existen
        Session = sessionmaker(bind=engine)  # Crea la clase para sesiones vinculada al motor
        return Session()  # Devuelve una instancia de sesión para operar con la BD
    except SQLAlchemyError as e:
        # Si ocurre un error, lanza un RuntimeError con el mensaje correspondiente
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")
