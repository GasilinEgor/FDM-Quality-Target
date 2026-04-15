<script setup>
import { onBeforeUnmount, ref } from 'vue'

const fileInput = ref(null)
const isDragging = ref(false)
const imageUrl = ref('')
const fileName = ref('')


function openFileDialog() {
  fileInput.value?.click()
}

function setImageFromFile(file) {
  if (!file) return

  fileName.value = file.name

  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
  }
  imageUrl.value = URL.createObjectURL(file)
}

function onInputChange(event) {
  const file = event.target.files?.[0]
  setImageFromFile(file)
}

function onDragOver(event) {
  event.preventDefault()
  isDragging.value = true
}

function onDragLeave(event) {
  event.preventDefault()
  isDragging.value = false
}

function onDrop(event) {
  event.preventDefault()
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  setImageFromFile(file)
}

onBeforeUnmount(() => {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
  }
})
</script>

<template>
  <div class="photo-load">
    <input
      ref="fileInput"
      class="photo-load__input"
      type="file"
      accept="image/*"
      @change="onInputChange"
    />

    <button
      type="button"
      class="photo-load__dropzone"
      :class="{ 'photo-load__dropzone--dragging': isDragging }"
      @click="openFileDialog"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <template v-if="imageUrl">
        <img class="photo-load__preview" :src="imageUrl" :alt="fileName || 'Загруженное изображение'" />
      </template>
      <template v-else>
        <span class="photo-load__title">Перетащите фотографии сюда</span>
        <span class="photo-load__hint">или нажмите для выбора файлов</span>
      </template>
    </button>
  </div>
</template>

<style scoped>
.photo-load {
  width: 100%;
  max-width: 704px;
  height: 100%;
  max-height: 400px;
}

.photo-load__input {
  display: none;
}

.photo-load__dropzone {
  width: 100%;
  min-height: 280px;
  border: 2px dashed #A60C0C;
  border-radius: 14px;
  background: #3a3a3a;
  color: #2c3e50;
  cursor: pointer;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.photo-load__dropzone--dragging {
  border-color: #3b82f6;
  background: #eef5ff;
}

.photo-load__title {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.photo-load__hint {
  font-size: 14px;
  opacity: 0.8;
  color: white;
}

.photo-load__preview {
  max-width: 100%;
  max-height: 460px;
  object-fit: contain;
  border-radius: 8px;
}

.photo-load__filename {
  margin-top: 10px;
  font-size: 14px;
  color: #3b4a5a;
}

.photo-load__error {
  margin-top: 8px;
  color: #d93025;
  font-size: 14px;
}
</style>