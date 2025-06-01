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
        tarea = comando.replace("tarea normal", "").strip()

        while not tarea:
            self.voz.hablar("¿Qué tarea quieres añadir?")
            tarea = self.voz.escuchar()

        session = obtener_sesion()
        nueva_tarea = Tarea(descripcion=tarea, es_concreta=False)
        session.add(nueva_tarea)
        session.commit()
        self.voz.hablar(f"Tarea normal añadida: {tarea}")


class ComandoTareaConcreta(BaseComando):
    def activar(self, comando):
        return "tarea concreta" in comando

    def ejecutar(self, comando):
        # Paso 1: pedir descripción
        descripcion = comando.replace("tarea concreta", "").strip()
        while not descripcion:
            self.voz.hablar("¿Qué tarea concreta quieres añadir?")
            descripcion = self.voz.escuchar()

        # Paso 2: pedir fecha
        fecha = None
        while not fecha:
            self.voz.hablar("¿Para qué día es la tarea? Por ejemplo, 9 de mayo.")
            texto_fecha = self.voz.escuchar()
            fecha = self._parsear_fecha(texto_fecha)
            if not fecha:
                self.voz.hablar("No entendí la fecha. Por favor, repítela.")

        # Paso 3: pedir hora
        hora_valida = False
        while not hora_valida:
            self.voz.hablar("¿A qué hora es la tarea? Por ejemplo, 21:30.")
            texto_hora = self.voz.escuchar()
            try:
                hora, minuto = map(int, texto_hora.split(":"))
                if 0 <= hora < 24 and 0 <= minuto < 60:
                    fecha = fecha.replace(hour=hora, minute=minuto)
                    hora_valida = True
                else:
                    self.voz.hablar("Hora inválida. Debe estar entre 00:00 y 23:59.")
            except Exception:
                self.voz.hablar("No entendí la hora. Por favor, dilo en formato 21:30.")

        # Guardar tarea y crear evento Google Calendar
        session = obtener_sesion()
        nueva_tarea = Tarea(descripcion=descripcion, es_concreta=True, fecha=fecha)
        session.add(nueva_tarea)
        session.commit()
        crear_evento_google_calendar(descripcion, fecha)

        self.voz.hablar(f"Tarea concreta añadida: {descripcion} para el {fecha.strftime('%d/%m/%Y %H:%M')}")

    def _parsear_fecha(self, texto):
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
            'noviembre': 11, 'diciembre': 12
        }
        texto = texto.lower()
        try:
            if "pasado mañana" in texto:
                return datetime.now() + timedelta(days=2)
            elif "mañana" in texto:
                return datetime.now() + timedelta(days=1)

            match_dias = re.search(r"en (\d+) día", texto)
            if match_dias:
                dias = int(match_dias.group(1))
                return datetime.now() + timedelta(days=dias)

            # Patrón: día de mes (sin hora)
            match = re.search(r"(\d{1,2}) de (\w+)", texto)
            if match:
                dia = int(match.group(1))
                mes_texto = match.group(2)
                mes = meses.get(mes_texto)
                if mes:
                    año_actual = datetime.now().year
                    fecha = datetime(año_actual, mes, dia)

                    hoy_sin_hora = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    # Si la fecha ya pasó, asume del siguiente año
                    if fecha < hoy_sin_hora:
                        fecha = datetime(año_actual + 1, mes, dia)
                    return fecha

        except Exception as e:
            print(f"Error al interpretar la fecha: {e}")
        return None


class ComandoListarTareas(BaseComando):
    def activar(self, comando):
        return "mostrar tareas" in comando or "ver tareas" in comando

    def ejecutar(self, comando):
        session = obtener_sesion()
        tareas = session.query(Tarea).filter_by(completada=False).all()
        if tareas:
            self.voz.hablar(f"Tienes {len(tareas)} tareas pendientes.")
            for i, tarea in enumerate(tareas, 1):
                self.voz.hablar(f"{i}. {descripcion_con_fecha(tarea)}")
        else:
            self.voz.hablar("No tienes tareas pendientes.")


class ComandoCompletarTarea(BaseComando):
    def activar(self, comando):
        return "completar tarea" in comando

    def ejecutar(self, comando):
        session = obtener_sesion()
        tareas = session.query(Tarea).filter_by(completada=False).all()

        if not tareas:
            self.voz.hablar("No tienes tareas pendientes para completar.")
            return

        # Buscar número en el comando
        match_num = re.search(r"número (\d+)", comando)
        if match_num:
            numero = int(match_num.group(1))
            if 1 <= numero <= len(tareas):
                tarea = tareas[numero - 1]
                tarea.completada = True
                session.commit()
                self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
            else:
                self.voz.hablar(f"No existe la tarea número {numero}.")
            return

        # Si solo dice "completar tarea X" donde X es un número simple sin "número"
        match_simple_num = re.search(r"completar tarea (\d+)", comando)
        if match_simple_num:
            numero = int(match_simple_num.group(1))
            if 1 <= numero <= len(tareas):
                tarea = tareas[numero - 1]
                tarea.completada = True
                session.commit()
                self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
            else:
                self.voz.hablar(f"No existe la tarea número {numero}.")
            return

        tarea_desc = comando.replace("completar tarea", "").replace("número", "").strip()

        if not tarea_desc:
            self.voz.hablar("¿Qué tarea quieres marcar como completada? Puedes decir el número o la descripción.")
            tarea_desc = self.voz.escuchar()

        tareas_encontradas = [t for t in tareas if tarea_desc.lower() in t.descripcion.lower()]

        if not tareas_encontradas:
            self.voz.hablar("No encontré esa tarea pendiente.")
        elif len(tareas_encontradas) == 1:
            tarea = tareas_encontradas[0]
            tarea.completada = True
            session.commit()
            self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
        else:
            self.voz.hablar("Encontré varias tareas similares:")
            for i, tarea in enumerate(tareas_encontradas, 1):
                self.voz.hablar(f"{i}. {descripcion_con_fecha(tarea)}")
            self.voz.hablar("¿Cuál número quieres completar?")
            opcion = self.voz.escuchar()
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(tareas_encontradas):
                    tarea = tareas_encontradas[indice]
                    tarea.completada = True
                    session.commit()
                    self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
                else:
                    self.voz.hablar("Número inválido.")
            except ValueError:
                self.voz.hablar("No entendí el número.")


class ComandoEliminarTarea(BaseComando):
    def activar(self, comando):
        return "eliminar tarea" in comando or "borrar tarea" in comando

    def ejecutar(self, comando):
        session = obtener_sesion()
        tareas = session.query(Tarea).filter_by(completada=False).all()

        if not tareas:
            self.voz.hablar("No tienes tareas para eliminar.")
            return

        match_num = re.search(r"número (\d+)", comando)
        if match_num:
            numero = int(match_num.group(1))
            if 1 <= numero <= len(tareas):
                tarea = tareas[numero - 1]
                session.delete(tarea)
                session.commit()
                self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
            else:
                self.voz.hablar(f"No existe la tarea número {numero}.")
            return

        match_simple_num = re.search(r"(eliminar|borrar) tarea (\d+)", comando)
        if match_simple_num:
            numero = int(match_simple_num.group(2))
            if 1 <= numero <= len(tareas):
                tarea = tareas[numero - 1]
                session.delete(tarea)
                session.commit()
                self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
            else:
                self.voz.hablar(f"No existe la tarea número {numero}.")
            return

        tarea_desc = comando.replace("eliminar tarea", "").replace("borrar tarea", "").replace("número", "").strip()

        if not tarea_desc:
            self.voz.hablar("¿Qué tarea quieres eliminar? Puedes decir el número o la descripción.")
            tarea_desc = self.voz.escuchar()

        tareas_encontradas = [t for t in tareas if tarea_desc.lower() in t.descripcion.lower()]

        if not tareas_encontradas:
            self.voz.hablar("No encontré esa tarea.")
        elif len(tareas_encontradas) == 1:
            tarea = tareas_encontradas[0]
            session.delete(tarea)
            session.commit()
            self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
        else:
            self.voz.hablar("Encontré varias tareas similares:")
            for i, tarea in enumerate(tareas_encontradas, 1):
                self.voz.hablar(f"{i}. {descripcion_con_fecha(tarea)}")
            self.voz.hablar("¿Cuál número quieres eliminar?")
            opcion = self.voz.escuchar()
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(tareas_encontradas):
                    tarea = tareas_encontradas[indice]
                    session.delete(tarea)
                    session.commit()
                    self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
                else:
                    self.voz.hablar("Número inválido.")
            except ValueError:
                self.voz.hablar("No entendí el número.")
