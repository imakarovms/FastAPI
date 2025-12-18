<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const categories = ref([])
const loading = ref(true)
const error = ref(null)

// Группируем категории по parent_id
const groupedCategories = ref({})

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/')
    categories.value = response.data
    
    // Группируем категории для удобного отображения
    groupedCategories.value = categories.value.reduce((acc, category) => {
      const parentId = category.parent_id || 'root'
      if (!acc[parentId]) {
        acc[parentId] = []
      }
      acc[parentId].push(category)
      return acc
    }, {})
  } catch (err) {
    error.value = 'Ошибка загрузки категорий. Убедитесь, что бэкенд запущен.'
    console.error('API Error:', err)
  } finally {
    loading.value = false
  }
}

const getParentName = (parentId) => {
  const parentCategory = categories.value.find(cat => cat.id === parseInt(parentId))
  return parentCategory ? parentCategory.name : 'Без родителя'
}

onMounted(fetchCategories)
</script>

<template>
  <div class="category-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка категорий...</p>
    </div>
    
    <div v-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCategories" class="retry-btn">Попробовать снова</button>
    </div>
    
    <div v-if="!loading && !error">
      <div v-for="(subcategories, parentId) in groupedCategories" :key="parentId" class="category-group">
        <h2 v-if="parentId !== 'root'">
          {{ getParentName(parentId) }}
        </h2>
        <ul class="category-list">
          <li v-for="category in subcategories" :key="category.id" class="category-item">
            <router-link :to="`/categories/${category.id}`">
              {{ category.name }}
            </router-link>
          </li>
        </ul>
      </div>
      
      <!-- Корневые категории (без родителя) -->
      <div v-if="groupedCategories['root'] && groupedCategories['root'].length > 0" class="category-group">
        <h2>Основные категории</h2>
        <ul class="category-list">
          <li v-for="category in groupedCategories['root']" :key="category.id" class="category-item">
            <router-link :to="`/categories/${category.id}`">
              {{ category.name }}
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
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

.category-group {
  margin-bottom: 2rem;
}

.category-list {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.category-item {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
  transition: all 0.2s;
  text-align: center;
}

.category-item:hover {
  background: #e3f2fd;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.category-item a {
  color: #1976d2;
  text-decoration: none;
  font-weight: 500;
  display: block;
  padding: 0.5rem;
}

.category-item a:hover {
  text-decoration: underline;
}

h2 {
  color: #1976d2;
  border-bottom: 2px solid #1976d2;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
</style>