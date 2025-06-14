# Usar una imagen base más reciente con Ubuntu 22.04
FROM ubuntu:22.04

# Establecer el directorio de trabajo
WORKDIR /home/app

# Instalar dependencias necesarias, CUDA, y Python
RUN apt update && apt install -y \
    python3-pip python3-dev build-essential git \
    curl wget \
    libstdc++6 libc6 \
    && rm -rf /var/lib/apt/lists/*

# Instalar PyTorch con soporte para CUDA 12.1
RUN pip3 install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --extra-index-url https://download.pytorch.org/whl/cu121

# Clonar el repositorio de text-generation-webui
RUN git clone https://github.com/oobabooga/text-generation-webui.git

# Ir al directorio de la app
WORKDIR /home/app/text-generation-webui

# Copiar el archivo de requirements para evitar usar start_linux.sh en la build
COPY requirements.txt ./ 

# Instalar dependencias Python (puedes usar también el requirements_cpu_only.txt, etc)
RUN pip install --no-cache-dir -r requirements.txt

# Instalar llama-cpp-binaries
RUN pip install https://github.com/oobabooga/llama-cpp-binaries/releases/download/v0.8.0/llama_cpp_binaries-0.8.0+cu124-py3-none-linux_x86_64.whl --no-cache-dir

# Copiar flags si los usas
COPY CMD_FLAGS.txt /home/app/text-generation-webui/

# Exponer los puertos del contenedor
EXPOSE 7860 5000

# Comando final para arrancar la app
CMD ["python3", "server.py", "--listen", "--model", "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf", "--loader", "llamacpp"]
