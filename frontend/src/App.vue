<script setup lang="ts">
import Header from './Components/Header.vue'
import Form from './Components/Form.vue';
import History from './Components/History.vue';
</script>
<template>
  <div class="app">
    <Header />
    <div class="form">
      <Form />
    </div>
    <div class="history">
      <History />
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  background-color: #5f5f5f;
}

.app {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.history {
  margin: 20px;
}
</style>
