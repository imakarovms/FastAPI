// src/services/api.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.DEV 
  ? '/api'  // будет перенаправлен через прокси
  : 'https://your-production-api.com/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Интерсептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Обработка неавторизованного доступа
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);