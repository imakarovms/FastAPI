# backend/Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Стадия разработки
FROM base AS development

# Копируем ВЕСЬ код, включая entrypoint.sh
COPY . .

# Гарантируем, что entrypoint.sh исполняем (на случай, если права не сохранились)
RUN chmod +x /app/entrypoint.sh

# Запускаем через скрипт
CMD ["/app/entrypoint.sh"]