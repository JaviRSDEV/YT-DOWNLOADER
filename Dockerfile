# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Instalar FFmpeg (imprescindible para yt-dlp)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Definir directorio de trabajo
WORKDIR /app

# 4. Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código del proyecto
COPY . .

# 6. Exponer el puerto
EXPOSE 8000

# 7. Arrancar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
