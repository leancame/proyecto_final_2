# Importa la clase base que deben seguir todos los comandos
from .base import BaseComando
# Importa la función para obtener una sesión de la base de datos y la clase Tarea para trabajar con ellas
from asistente.servicios.db import obtener_sesion, Tarea
# Importa la función para crear eventos en Google Calendar
from asistente.servicios.google_calendar import crear_evento_google_calendar
# Importa las clases necesarias para trabajar con fechas y horas
from datetime import datetime, timedelta
import re

# Comando para añadir una tarea normal (sin fecha)
class ComandoTareaNormal(BaseComando):
    def activar(self, comando):
        # Activa el comando si se menciona "tarea normal" en el comando
        return "tarea normal" in comando

    def ejecutar(self, comando):
        # Extrae la descripción de la tarea eliminando "tarea normal" del comando
        tarea = comando.replace("tarea normal", "").strip()

        if not tarea:
            # Si no se especificó ninguna tarea, pregunta por ella
            self.voz.hablar("¿Qué tarea quieres añadir?")
            tarea = self.voz.escuchar()

        if tarea:
            # Crea una nueva tarea en la base de datos sin fecha
            session = obtener_sesion()
            nueva_tarea = Tarea(descripcion=tarea, es_concreta=False)
            session.add(nueva_tarea)
            session.commit()  # Guarda la tarea en la base de datos
            self.voz.hablar(f"Tarea normal añadida: {tarea}")  # Informa al usuario
        else:
            self.voz.hablar("No entendí la tarea. Intenta de nuevo.")  # Si no se reconoce la tarea

# Comando para añadir una tarea concreta (con fecha)
class ComandoTareaConcreta(BaseComando):
    def activar(self, comando):
        # Activa el comando si se menciona "tarea concreta" en el comando
        return "tarea concreta" in comando

    def ejecutar(self, comando):
        # Extrae la descripción de la tarea, eliminando "tarea concreta"
        tarea = comando.replace("tarea concreta", "").strip()

        if not tarea:
            # Si no se especificó ninguna tarea concreta, pregunta por ella
            self.voz.hablar("¿Qué tarea concreta quieres añadir? Puedes decir algo como 'tomar pastilla el 22 de abril a las 15:00'")
            tarea = self.voz.escuchar()

        # Extrae la fecha y la descripción de la tarea
        fecha = self._obtener_fecha_de_comando(tarea)
        descripcion = tarea.split(" a las")[0].strip()

        if descripcion and fecha:
            # Crea una nueva tarea concreta en la base de datos con la fecha
            session = obtener_sesion()
            nueva_tarea = Tarea(descripcion=descripcion, es_concreta=True, fecha=fecha)
            session.add(nueva_tarea)
            session.commit()  # Guarda la tarea en la base de datos

            # Crea un evento en Google Calendar
            crear_evento_google_calendar(descripcion, fecha)

            # Informa al usuario sobre la tarea añadida
            self.voz.hablar(f"Tarea concreta añadida: {descripcion} para el {fecha.strftime('%d/%m/%Y %H:%M')}")
        else:
            # Si no se entiende bien la tarea, informa al usuario
            self.voz.hablar("No entendí bien la tarea concreta. Por favor, repite.")

    def _obtener_fecha_de_comando(self, comando):
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
            'noviembre': 11, 'diciembre': 12
        }

        comando = comando.lower()

        try:
            # Manejo de fechas relativas
            if "pasado mañana" in comando:
                return datetime.now() + timedelta(days=2)
            elif "mañana" in comando:
                return datetime.now() + timedelta(days=1)
            elif match := re.search(r"en (\d+) día", comando):
                dias = int(match.group(1))
                return datetime.now() + timedelta(days=dias)

            # Fecha exacta: "el 9 de mayo a las 21:25"
            match = re.search(r"(\d{1,2}) de (\w+) a las (\d{1,2}):(\d{2})", comando)
            if match:
                dia, mes_texto, hora, minuto = match.groups()
                mes = meses.get(mes_texto)
                if mes:
                    año = datetime.now().year
                    return datetime(año, mes, int(dia), int(hora), int(minuto))

        except Exception as e:
            print(f"Error al interpretar la fecha: {e}")

        return None

# Comando para listar las tareas pendientes
class ComandoListarTareas(BaseComando):
    def activar(self, comando):
        # Activa el comando si se menciona "mostrar tareas" o "ver tareas"
        return "mostrar tareas" in comando or "ver tareas" in comando

    def ejecutar(self, comando):
        # Consulta todas las tareas pendientes en la base de datos
        session = obtener_sesion()
        tareas = session.query(Tarea).filter_by(completada=False).all()
        if tareas:
            self.voz.hablar(f"Tienes {len(tareas)} tareas pendientes.")
            for tarea in tareas:
                desc = tarea.descripcion
                if tarea.es_concreta and tarea.fecha:
                    self.voz.hablar(f"{desc} para el {tarea.fecha.strftime('%d/%m/%Y %H:%M')}")
                else:
                    self.voz.hablar(desc)
        else:
            self.voz.hablar("No tienes tareas pendientes.")  # Si no hay tareas pendientes

# Comando para completar una tarea pendiente
class ComandoCompletarTarea(BaseComando):
    def activar(self, comando):
        # Activa el comando si se menciona "completar tarea"
        return "completar tarea" in comando

    def ejecutar(self, comando):
        # Extrae la descripción de la tarea a completar
        tarea_desc = comando.replace("completar tarea", "").strip()

        if not tarea_desc:
            # Si no se especifica la tarea, pregunta al usuario
            self.voz.hablar("¿Qué tarea quieres marcar como completada?")
            tarea_desc = self.voz.escuchar()

        # Busca la tarea pendiente por descripción en la base de datos
        session = obtener_sesion()
        tarea = session.query(Tarea).filter(
            Tarea.descripcion.ilike(f"%{tarea_desc}%"),
            Tarea.completada == False
        ).first()

        if tarea:
            tarea.completada = True  # Marca la tarea como completada
            session.commit()  # Guarda los cambios en la base de datos
            self.voz.hablar(f"Tarea completada: {tarea.descripcion}")  # Informa al usuario
        else:
            self.voz.hablar("No encontré esa tarea pendiente.")  # Si no encuentra la tarea

# Comando para eliminar una tarea
class ComandoEliminarTarea(BaseComando):
    def activar(self, comando):
        # Activa el comando si se menciona "eliminar tarea" o "borrar tarea"
        return "eliminar tarea" in comando or "borrar tarea" in comando

    def ejecutar(self, comando):
        # Extrae la descripción de la tarea a eliminar
        tarea_desc = comando.replace("eliminar tarea", "").replace("borrar tarea", "").strip()

        if not tarea_desc:
            # Si no se especifica la tarea, pregunta al usuario
            self.voz.hablar("¿Qué tarea quieres eliminar?")
            tarea_desc = self.voz.escuchar()

        # Busca la tarea por descripción en la base de datos
        session = obtener_sesion()
        tarea = session.query(Tarea).filter(
            Tarea.descripcion.ilike(f"%{tarea_desc}%")
        ).first()

        if tarea:
            session.delete(tarea)  # Elimina la tarea de la base de datos
            session.commit()  # Guarda los cambios
            self.voz.hablar(f"Tarea eliminada: {tarea.descripcion}")  # Informa al usuario
        else:
            self.voz.hablar("No encontré esa tarea.")  # Si no se encuentra la tarea
