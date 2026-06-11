FROM python:3.13-slim

WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////tmp/workout_app.db

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/. ./
COPY cwiczenia /app/cwiczenia
RUN chmod +x ./start.sh

EXPOSE 8000

CMD ["./start.sh"]
