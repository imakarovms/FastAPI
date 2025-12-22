<!-- CategoryTree.vue -->
<script setup>
defineProps({
  categories: {
    type: Array,
    required: true
  }
})
</script>

<template>
  <ul class="category-tree">
    <li v-for="cat in categories" :key="cat.id">
      {{ cat.name }}
      <CategoryTree v-if="cat.children?.length" :categories="cat.children" />
    </li>
  </ul>
</template>

<style scoped>
.category-tree {
  list-style: none;
  padding-left: 20px;
}
.category-tree > li {
  margin: 4px 0;
}
</style>