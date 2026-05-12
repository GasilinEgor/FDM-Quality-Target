<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const props = defineProps({
  photos: {
    type: Array,
    default: () => []
  },
  formData: {
    type: Object,
    default: () => ({})
  }
})

async function sendData() {
  const formData = new FormData()

  props.photos.forEach(photo => {
    formData.append('photos', photo.file)
  })

  formData.append('plastic_type', props.formData.polymer_type || '')
  formData.append('plastic_color', props.formData.polymer_color || '')
  formData.append('printer_name', props.formData.printer || '')

  for (const [key, value] of formData.entries()) {
    alert(key + value)
}

  try {
    const response = await axios.post(
      'http://127.0.0.1:8000/photos/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    console.log(response.data)
  } catch (error) {
    console.log(error.response?.data)
  }
}
</script>
<template>
<div>
    <button class="get_mark_button" type="button" @click="sendData">Получить оценку</button>
</div>
</template>


<style scoped>
.get_mark_button {
    width: 200px;
    height: 50px;
    background-color: #d93025;

    font-size: 16px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: white;
    border-radius: 10px;

    border: none; 
    outline: none; 
    transition: none;
}
</style>