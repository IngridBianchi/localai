# Base Python para tu webhook
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instalar dependencias para Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto Flask
EXPOSE 5000

# Ejecutar Flask para debug
CMD ["python", "sophie_webhook.py"]

ENV PYTHONPATH=/app
