# Importa la clase base para comandos
from .base import BaseComando
# Importa funciones y clases para manejar la base de datos y tareas
from asistente.servicios.db import obtener_sesion, Tarea
# Importa función para crear eventos en Google Calendar
from asistente.servicios.google_calendar import crear_evento_google_calendar
# Importa clases para manejo de fechas y tiempos
from datetime import datetime, timedelta
# Importa módulo para expresiones regulares
import re


# Función que devuelve la descripción de una tarea, incluyendo la fecha si es concreta
def descripcion_con_fecha(tarea):
    # Si la tarea es concreta y tiene fecha, devuelve descripción con fecha formateada
    if tarea.es_concreta and tarea.fecha:
        return f"{tarea.descripcion} para el {tarea.fecha.strftime('%d/%m/%Y %H:%M')}"
    # Si no, devuelve solo la descripción
    return tarea.descripcion


# Clase para manejar comandos de tareas normales (sin fecha concreta)
class ComandoTareaNormal(BaseComando):
    # Método para activar este comando si el texto contiene "tarea normal"
    def activar(self, comando):
        return "tarea normal" in comando

    # Método para ejecutar el comando
    def ejecutar(self, comando):
        try:
            # Extrae la descripción de la tarea quitando la parte "tarea normal"
            tarea = comando.replace("tarea normal", "").strip()
            # Si no se especifica tarea, pregunta al usuario hasta que responda o cancele
            while not tarea:
                self.voz.hablar("¿Qué tarea quieres añadir?")
                tarea = self.voz.escuchar()
                # Si el usuario dice cancelar, salir o finalizar, cancela la operación
                if tarea.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            # Obtiene la sesión de base de datos
            session = obtener_sesion()
            # Crea una nueva tarea con la descripción y marca que no es concreta (sin fecha)
            nueva_tarea = Tarea(descripcion=tarea, es_concreta=False)
            # Añade la tarea a la sesión
            session.add(nueva_tarea)
            # Guarda los cambios en la base de datos
            session.commit()
            # Informa al usuario que la tarea fue añadida
            self.voz.hablar(f"Tarea normal añadida: {tarea}")

        except Exception as e:
            # En caso de error, informa al usuario y muestra el error en consola
            self.voz.hablar("Ocurrió un error al guardar la tarea.")
            print(f"Error en ComandoTareaNormal: {e}")


# Clase para manejar comandos de tareas concretas (con fecha y hora)
class ComandoTareaConcreta(BaseComando):
    # Activa este comando si el texto contiene "tarea concreta"
    def activar(self, comando):
        return "tarea concreta" in comando

    # Ejecuta el comando para añadir una tarea concreta
    def ejecutar(self, comando):
        try:
            # Extrae la descripción quitando "tarea concreta"
            descripcion = comando.replace("tarea concreta", "").strip()
            # Si no hay descripción, pregunta al usuario hasta que responda o cancele
            while not descripcion:
                self.voz.hablar("¿Qué tarea concreta quieres añadir?")
                descripcion = self.voz.escuchar()
                if descripcion.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            # Pide la fecha para la tarea
            fecha = None
            while not fecha:
                self.voz.hablar("¿Para qué día es la tarea? Por ejemplo, 9 de mayo.")
                texto_fecha = self.voz.escuchar()
                if texto_fecha.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                # Intenta parsear la fecha del texto recibido
                fecha = self._parsear_fecha(texto_fecha)
                if not fecha:
                    self.voz.hablar("No entendí la fecha. Por favor, repítela.")

            # Pide la hora para la tarea
            hora_valida = False
            while not hora_valida:
                self.voz.hablar("¿A qué hora es la tarea? Por ejemplo, 21:30.")
                texto_hora = self.voz.escuchar()
                if texto_hora.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                try:
                    # Intenta extraer hora y minuto del texto
                    hora, minuto = map(int, texto_hora.split(":"))
                    # Verifica que la hora y minuto estén en rango válido
                    if 0 <= hora < 24 and 0 <= minuto < 60:
                        # Actualiza la fecha con la hora y minuto indicados
                        fecha = fecha.replace(hour=hora, minute=minuto)
                        hora_valida = True
                    else:
                        self.voz.hablar("Hora inválida. Debe estar entre 00:00 y 23:59.")
                except Exception:
                    self.voz.hablar("No entendí la hora. Por favor, dilo en formato 21:30.")

            # Guarda la tarea en la base de datos
            session = obtener_sesion()
            nueva_tarea = Tarea(descripcion=descripcion, es_concreta=True, fecha=fecha)
            session.add(nueva_tarea)
            session.commit()
            # Crea un evento en Google Calendar con la descripción y fecha
            crear_evento_google_calendar(descripcion, fecha)

            # Informa al usuario que la tarea concreta fue añadida con fecha y hora
            self.voz.hablar(f"Tarea concreta añadida: {descripcion} para el {fecha.strftime('%d/%m/%Y %H:%M')}")

        except Exception as e:
            # En caso de error, informa al usuario y muestra el error en consola
            self.voz.hablar("Ocurrió un error al añadir la tarea concreta.")
            print(f"Error en ComandoTareaConcreta: {e}")

    # Método privado para parsear texto y obtener un objeto datetime
    def _parsear_fecha(self, texto):
        try:
            # Diccionario que mapea nombres de meses a números
            meses = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
                'noviembre': 11, 'diciembre': 12
            }
            texto = texto.lower()

            # Maneja expresiones relativas de fecha
            if "pasado mañana" in texto:
                return datetime.now() + timedelta(days=2)
            elif "mañana" in texto:
                return datetime.now() + timedelta(days=1)

            # Busca expresiones como "en X día(s)"
            match_dias = re.search(r"en (\d+) día", texto)
            if match_dias:
                dias = int(match_dias.group(1))
                return datetime.now() + timedelta(days=dias)

            # Busca fechas en formato "día de mes"
            match = re.search(r"(\d{1,2}) de (\w+)", texto)
            if match:
                dia = int(match.group(1))
                mes = meses.get(match.group(2))
                if mes:
                    año = datetime.now().year
                    fecha = datetime(año, mes, dia)
                    # Si la fecha ya pasó este año, la pone para el próximo año
                    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    if fecha < hoy:
                        fecha = datetime(año + 1, mes, dia)
                    return fecha
        except Exception as e:
            # En caso de error al parsear, imprime el error
            print(f"Error al parsear fecha: {e}")
        # Si no pudo parsear, devuelve None
        return None


# Clase para listar las tareas pendientes
class ComandoListarTareas(BaseComando):
    # Activa el comando si el texto contiene "mostrar tareas" o "ver tareas"
    def activar(self, comando):
        return "mostrar tareas" in comando or "ver tareas" in comando

    # Ejecuta el comando para listar tareas
    def ejecutar(self, comando):
        try:
            # Obtiene la sesión de base de datos
            session = obtener_sesion()
            # Consulta todas las tareas que no están completadas
            tareas = session.query(Tarea).filter_by(completada=False).all()
            if tareas:
                # Informa cuántas tareas pendientes hay
                self.voz.hablar(f"Tienes {len(tareas)} tareas pendientes.")
                # Enumera y dice la descripción de cada tarea con fecha si tiene
                for i, tarea in enumerate(tareas, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(tarea)}")
            else:
                # Si no hay tareas pendientes, informa al usuario
                self.voz.hablar("No tienes tareas pendientes.")
        except Exception as e:
            # En caso de error, informa al usuario y muestra el error en consola
            self.voz.hablar("Ocurrió un error al listar las tareas.")
            print(f"Error en ComandoListarTareas: {e}")


# Clase para completar una tarea pendiente
class ComandoCompletarTarea(BaseComando):
    # Activa el comando si el texto contiene "completar tarea"
    def activar(self, comando):
        return "completar tarea" in comando

    # Ejecuta el comando para marcar una tarea como completada
    def ejecutar(self, comando):
        try:
            # Obtiene la sesión de base de datos
            session = obtener_sesion()
            # Consulta todas las tareas no completadas
            tareas = session.query(Tarea).filter_by(completada=False).all()
            # Si no hay tareas pendientes, informa y termina
            if not tareas:
                self.voz.hablar("No tienes tareas pendientes.")
                return

            # Busca un número de tarea en el comando (ejemplo: "número 2")
            match_num = re.search(r"número (\d+)", comando)
            if not match_num:
                # Alternativamente busca "completar tarea X"
                match_num = re.search(r"completar tarea (\d+)", comando)

            if match_num:
                # Si encontró número, convierte a entero
                num = int(match_num.group(1))
                # Verifica que el número esté dentro del rango de tareas
                if 1 <= num <= len(tareas):
                    # Marca la tarea correspondiente como completada
                    tarea = tareas[num - 1]
                    tarea.completada = True
                    session.commit()
                    # Informa al usuario que la tarea fue completada
                    self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
                else:
                    # Si el número no existe, informa al usuario
                    self.voz.hablar("No existe esa tarea.")
                return

            # Si no se especificó número, intenta obtener descripción de la tarea
            desc = comando.replace("completar tarea", "").replace("número", "").strip()
            # Si no hay descripción, pregunta al usuario hasta que responda o cancele
            while not desc:
                self.voz.hablar("¿Qué tarea quieres completar? Puedes decir el número o la descripción.")
                desc = self.voz.escuchar()
                if desc.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            # Busca tareas que contengan la descripción dada
            coincidencias = [t for t in tareas if desc.lower() in t.descripcion.lower()]
            if not coincidencias:
                # Si no encontró ninguna, informa al usuario
                self.voz.hablar("No encontré esa tarea.")
            elif len(coincidencias) == 1:
                # Si encontró una sola, la marca como completada
                coincidencias[0].completada = True
                session.commit()
                self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(coincidencias[0])}")
            else:
                # Si encontró varias, las enumera y pregunta cuál completar
                self.voz.hablar("Encontré varias tareas similares:")
                for i, t in enumerate(coincidencias, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(t)}")
                self.voz.hablar("¿Cuál número quieres completar?")
                respuesta = self.voz.escuchar()
                if respuesta.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                try:
                    # Intenta convertir la respuesta a número y marcar la tarea
                    indice = int(respuesta) - 1
                    if 0 <= indice < len(coincidencias):
                        coincidencias[indice].completada = True
                        session.commit()
                        self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(coincidencias[indice])}")
                    else:
                        self.voz.hablar("Número inválido.")
                except ValueError:
                    self.voz.hablar("No entendí el número.")
        except Exception as e:
            # En caso de error, informa al usuario y muestra el error en consola
            self.voz.hablar("Ocurrió un error al completar la tarea.")
            print(f"Error en ComandoCompletarTarea: {e}")


# Clase para eliminar una tarea pendiente
class ComandoEliminarTarea(BaseComando):
    # Activa el comando si el texto contiene "eliminar tarea" o "borrar tarea"
    def activar(self, comando):
        return "eliminar tarea" in comando or "borrar tarea" in comando

    # Ejecuta el comando para eliminar una tarea
    def ejecutar(self, comando):
        try:
            # Obtiene la sesión de base de datos
            session = obtener_sesion()
            # Consulta todas las tareas no completadas
            tareas = session.query(Tarea).filter_by(completada=False).all()
            # Si no hay tareas para eliminar, informa y termina
            if not tareas:
                self.voz.hablar("No tienes tareas para eliminar.")
                return

            # Busca un número de tarea en el comando
            match_num = re.search(r"número (\d+)", comando)
            if not match_num:
                # Alternativamente busca "eliminar tarea X" o "borrar tarea X"
                match_num = re.search(r"(eliminar|borrar) tarea (\d+)", comando)

            if match_num:
                # Obtiene el número según el formato del comando
                num = int(match_num.group(1) if "número" in comando else match_num.group(2))
                # Verifica que el número esté dentro del rango de tareas
                if 1 <= num <= len(tareas):
                    # Elimina la tarea correspondiente
                    tarea = tareas[num - 1]
                    session.delete(tarea)
                    session.commit()
                    # Informa al usuario que la tarea fue eliminada
                    self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
                else:
                    # Si el número no existe, informa al usuario
                    self.voz.hablar("No existe esa tarea.")
                return

            # Si no se especificó número, intenta obtener descripción de la tarea
            desc = comando.replace("eliminar tarea", "").replace("borrar tarea", "").replace("número", "").strip()
            # Si no hay descripción, pregunta al usuario hasta que responda o cancele
            while not desc:
                self.voz.hablar("¿Qué tarea quieres eliminar? Puedes decir el número o la descripción.")
                desc = self.voz.escuchar()
                if desc.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            # Busca tareas que contengan la descripción dada
            coincidencias = [t for t in tareas if desc.lower() in t.descripcion.lower()]
            if not coincidencias:
                # Si no encontró ninguna, informa al usuario
                self.voz.hablar("No encontré esa tarea.")
            elif len(coincidencias) == 1:
                # Si encontró una sola, la elimina
                session.delete(coincidencias[0])
                session.commit()
                self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(coincidencias[0])}")
            else:
                # Si encontró varias, las enumera y pregunta cuál eliminar
                self.voz.hablar("Encontré varias tareas similares:")
                for i, t in enumerate(coincidencias, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(t)}")
                self.voz.hablar("¿Cuál número quieres eliminar?")
                respuesta = self.voz.escuchar()
                if respuesta.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                try:
                    # Intenta convertir la respuesta a número y eliminar la tarea
                    indice = int(respuesta) - 1
                    if 0 <= indice < len(coincidencias):
                        session.delete(coincidencias[indice])
                        session.commit()
                        self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(coincidencias[indice])}")
                    else:
                        self.voz.hablar("Número inválido.")
                except ValueError:
                    self.voz.hablar("No entendí el número.")
        except Exception as e:
            # En caso de error, informa al usuario y muestra el error en consola
            self.voz.hablar("Ocurrió un error al eliminar la tarea.")
            print(f"Error en ComandoEliminarTarea: {e}")
