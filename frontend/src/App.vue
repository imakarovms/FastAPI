<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <header class="header">
      <router-link to="/" class="logo">
        <span class="logo-text">🛍️ Интернет-магазин</span>
      </router-link>
      <nav class="nav">
        <router-link to="/">Категории</router-link>
      </nav>
    </header>
    
    <main class="main-content">
      <RouterView />
    </main>
    
    <footer class="footer">
      <p>© 2025 Интернет-магазин. Все права защищены.</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 2px solid #1976d2;
  margin-bottom: 2rem;
}

.logo {
  text-decoration: none;
  color: #1976d2;
  font-size: 1.8rem;
  font-weight: bold;
}

.logo-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav {
  display: flex;
  gap: 1.5rem;
}

.nav a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav a:hover, .nav a.router-link-active {
  background: #1976d2;
  color: white;
}

.main-content {
  flex: 1;
}

.footer {
  text-align: center;
  padding: 2rem 0;
  margin-top: 2rem;
  border-top: 1px solid #e0e0e0;
  color: #666;
}
</style>