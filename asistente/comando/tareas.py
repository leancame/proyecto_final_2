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

# Función que convierte un número escrito en texto (como "uno", "dos") a su valor numérico (1, 2, etc.)
def texto_a_numero(texto):
    # Diccionario que mapea palabras numéricas en español a sus valores enteros correspondientes
    numeros = {
        "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
        "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
        "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
        "dieciséis": 16, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
        "diecinueve": 19, "veinte": 20
    }
    # Convierte el texto a minúsculas para evitar errores por uso de mayúsculas
    texto = texto.lower()
    # Si el texto está compuesto por dígitos (como "12"), lo convierte directamente a entero
    if texto.isdigit():
        return int(texto)
    # Si el texto coincide con una palabra del diccionario, devuelve su valor; si no, devuelve None
    return numeros.get(texto, None)


# Clase para manejar el comando de "completar tarea"
class ComandoCompletarTarea(BaseComando):

    # Método que determina si este comando debe activarse en base al texto dado
    def activar(self, comando):
        # Retorna True si el texto contiene la frase "completar tarea"
        return "completar tarea" in comando.lower()

    # Método principal que ejecuta la lógica para completar una tarea
    def ejecutar(self, comando):
        try:
            # Obtiene una sesión de la base de datos
            session = obtener_sesion()
            # Consulta todas las tareas que aún no han sido completadas
            tareas = session.query(Tarea).filter_by(completada=False).all()

            # Si no hay tareas pendientes, se informa al usuario
            if not tareas:
                self.voz.hablar("No tienes tareas pendientes.")
                return

            # Convierte el comando a minúsculas para hacer comparaciones sin distinción de mayúsculas
            comando_lower = comando.lower()

            # Busca un número (como "completar tarea 2") en el texto del comando usando una expresión regular
            match_num = re.search(r"completar tarea(?: número)? (\d+)", comando_lower)
            if match_num:
                # Si encuentra un número, lo convierte a entero
                num = int(match_num.group(1))
                # Verifica si el número es válido dentro del rango de tareas
                if 1 <= num <= len(tareas):
                    # Marca la tarea como completada
                    tarea = tareas[num - 1]
                    tarea.completada = True
                    # Guarda los cambios en la base de datos
                    session.commit()
                    # Informa al usuario que la tarea fue completada
                    self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
                else:
                    # Si el número está fuera del rango, informa al usuario
                    self.voz.hablar("No existe esa tarea.")
                return

            # Si no se detectó un número con regex, se analiza palabra por palabra
            palabras = comando_lower.split()
            for palabra in palabras:
                # Intenta convertir cada palabra a número usando la función definida antes
                num = texto_a_numero(palabra)
                if num is not None:
                    # Si el número es válido, completa la tarea correspondiente
                    if 1 <= num <= len(tareas):
                        tarea = tareas[num - 1]
                        tarea.completada = True
                        session.commit()
                        self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
                        return
                    else:
                        self.voz.hablar("Número fuera de rango.")
                        return

            # Si aún no se encontró número, se le pide al usuario que especifique la tarea
            self.voz.hablar("¿Qué tarea quieres completar? Puedes decir el número o la descripción.")

            # Bucle para esperar la respuesta del usuario
            while True:
                # Escucha la respuesta por voz
                respuesta = self.voz.escuchar()
                print(f"DEBUG: respuesta recibida: '{respuesta}'")

                # Si no se recibe una respuesta clara, se vuelve a pedir
                if not respuesta:
                    self.voz.hablar("No entendí. Por favor, repite o di 'cancelar'.")
                    continue

                # Convierte la respuesta a minúsculas
                respuesta_lower = respuesta.lower()

                # Si el usuario dice cancelar, se interrumpe el proceso
                if respuesta_lower in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

                # Intenta convertir la respuesta a número (primero como texto, luego como dígito)
                num = texto_a_numero(respuesta_lower)
                if num is None:
                    try:
                        num = int(respuesta_lower)
                    except:
                        num = None

                # Si se logró obtener un número válido
                if num is not None:
                    if 1 <= num <= len(tareas):
                        tarea = tareas[num - 1]
                        tarea.completada = True
                        session.commit()
                        self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(tarea)}")
                        return
                    else:
                        self.voz.hablar("Número inválido. Intenta de nuevo o di 'cancelar'.")
                        continue

                # Si no es número, intenta buscar tareas por coincidencia parcial en la descripción
                coincidencias = [t for t in tareas if respuesta_lower in t.descripcion.lower()]

                # Si no se encontraron coincidencias, se informa
                if not coincidencias:
                    self.voz.hablar("No encontré esa tarea. Intenta con otra descripción o di 'cancelar'.")
                    continue

                # Si hay una sola coincidencia, se completa directamente
                if len(coincidencias) == 1:
                    coincidencias[0].completada = True
                    session.commit()
                    self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(coincidencias[0])}")
                    return

                # Si hay varias coincidencias, se listan al usuario
                self.voz.hablar("Encontré varias tareas similares:")
                for i, tarea in enumerate(coincidencias, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(tarea)}")

                # Se pide al usuario que indique cuál desea completar
                self.voz.hablar("¿Cuál número quieres completar?")

                # Segundo bucle para recibir número de selección
                while True:
                    respuesta_num = self.voz.escuchar()

                    # Verifica si la respuesta es válida
                    if not respuesta_num:
                        self.voz.hablar("No entendí. Por favor, di el número o 'cancelar'.")
                        continue

                    # Si el usuario dice cancelar, finaliza
                    if respuesta_num.lower() in ["cancelar", "salir", "finalizar"]:
                        self.voz.hablar("Operación cancelada.")
                        return

                    # Intenta convertir la respuesta a número (como palabra o dígito)
                    num = texto_a_numero(respuesta_num.lower())
                    if num is None:
                        try:
                            num = int(respuesta_num)
                        except:
                            self.voz.hablar("No entendí. Por favor, di el número o 'cancelar'.")
                            continue

                    # Verifica si el número está dentro del rango válido
                    if 1 <= num <= len(coincidencias):
                        coincidencias[num - 1].completada = True
                        session.commit()
                        self.voz.hablar(f"Tarea completada: {descripcion_con_fecha(coincidencias[num - 1])}")
                        return
                    else:
                        self.voz.hablar("Número inválido. Intenta de nuevo o di 'cancelar'.")

        # Si ocurre algún error en la ejecución, se informa al usuario y se imprime en consola
        except Exception as e:
            self.voz.hablar("Ocurrió un error al completar la tarea.")
            print(f"Error en ComandoCompletarTarea: {e}")

# Clase que maneja el comando para eliminar o borrar una tarea
class ComandoEliminarTarea(BaseComando):

    # Método que determina si el comando ingresado corresponde a eliminar una tarea
    def activar(self, comando):
        # Devuelve True si el comando contiene "eliminar tarea" o "borrar tarea"
        return "eliminar tarea" in comando or "borrar tarea" in comando

    # Método que ejecuta la lógica para eliminar una tarea
    def ejecutar(self, comando):
        try:
            # Obtiene una sesión de la base de datos
            session = obtener_sesion()
            # Consulta todas las tareas no completadas (activas)
            tareas = session.query(Tarea).filter_by(completada=False).all()

            # Si no hay tareas pendientes, informa al usuario
            if not tareas:
                self.voz.hablar("No tienes tareas para eliminar.")
                return

            # Intenta extraer un número directamente desde el comando usando regex
            match_num = re.search(r"número (\d+)", comando)
            # Si no encontró, intenta con otra estructura del comando (ej. "eliminar tarea 2")
            if not match_num:
                match_num = re.search(r"(eliminar|borrar) tarea (\d+)", comando)

            # Inicializa la variable num como None
            num = None

            # Si encontró un número en el comando
            if match_num:
                # Dependiendo de qué patrón coincidió, extrae el número del grupo adecuado
                num = int(match_num.group(1) if "número" in comando else match_num.group(2))
            else:
                # Si no encontró número con regex, intenta palabra por palabra convertir texto a número
                for palabra in comando.lower().split():
                    num = texto_a_numero(palabra)
                    if num is not None:
                        break  # Si encuentra uno válido, se detiene

            # Si obtuvo un número
            if num is not None:
                # Verifica que el número esté dentro del rango de tareas existentes
                if 1 <= num <= len(tareas):
                    # Selecciona la tarea correspondiente
                    tarea = tareas[num - 1]
                    # Elimina la tarea de la base de datos
                    session.delete(tarea)
                    # Guarda los cambios
                    session.commit()
                    # Informa al usuario que la tarea fue eliminada
                    self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(tarea)}")
                else:
                    # Si el número no corresponde a ninguna tarea, informa
                    self.voz.hablar("No existe esa tarea.")
                return  # Sale del método después de eliminar o informar error

            # Si no se encontró número, intenta obtener la descripción
            desc = comando.replace("eliminar tarea", "").replace("borrar tarea", "").replace("número", "").strip()

            # Si la descripción está vacía, se pregunta al usuario qué tarea eliminar
            while not desc:
                self.voz.hablar("¿Qué tarea quieres eliminar? Puedes decir el número o la descripción.")
                desc = self.voz.escuchar()
                print(f"DEBUG: respuesta recibida: '{desc}'")

                # Si el usuario quiere cancelar, termina el proceso
                if desc.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

            # Busca tareas cuya descripción contenga la palabra clave ingresada
            coincidencias = [t for t in tareas if desc.lower() in t.descripcion.lower()]

            # Si no encontró ninguna tarea con esa descripción, informa
            if not coincidencias:
                self.voz.hablar("No encontré esa tarea.")
            # Si solo hay una coincidencia, la elimina directamente
            elif len(coincidencias) == 1:
                session.delete(coincidencias[0])
                session.commit()
                self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(coincidencias[0])}")
            else:
                # Si hay varias coincidencias, las enumera para que el usuario elija
                self.voz.hablar("Encontré varias tareas similares:")
                for i, t in enumerate(coincidencias, 1):
                    self.voz.hablar(f"{i}. {descripcion_con_fecha(t)}")

                # Pide al usuario que indique cuál tarea quiere eliminar
                self.voz.hablar("¿Cuál número quieres eliminar?")
                respuesta = self.voz.escuchar()

                # Si el usuario cancela, termina la operación
                if respuesta.lower() in ["cancelar", "salir", "finalizar"]:
                    self.voz.hablar("Operación cancelada.")
                    return

                # Intenta convertir la respuesta del usuario a número
                num_resp = texto_a_numero(respuesta)
                if num_resp is None:
                    try:
                        num_resp = int(respuesta)
                    except ValueError:
                        self.voz.hablar("No entendí el número.")
                        return

                # Convierte a índice (base cero)
                indice = num_resp - 1

                # Verifica si el número corresponde a una coincidencia válida
                if 0 <= indice < len(coincidencias):
                    # Elimina la tarea seleccionada
                    session.delete(coincidencias[indice])
                    session.commit()
                    self.voz.hablar(f"Tarea eliminada: {descripcion_con_fecha(coincidencias[indice])}")
                else:
                    # Si el número está fuera de rango, informa
                    self.voz.hablar("Número inválido.")
        except Exception as e:
            # Captura cualquier error y lo informa al usuario
            self.voz.hablar("Ocurrió un error al eliminar la tarea.")
            print(f"Error en ComandoEliminarTarea: {e}")
