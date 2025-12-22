<!-- HomeView.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import CategoryTree from './CategoryTree.vue'

const categoriesTree = ref([])

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
</script>

<template>
  <div>
    <h2>Категории</h2>
    <CategoryTree :categories="categoriesTree" />
  </div>
</template>