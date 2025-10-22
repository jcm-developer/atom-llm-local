FROM python:3.11-slim

# Evitar buffering y mejorar logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar requirements e instalarlos antes (mejor cacheo)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Crear carpeta de salida para archivos PDF
RUN mkdir -p /app/files

EXPOSE 8000

CMD ["python", "main.py"]