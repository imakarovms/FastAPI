import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { setupTokenInterceptor } from './utils/tokenManager'

const app = createApp(App)

setupTokenInterceptor()

app.use(router)

app.mount('#app')
