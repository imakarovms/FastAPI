<script setup>
import { onMounted, ref } from 'vue'

const categories = ref([])

onMounted(async () => {
  const res = await fetch('/api/categories/')
  categories.value = await res.json()
})
</script>

<template>
  <div v-for="cat in categories" :key="cat.id">
    {{ cat.name }}
  </div>
</template>