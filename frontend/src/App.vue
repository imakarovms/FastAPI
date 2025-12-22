<template>
  <div id="app">
    <header>
      <h1>Магазин</h1>
    </header>
    <main>
      <HomeView />
    </main>
  </div>
</template>

<script setup>
import HomeView from './views/HomeView.vue'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>