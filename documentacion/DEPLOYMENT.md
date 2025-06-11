# Guía de Despliegue del Proyecto Asistente Virtual

Este documento describe los pasos para crear un entorno Python, instalar dependencias y ejecutar el proyecto.

---

## Requisitos Previos

- Python 3.10 o superior instalado en el sistema.
- pip actualizado.
- Acceso a internet para descargar dependencias y usar APIs externas.

---

## Pasos para Desplegar el Proyecto

### 1. Crear un entorno virtual

Es recomendable usar un entorno virtual para aislar las dependencias del proyecto.

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

- En Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

- En Windows (cmd):

```cmd
.\venv\Scripts\activate.bat
```

- En Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Actualizar pip

```bash
pip install --upgrade pip
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar credenciales de Google

- Asegúrate de tener el archivo `asistente/google/credentials.json` con las credenciales OAuth2.
- Si es la primera vez, el sistema generará un archivo `token.json` tras autenticarte con Google Calendar.

### 6. Ejecutar la aplicación

El punto de entrada principal es `main.py`. Ejecuta:

```bash
python main.py
```

### 7. Uso

- El asistente escuchará comandos de voz.
- Responderá con voz y animaciones sincronizadas.
- Podrás usar comandos para consultar clima, gestionar tareas, buscar en Wikipedia, YouTube, etc.

---

## Notas adicionales

- Asegúrate de tener acceso a internet para que el asistente pueda consultar APIs externas.
- Para detener el asistente, usa Ctrl+C en la terminal.

---

## Despliegue con Docker y NVIDIA Container

Este proyecto incluye configuraciones para desplegar la aplicación usando contenedores Docker, incluyendo soporte para GPU con la carpeta `nvidia_container/`.

### 1. Construir y subir la imagen Docker para `nvidia_container`

Ubícate en la carpeta `nvidia_container/` y ejecuta:

```bash
cd nvidia_container
docker build -t tu_usuario_docker/nvidia_asistente:latest .
docker push tu_usuario_docker/nvidia_asistente:latest
```

Reemplaza `tu_usuario_docker` con tu nombre de usuario en Docker Hub o el repositorio que uses.

### 2. Crear y levantar los contenedores con `docker-compose` en `nvidia_container`

Desde la carpeta `nvidia_container/` ejecuta:

```bash
docker-compose up -d
```

O para construir y levantar en un solo paso:

```bash
docker-compose up --build -d
```

Esto levantará los servicios definidos en `nvidia_container/docker-compose.yml`.

### 3. Construir y subir la imagen Docker para la aplicación principal

Desde la raíz del proyecto ejecuta:

```bash
docker build -t tu_usuario_docker/asistente_app:latest .
docker push tu_usuario_docker/asistente_app:latest
```

### 4. Crear y levantar los contenedores con `docker-compose` en la raíz del proyecto

Desde la raíz del proyecto ejecuta:

```bash
docker-compose up -d
```

O para construir y levantar en un solo paso:

```bash
docker-compose up --build -d
```

Esto levantará los servicios definidos en `docker-compose.yml`, incluyendo la aplicación y la base de datos MySQL.

### 5. Notas adicionales

- Asegúrate de tener Docker instalado y configurado correctamente.
- Para detener los contenedores, usa:

```bash
docker-compose down
```

- Para ver los logs de un contenedor:

```bash
docker logs -f nombre_contenedor
```

- Para listar los contenedores activos:

```bash
docker ps
