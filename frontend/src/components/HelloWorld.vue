<template>
  <div class="hello">
    <h2>{{ msg }}</h2>
    <p>Это отдельное Vue-приложение, готовое к подключению к FastAPI-бэкенду.</p>
  </div>
</template>

<script setup>
defineProps({
  msg: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
h2 {
  color: #42b983;
}
</style>