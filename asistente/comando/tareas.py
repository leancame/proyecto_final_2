from .base import BaseComando
from asistente.servicios.db import obtener_sesion, Tarea
from asistente.servicios.google_calendar import crear_evento_google_calendar
from datetime import datetime, timedelta
import re


def descripcion_con_fecha(tarea):
    if tarea.es_concreta and tarea.fecha:
        return f"{tarea.descripcion} para el {tarea.fecha.strftime('%d/%m/%Y %H:%M')}"
    return tarea.descripcion


class ComandoTareaNormal(BaseComando):
    def activar(self, comando):
        return "tarea normal" in comando

    def ejecutar(self, comando):
        try:
            tarea = comando.replace("tarea normal", "").strip()
            while not tarea:
                self.voz.hablar("¿Qué tarea quieres añadir?")
                tarea = self.voz.escuchar()
                if tarea.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            session = obtener_sesion()
            nueva_tarea = Tarea(descripcion=tarea, es_concreta=False)
            session.add(nueva_tarea)
            session.commit()
            self.voz.hablar(f"Tarea normal añadida: {tarea}")

        except Exception as e:
            self.voz.hablar("Ocurrió un error al guardar la tarea.")
            print(f"Error en ComandoTareaNormal: {e}")


class ComandoTareaConcreta(BaseComando):
    def activar(self, comando):
        return "tarea concreta" in comando

    def ejecutar(self, comando):
        try:
            descripcion = comando.replace("tarea concreta", "").strip()
            while not descripcion:
                self.voz.hablar("¿Qué tarea concreta quieres añadir?")
                descripcion = self.voz.escuchar()
                if descripcion.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            # Pedir fecha
            fecha = None
            while not fecha:
                self.voz.hablar("¿Para qué día es la tarea? Por ejemplo, 9 de mayo.")
                texto_fecha = self.voz.escuchar()
                if texto_fecha.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                fecha = self._parsear_fecha(texto_fecha)
                if not fecha:
                    self.voz.hablar("No entendí la fecha. Por favor, repítela.")

            # Pedir hora
            hora_valida = False
            while not hora_valida:
                self.voz.hablar("¿A qué hora es la tarea? Por ejemplo, 21:30.")
                texto_hora = self.voz.escuchar()
                if texto_hora.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                try:
                    hora, minuto = map(int, texto_hora.split(":"))
                    if 0 <= hora < 24 and 0 <= minuto < 60:
                        fecha = fecha.replace(hour=hora, minute=minuto)
                        hora_valida = True
                    else:
                        self.voz.hablar("Hora inválida. Debe estar entre 00:00 y 23:59.")
                except Exception:
                    self.voz.hablar("No entendí la hora. Por favor, dilo en formato 21:30.")

            # Guardar tarea
            session = obtener_sesion()
            nueva_tarea = Tarea(descripcion=descripcion, es_concreta=True, fecha=fecha)
            session.add(nueva_tarea)
            session.commit()
            crear_evento_google_calendar(descripcion, fecha)

            self.voz.hablar(f"Tarea concreta añadida: {descripcion} para el {fecha.strftime('%d/%m/%Y %H:%M')}")

        except Exception as e:
            self.voz.hablar("Ocurrió un error al añadir la tarea concreta.")
            print(f"Error en ComandoTareaConcreta: {e}")

    def _parsear_fecha(self, texto):
        try:
            meses = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
                'noviembre': 11, 'diciembre': 12
            }
            texto = texto.lower()

            if "pasado mañana" in texto:
                return datetime.now() + timedelta(days=2)
            elif "mañana" in texto:
                return datetime.now() + timedelta(days=1)

            match_dias = re.search(r"en (\d+) día", texto)
            if match_dias:
                dias = int(match_dias.group(1))
                return datetime.now() + timedelta(days=dias)

            match = re.search(r"(\d{1,2}) de (\w+)", texto)
            if match:
                dia = int(match.group(1))
                mes = meses.get(match.group(2))
                if mes:
                    año = datetime.now().year
                    fecha = datetime(año, mes, dia)
                    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    if fecha < hoy:
                        fecha = datetime(año + 1, mes, dia)
                    return fecha
        except Exception as e:
            print(f"Error al parsear fecha: {e}")
        return None


class ComandoListarTareas(BaseComando):
    def activar(self, comando):
        return "mostrar tareas" in comando or "ver tareas" in comando

    def ejecutar(self, comando):
        try:
            session = obtener_sesion()
            tareas = session.query(Tarea).filter_by(completada=False).all()
            if tareas:
                self.voz.hablar(f"Tienes {len(tareas)} tareas pendientes.")
                for i, tarea in enumerate(tareas, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(tarea)}")
            else:
                self.voz.hablar("No tienes tareas pendientes.")
        except Exception as e:
            self.voz.hablar("Ocurrió un error al listar las tareas.")
            print(f"Error en ComandoListarTareas: {e}")


class ComandoCompletarTarea(BaseComando):
    def activar(self, comando):
        return "completar tarea" in comando

    def ejecutar(self, comando):
        try:
            session = obtener_sesion()
            tareas = session.query(Tarea).filter_by(completada=False).all()
            if not tareas:
                self.voz.hablar("No tienes tareas pendientes.")
                return

            match_num = re.search(r"número (\d+)", comando)
            if not match_num:
                match_num = re.search(r"completar tarea (\d+)", comando)

            if match_num:
                num = int(match_num.group(1))
                if 1 <= num <= len(tareas):
                    tarea = tareas[num - 1]
                    tarea.completada = True
                    session.commit()
                    self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
                else:
                    self.voz.hablar("No existe esa tarea.")
                return

            desc = comando.replace("completar tarea", "").replace("número", "").strip()
            while not desc:
                self.voz.hablar("¿Qué tarea quieres completar? Puedes decir el número o la descripción.")
                desc = self.voz.escuchar()
                if desc.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            coincidencias = [t for t in tareas if desc.lower() in t.descripcion.lower()]
            if not coincidencias:
                self.voz.hablar("No encontré esa tarea.")
            elif len(coincidencias) == 1:
                coincidencias[0].completada = True
                session.commit()
                self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(coincidencias[0])}")
            else:
                self.voz.hablar("Encontré varias tareas similares:")
                for i, t in enumerate(coincidencias, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(t)}")
                self.voz.hablar("¿Cuál número quieres completar?")
                respuesta = self.voz.escuchar()
                if respuesta.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                try:
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
            self.voz.hablar("Ocurrió un error al completar la tarea.")
            print(f"Error en ComandoCompletarTarea: {e}")


class ComandoEliminarTarea(BaseComando):
    def activar(self, comando):
        return "eliminar tarea" in comando or "borrar tarea" in comando

    def ejecutar(self, comando):
        try:
            session = obtener_sesion()
            tareas = session.query(Tarea).filter_by(completada=False).all()
            if not tareas:
                self.voz.hablar("No tienes tareas para eliminar.")
                return

            match_num = re.search(r"número (\d+)", comando)
            if not match_num:
                match_num = re.search(r"(eliminar|borrar) tarea (\d+)", comando)

            if match_num:
                num = int(match_num.group(1) if "número" in comando else match_num.group(2))
                if 1 <= num <= len(tareas):
                    tarea = tareas[num - 1]
                    session.delete(tarea)
                    session.commit()
                    self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
                else:
                    self.voz.hablar("No existe esa tarea.")
                return

            desc = comando.replace("eliminar tarea", "").replace("borrar tarea", "").replace("número", "").strip()
            while not desc:
                self.voz.hablar("¿Qué tarea quieres eliminar? Puedes decir el número o la descripción.")
                desc = self.voz.escuchar()
                if desc.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            coincidencias = [t for t in tareas if desc.lower() in t.descripcion.lower()]
            if not coincidencias:
                self.voz.hablar("No encontré esa tarea.")
            elif len(coincidencias) == 1:
                session.delete(coincidencias[0])
                session.commit()
                self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(coincidencias[0])}")
            else:
                self.voz.hablar("Encontré varias tareas similares:")
                for i, t in enumerate(coincidencias, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(t)}")
                self.voz.hablar("¿Cuál número quieres eliminar?")
                respuesta = self.voz.escuchar()
                if respuesta.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return
                try:
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
            self.voz.hablar("Ocurrió un error al eliminar la tarea.")
            print(f"Error en ComandoEliminarTarea: {e}")
