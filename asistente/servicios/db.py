# Importa los componentes necesarios de SQLAlchemy para definir el modelo de datos y conectarse a la base de datos
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
# Importa la función para crear una clase base de la que heredan todos los modelos
from sqlalchemy.ext.declarative import declarative_base
# Importa el creador de sesiones para manejar transacciones con la base de datos
from sqlalchemy.orm import sessionmaker
# Importa el módulo datetime para trabajar con fechas y horas
from datetime import datetime

# Crea una clase base para los modelos usando el sistema de declarative de SQLAlchemy
Base = declarative_base()

# Define una clase que representa la tabla "tareas" en la base de datos
class Tarea(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = 'tareas'

    # Define las columnas de la tabla y sus tipos
    id = Column(Integer, primary_key=True)  # Columna ID, clave primaria
    descripcion = Column(String(255), nullable=False)  # Descripción de la tarea, no puede ser nula
    es_concreta = Column(Boolean, default=False)  # Indica si la tarea es concreta, por defecto es False
    fecha = Column(DateTime, nullable=True)  # Fecha de la tarea, puede ser nula
    completada = Column(Boolean, default=False)  # Estado de completitud de la tarea, por defecto es False

    # Método de representación en forma de string para facilitar la depuración y el log
    def __repr__(self):
        return f"Tarea(id={self.id}, descripcion={self.descripcion}, es_concreta={self.es_concreta}, fecha={self.fecha}, completada={self.completada})"

# Función para obtener una sesión de conexión a la base de datos
def obtener_sesion():
    # Crea un motor de conexión usando MySQL con el conector mysqlconnector
    engine = create_engine('mysql+mysqlconnector://root:@localhost/tareas_db')  
    # Crea todas las tablas definidas en Base si no existen
    Base.metadata.create_all(engine)
    # Crea una clase de sesión asociada al motor
    Session = sessionmaker(bind=engine)
    # Retorna una instancia de sesión para interactuar con la base de datos
    return Session()
