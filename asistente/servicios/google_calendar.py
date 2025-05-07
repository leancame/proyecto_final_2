# Importa las credenciales para autenticar al usuario con OAuth2
from google.oauth2.credentials import Credentials
# Importa el manejador de solicitudes para refrescar tokens de acceso
from google.auth.transport.requests import Request
# Importa el flujo de autenticación para aplicaciones instaladas
from google_auth_oauthlib.flow import InstalledAppFlow
# Importa la función build para construir el servicio de la API de Google
from googleapiclient.discovery import build
# Importa timedelta para operar con fechas y horas
from datetime import timedelta
# Importa os para verificar la existencia de archivos
import os

# Define los permisos necesarios para acceder al calendario de Google
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Función que configura y retorna el servicio de Google Calendar autenticado
def obtener_servicio():
    creds = None  # Inicializa las credenciales como None

    # Verifica si existe un archivo con credenciales previamente guardadas
    if os.path.exists('token.json'):
        # Carga las credenciales desde el archivo
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si no hay credenciales válidas, se realiza el flujo de autenticación
    if not creds or not creds.valid:
        # Si las credenciales están vencidas pero se pueden refrescar
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresca el token
        else:
            # Inicia el flujo de autenticación usando un archivo de secretos
            flow = InstalledAppFlow.from_client_secrets_file('asistente/google/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Ejecuta el servidor local para autenticación

        # Guarda las nuevas credenciales en un archivo para futuras sesiones
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Construye y retorna el servicio de Google Calendar autenticado
    servicio = build('calendar', 'v3', credentials=creds)
    return servicio

# Función que crea un evento en Google Calendar
def crear_evento_google_calendar(descripcion, fecha):
    servicio = obtener_servicio()  # Obtiene el servicio autenticado

    # Define el evento con título, fecha de inicio y fin (1 hora después)
    evento = {
        'summary': descripcion,  # Título del evento
        'start': {
            'dateTime': fecha.isoformat(),  # Fecha y hora de inicio en formato ISO
            'timeZone': 'Europe/Madrid',  # Zona horaria del evento
        },
        'end': {
            'dateTime': (fecha + timedelta(hours=1)).isoformat(),  # Fin del evento, 1 hora después
            'timeZone': 'Europe/Madrid',
        }
    }

    # Inserta el evento en el calendario principal del usuario
    servicio.events().insert(calendarId='primary', body=evento).execute()

