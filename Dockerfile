FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install flask requests instagrapi python-dotenv gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "sophie_webhook:app"]