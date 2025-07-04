import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Tarea(Base):
    __tablename__ = 'tareas'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255), nullable=False)
    es_concreta = Column(Boolean, default=False)
    fecha = Column(DateTime, nullable=True)
    completada = Column(Boolean, default=False)

    def __repr__(self):
        return (f"Tarea(id={self.id}, descripcion={self.descripcion}, "
                f"es_concreta={self.es_concreta}, fecha={self.fecha}, completada={self.completada})")

def obtener_sesion():
    try:
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', 'proyectofinal')
        host = os.getenv('MYSQL_HOST', 'localhost')
        database = os.getenv('MYSQL_DATABASE', 'tareas_db')
        port = os.getenv('MYSQL_PORT', '3306')
        connection_string = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")
