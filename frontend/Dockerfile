# frontend/Dockerfile
# STAGE 1: Разработка (с hot-reload)
FROM node:20-alpine AS development

WORKDIR /app

# Установка curl для health-check
RUN apk add --no-cache curl  # ← КРИТИЧЕСКИ ВАЖНО

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем исходный код
COPY . .

# Открываем порт Vite
EXPOSE 5173

# Запускаем dev-сервер с host=0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]