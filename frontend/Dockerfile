# Этап разработки
FROM node:20-alpine AS development

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm ci

# Копируем исходный код
COPY . .

# Запускаем dev-сервер Vite
CMD ["npm", "run", "dev"]