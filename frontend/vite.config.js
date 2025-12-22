import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  // Ключевая настройка для прокси без префикса
  server: {
    host: '0.0.0.0', // Важно для Docker
    port: 5173,
    
    // Проксируем ВСЕ запросы (кроме статики) в бэкенд
    proxy: {
      // Регулярное выражение исключает:
      // - файлы из папок static, assets, public
      // - favicon.ico
      // - все файлы с расширениями .js, .css, .png, .jpg, .jpeg, .gif, .svg
      '^/(?!static|assets|public|favicon.ico|.*\\.(js|css|png|jpg|jpeg|gif|svg)$)': {
        target: 'http://backend:8000', // Имя сервиса в Docker-сети
        changeOrigin: true,
        rewrite: (path) => path, // Не меняем путь
        secure: false, // Отключаем проверку SSL для dev
        ws: true, // Проксируем WebSocket для hot-reload
      }
    }
  }
})