FROM python:3.11-slim

# Instalar dependencias para psycopg2 (PostgreSQL) y utilidades
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar el archivo de dependencias y construir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación (incluyendo app/main.py)
COPY . .

# Comando para iniciar la aplicación FastAPI
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
# Usa uvicorn para iniciar la aplicación principal (app/main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]