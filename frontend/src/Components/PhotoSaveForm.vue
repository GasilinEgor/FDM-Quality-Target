<script setup>
defineProps({
  photos: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <section class="photo-save-form">
    <h2 class="photo-save-form__title">Загруженные фотографии</h2>
    <div class="photo-save-form__scroll">
      <p v-if="photos.length === 0" class="photo-save-form__empty">
        Пока нет загруженных фотографий
      </p>
      <div v-else class="photo-save-form__list">
        <article v-for="photo in photos" :key="photo.id" class="photo-save-form__item">
          <img class="photo-save-form__img" :src="photo.url" :alt="photo.name" />
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.photo-save-form {
  width: 320px;
  border: 2px solid #d93025;
  border-radius: 10px;
  background-color: #3a3a3a;
  padding: 12px;
}

.photo-save-form__title {
  margin: 0 0 10px;
  color: #ffffff;
  font-size: 18px;
}

.photo-save-form__scroll {
  height: 420px;
  overflow-y: auto;
  padding-right: 6px;
}

.photo-save-form__empty {
  color: #c7c7c7;
  font-size: 14px;
}

.photo-save-form__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.photo-save-form__item {
  border: 1px solid #596274;
  border-radius: 8px;
  background: #364153;
  padding: 8px;
  border: 2px solid #d93025;
}

.photo-save-form__img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 6px;
  display: block;
}
</style>
