<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['update:form-data'])

const printer_input = ref('')
const polymer_type_input = ref('')
const polymer_color_input = ref('')

watch([printer_input, polymer_type_input, polymer_color_input], () => {
  emit('update:form-data', {
    printer: printer_input.value, 
    polymer_type: polymer_type_input.value, 
    polymer_color: polymer_color_input.value })
}, {deep: true })
</script>

<template>
<div class="main-form-info-div">
    <h1>Информация</h1>
    <div class="input-div">
        <h2>Название принтера</h2>
        <input placeholder="Введите название принтера" v-model="printer_input">
    </div>
    <div class="input-div">
        <h2>Тип пластика</h2>
        <input placeholder="Введите тип пластика" v-model="polymer_type_input">
    </div>
    <div class="input-div">
        <h2>Цвет пластика</h2>
        <input placeholder="Введите цвет пластика" v-model="polymer_color_input">
    </div>
</div>
</template>

<style scoped>
.main-form-info-div {
    width: 350px;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: #3a3a3a;
    border: 2px solid #d93025;
    border-radius: 10px;
    padding-bottom: 20px;
}

h1 {
    font-size: 24px;
    color: white;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

h2 {
    font-size: 20px;
    color: white;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.input-div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
    padding-left: 10px;
}

.input-div input {
    width: 90%;
    font-size: 16px;
    color: white;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    border: #d93025 solid 2px;
    border-radius: 10px;
    background-color: #364153;
    padding: 5px;
}
</style>