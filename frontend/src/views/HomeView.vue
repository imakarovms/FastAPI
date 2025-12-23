<!-- src/views/HomeView.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiJson as api } from '@/api/auth.js'
import CategoryTree from './CategoryTree.vue'

const router = useRouter()
const categoriesTree = ref([])
const selectedCategory = ref(null)
const products = ref([])
const cart = ref({ items: [], total_quantity: 0, total_price: 0 })
const loadingCart = ref(false)

// -------- Категории и товары --------
onMounted(async () => {
  try {
    const res = await api.get('/categories/')
    categoriesTree.value = buildCategoryTree(res.data)
  } catch (err) {
    console.error('Ошибка загрузки категорий', err)
  }
})

function buildCategoryTree(categories, parentId = null) {
  return categories
    .filter(cat => cat.parent_id === parentId)
    .map(cat => ({
      ...cat,
      children: buildCategoryTree(categories, cat.id)
    }))
}

async function loadProducts(categoryId) {
  selectedCategory.value = categoryId
  try {
    const res = await api.get(`/products/categories/${categoryId}`)
    products.value = res.data
  } catch (err) {
    console.error('Ошибка загрузки товаров', err)
  }
}

// -------- Корзина --------
async function loadCart() {
  loadingCart.value = true
  try {
    const res = await api.get('/cart/')
    cart.value = {
      ...res.data,
      total_price: parseFloat(res.data.total_price) || 0
    }
    console.log('Корзина загружена:', cart.value)
  } catch (err) {
    console.error('Не удалось загрузить корзину', err)
  } finally {
    loadingCart.value = false
  }
}

async function addToCart(productId) {
  try {
    console.log('Добавляем товар с ID:', productId)
    await api.post('/cart/items', {
      product_id: productId,
      quantity: 1
    })
    console.log('Товар успешно добавлен')
    await loadCart()
  } catch (err) {
    console.error('Ошибка добавления в корзину:', err)
    alert('Не удалось добавить в корзину: ' + (
      err.response?.data?.detail ||
      err.message ||
      'Неизвестная ошибка'
    ))
  }
}

function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}

onMounted(() => {
  loadCart()
})

const cartBadge = computed(() => cart.value.total_quantity)
</script>

<style>
@import '@/assets/styles/main-page.css';
</style>

<template>
  <div id="app">
    <!-- Header -->
    <header class="main-header">
      <div class="header-container">
        <div class="logo-section">
          <div class="logo-icon">🛍️</div>
          <h1 class="logo-text">Магазин</h1>
        </div>
        
        <div class="header-actions">
          <router-link to="/cart" class="cart-button-wrapper">
            <button class="cart-button">
              <span class="cart-icon">🛒</span>
              <span class="cart-text">Корзина</span>
              <span v-if="cartBadge > 0" class="cart-badge">
                {{ cartBadge }}
              </span>
            </button>
          </router-link>
          <button @click="logout" class="logout-button">
            <span class="logout-icon">🚪</span>
            Выйти
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Sidebar with Categories -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>📁 Категории</h3>
          <div class="category-count">{{ categoriesTree.length }}</div>
        </div>
        <div class="category-list-container">
          <div class="category-tree-container">
            <CategoryTree 
              :categories="categoriesTree" 
              :active-category="selectedCategory"
              @select="loadProducts" 
              class="category-tree"
            />
          </div>
        </div>
      </aside>

      <!-- Products Section -->
      <section class="products-section">
        <div class="products-header">
          <h3 v-if="selectedCategory">
            📦 Товары
            <span class="products-count">{{ products.length }}</span>
          </h3>
          <h3 v-else class="select-category-prompt">
            👈 Выберите категорию для просмотра товаров
          </h3>
        </div>

        <div v-if="products.length" class="products-grid">
          <div
            v-for="p in products"
            :key="p.id"
            class="product-card"
          >
            <div class="product-image-placeholder">
              <span class="product-emoji">📦</span>
            </div>
            <div class="product-content">
              <div class="product-header">
                <h4 class="product-title">{{ p.name }}</h4>
                <span class="product-price">{{ p.price }} ₽</span>
              </div>
              <p class="product-description">{{ p.description }}</p>
              <div class="product-footer">
                <button @click="addToCart(p.id)" class="add-to-cart-btn">
                  <span class="cart-icon-small">🛒</span>
                  В корзину
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="selectedCategory" class="empty-products">
          <div class="empty-state">
            <span class="empty-icon">📭</span>
            <p>Нет товаров в этой категории</p>
          </div>
        </div>
      </section>
    </main>

    <!-- Cart Summary Floating Panel -->
    <div v-if="cart.items.length" class="cart-summary-panel">
      <div class="cart-summary-header">
        <h4>🛒 Ваша корзина</h4>
        <button @click="cart.items.length = 0" class="close-summary">×</button>
      </div>
      <div class="cart-summary-total">
        <span>Итого:</span>
        <span class="total-price">{{ (cart.total_price || 0).toFixed(2) }} ₽</span>
      </div>
      <div class="cart-summary-actions">
        <button @click="router.push('/cart')" class="go-to-cart-btn">
          Перейти в корзину
        </button>
      </div>
    </div>
  </div>
</template>