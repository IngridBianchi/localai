FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar requirements primero
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto (incluido sophie_webhook.py)
COPY . .

# Producción con Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "sophie_webhook:app"]

# Para debug con Flask, cambiar la línea de arriba por:
CMD ["python", "sophie_webhook.py"]

ENV PYTHONPATH=/app
