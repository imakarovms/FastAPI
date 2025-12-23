// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/views/LoginView.vue';
import HomeView from '@/views/HomeView.vue';
import CartView from '@/views/CartView.vue'; 

const routes = [
  { path: '/login', component: LoginView },
  { path: '/', component: HomeView },
  { path: '/cart', component: CartView }, // ← новый маршрут
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Защита маршрутов
router.beforeEach((to, from, next) => {
  const publicPages = ['/login'];
  const authRequired = !publicPages.includes(to.path);
  const accessToken = localStorage.getItem('access_token');

  if (authRequired && !accessToken) {
    return next('/login');
  }

  next();
});

export default router;