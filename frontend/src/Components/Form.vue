<script setup>
import { onBeforeUnmount, ref } from 'vue'
import PhotoLoad from './PhotoLoad.vue';
import FormInfo from './FormInfo.vue';
import PhotoSaveForm from './PhotoSaveForm.vue';
import GetMarkButton from './GetMarkButton.vue';
import Statistic from './Statistic.vue';

const uploadedPhotos = ref([])
const formData = ref({
  polymer_type: '',
  polymer_color: '',
  printer: '',
})

function addPhotos(files) {
  for (const file of files) {
    const url = URL.createObjectURL(file)
    uploadedPhotos.value.push({
      id: `${Date.now()}-${Math.random()}`,
      name: file.name,
      url,
      file,
    })
  }
}

onBeforeUnmount(() => {
  uploadedPhotos.value.forEach((photo) => URL.revokeObjectURL(photo.url))
})
</script>
<template>
<div class="main-div">
    <div class="load-form-div">
        <div class="left-column">
            <PhotoSaveForm :photos="uploadedPhotos"/>
        </div>
        <div class="middle-column">
            <PhotoLoad @photos-added="addPhotos"/>
        </div>
        <div class="right-column">
            <FormInfo v-model:form-data="formData"/>
        </div>
    </div>
    <div class="button-div">
        <GetMarkButton :photos="uploadedPhotos" :form-data="formData"/>
    </div>
    <div class="statistic-div">
        <Statistic />
    </div>
</div>
</template>
<style scoped>
.main-div {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.load-form-div {
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.button-div {
    display: flex;
    justify-content: center;
    margin: 20px;
}
</style>