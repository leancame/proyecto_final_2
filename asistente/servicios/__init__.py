# Módulo de servicios para la base de datos con selección de entorno

import os

ENTORNO = os.getenv('ENTORNO', 'local')

if ENTORNO == 'docker':
    from .db_docker import obtener_sesion
else:
    from .db import obtener_sesion
