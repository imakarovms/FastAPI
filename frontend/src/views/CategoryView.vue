<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const category = ref(null)
const products = ref([])
const loading = ref(true)
const error = ref(null)

const fetchCategoryData = async () => {
  try {
    loading.value = true
    
    // Получаем данные категории
    const categoryResponse = await axios.get(`/api/categories/${route.params.id}`)
    category.value = categoryResponse.data
    
    // Получаем товары в этой категории (заглушка - в реальном проекте будет свой эндпоинт)
    const productsResponse = await axios.get('/api/products/')
    products.value = productsResponse.data.filter(product => 
      product.category_id === parseInt(route.params.id)
    )
    
  } catch (err) {
    error.value = 'Ошибка загрузки данных категории'
    console.error('API Error:', err)
  } finally {
    loading.value = false
  }
}

// Загружаем данные при монтировании компонента
onMounted(fetchCategoryData)

// Следим за изменением ID категории при навигации
watch(() => route.params.id, () => {
  fetchCategoryData()
})
</script>

<template>
  <div class="category-page">
    <router-link to="/" class="back-link">← Вернуться к категориям</router-link>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка данных категории...</p>
    </div>
    
    <div v-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCategoryData" class="retry-btn">Попробовать снова</button>
    </div>
    
    <div v-if="!loading && !error && category">
      <h1>{{ category.name }}</h1>
      
      <div v-if="products.length > 0" class="products-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <h3>{{ product.name }}</h3>
          <p class="price">{{ product.price }} ₽</p>
          <p class="description">{{ product.description || 'Описание отсутствует' }}</p>
          <button class="add-to-cart">Добавить в корзину</button>
        </div>
      </div>
      
      <div v-else class="no-products">
        <p>В этой категории пока нет товаров</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.back-link {
  display: inline-block;
  color: #1976d2;
  text-decoration: none;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.back-link:hover {
  text-decoration: underline;
}

.loading, .error {
  padding: 1rem;
  margin: 1rem 0;
}

.loading {
  background-color: #e3f2fd;
  border-radius: 4px;
  text-align: center;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left: 4px solid #1976d2;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  text-align: center;
}

.retry-btn {
  background: #c62828;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  font-size: 1rem;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #b71c1c;
}

h1 {
  color: #1976d2;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
}

.no-products {
  text-align: center;
  padding: 2rem;
  background: #f5f5f5;
  border-radius: 8px;
  color: #666;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.product-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.2s;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.product-card h3 {
  color: #333;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.price {
  color: #1976d2;
  font-weight: bold;
  font-size: 1.2rem;
  margin: 0.5rem 0;
}

.description {
  color: #666;
  font-size: 0.9rem;
  margin: 0.5rem 0;
  min-height: 40px;
}

.add-to-cart {
  background: #1976d2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  margin-top: 1rem;
  font-weight: 500;
  transition: background 0.2s;
}

.add-to-cart:hover {
  background: #1565c0;
}
</style>