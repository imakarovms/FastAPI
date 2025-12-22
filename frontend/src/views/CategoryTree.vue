<script setup>
const props = defineProps({
  categories: { type: Array, required: true }
})
const emit = defineEmits(['select'])

function handleClick(id) {
  emit('select', id)
}
</script>

<template>
  <ul class="category-tree">
    <li v-for="cat in categories" :key="cat.id">
      <span @click="handleClick(cat.id)" class="category-link">{{ cat.name }}</span>
      <CategoryTree
        v-if="cat.children?.length"
        :categories="cat.children"
        @select="emit('select', $event)"
      />
    </li>
  </ul>
</template>

<style scoped>
.category-link {
  cursor: pointer;
  color: #1976d2;
  text-decoration: underline;
}
.category-link:hover {
  opacity: 0.8;
}
</style>