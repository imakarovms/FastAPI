# backend/Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Системные зависимости для asyncpg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \  
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install asyncpg

# Стадия разработки
FROM base AS development
COPY . .


RUN touch app/__init__.py

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]