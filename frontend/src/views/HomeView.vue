<script setup>
import { ref, onMounted } from 'vue'
import CategoryTree from './CategoryTree.vue'

const categoriesTree = ref([])
const selectedCategory = ref(null)
const products = ref([])

onMounted(async () => {
  const res = await fetch('/api/categories/')
  const flat = await res.json()
  categoriesTree.value = buildCategoryTree(flat)
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
  const res = await fetch(`/api/products/categories/${categoryId}`)
  products.value = await res.json()
}
</script>

<template>
  <div style="display: flex; gap: 2rem;">
    <div style="flex: 1;">
      <h2>Категории</h2>
      <CategoryTree :categories="categoriesTree" @select="loadProducts" />
    </div>
    <div style="flex: 2;">
      <h2 v-if="selectedCategory">Товары</h2>
      <div v-if="products.length">
        <div v-for="p in products" :key="p.id" style="margin-bottom: 1rem; padding: 0.5rem; border: 1px solid #ccc;">
          <h3>{{ p.name }}</h3>
          <p>{{ p.description }}</p>
          <p><strong>{{ p.price }} ₽</strong></p>
          <img v-if="p.image_url" :src="p.image_url" :alt="p.name" style="max-width: 100px;" />
        </div>
      </div>
      <p v-else-if="selectedCategory">Нет товаров в этой категории.</p>
    </div>
  </div>
</template>