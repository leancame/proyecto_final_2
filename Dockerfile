# Usar imagen oficial de Python
FROM python:3.13-slim

# Instalar dependencias del sistema necesarias para Kivy en Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libportaudio2 \
    portaudio19-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libjpeg-dev \
    libfreetype6-dev \
    xclip \
    xsel \
    libmtdev1 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos (usar requirements_linux.txt)
COPY requirements_linux.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements_linux.txt

# Copiar el resto del código
COPY . .

# Exponer puerto si la app lo usa (ajustar si es necesario)
EXPOSE 8000

# Comando para ejecutar la app (ajustar si main.py tiene otro nombre o argumentos)
CMD ["python", "main.py"]
