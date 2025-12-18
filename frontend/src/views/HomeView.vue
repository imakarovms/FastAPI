<script setup>
import CategoryList from '@/components/CategoryList.vue';
</script>

<template>
  <div class="home-container">
    <h1>🏠 Главная страница</h1>
    <p class="subtitle">Выберите категорию для просмотра товаров</p>
    
    <CategoryList />
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #1976d2;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.subtitle {
  color: #666;
  font-size: 1.2rem;
  text-align: center;
  margin-bottom: 2rem;
}
</style>