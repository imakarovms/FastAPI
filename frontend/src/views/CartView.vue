<!-- src/views/CartView.vue -->
<template>
  <div style="padding: 20px;">
    <h2>Ваша корзина</h2>
    <div v-if="cart.items.length">
      <div v-for="item in cart.items" :key="item.id" style="margin-bottom: 1rem; padding: 0.5rem; border: 1px solid #ccc;">
        <h4>{{ item.product.name }}</h4>
        <p>{{ item.product.description }}</p>
        <p>Цена: {{ item.product.price }} ₽</p>
        <p>Количество: {{ item.quantity }}</p>
        <p>Итого: {{ (item.product.price * item.quantity).toFixed(2) }} ₽</p>
        <button @click="removeItem(item)" style="background: #e74c3c; color: white; border: none; padding: 0.3rem 0.6rem;">
          Удалить
        </button>
      </div>
      <h3>Общая сумма: {{ cart.total_price.toFixed(2) }} ₽</h3>
    </div>
    <p v-else>Корзина пуста</p>
    <router-link to="/" style="display: inline-block; margin-top: 1rem; color: #2196F3;">← Назад к товарам</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/utils/axios';

const router = useRouter();
const cart = ref({ items: [], total_price: 0 });

async function loadCart() {
  try {
    const res = await apiClient.get('/cart/')
    
    // Преобразуем total_price в число
    cart.value = {
      ...res.data,
      total_price: parseFloat(res.data.total_price) || 0
    }

    console.log('Корзина загружена:', cart.value)
  } catch (err) {
    console.error('Ошибка загрузки корзины:', err)
    router.push('/login')
  }
}

async function removeItem(item) {
  console.log('Удаляем позицию корзины с ID:', item.id);
  try {
    await apiClient.delete(`/cart/items/${item.id}`);
    await loadCart();
  } catch (err) {
    alert('Не удалось удалить товар');
  }
}

onMounted(() => {
  loadCart();
});
</script>