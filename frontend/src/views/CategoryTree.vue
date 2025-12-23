<!-- src/views/CategoryTree.vue -->
<script setup>
const props = defineProps({
  categories: { type: Array, required: true },
  activeCategory: { type: Number, default: null }
})

const emit = defineEmits(['select'])

function handleClick(id) {
  emit('select', id)
}
</script>

<template>
  <ul class="category-tree">
    <li v-for="cat in categories" :key="cat.id" class="category-item">
      <div 
        class="category-main" 
        :class="{ active: activeCategory === cat.id }"
        @click="handleClick(cat.id)"
      >
        <span class="category-icon">
          {{ cat.children?.length ? '📁' : '📄' }}
        </span>
        <span class="category-name">{{ cat.name }}</span>
        <span v-if="cat.children?.length" class="category-count">
          {{ cat.children.length }}
        </span>
      </div>
      <div v-if="cat.children?.length" class="category-children-wrapper">
        <CategoryTree
          :categories="cat.children"
          :active-category="activeCategory"
          @select="emit('select', $event)"
        />
      </div>
    </li>
  </ul>
</template>

<style scoped>
@import '@/assets/styles/category-tree.css';
</style>