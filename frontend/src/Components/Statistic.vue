<script setup>
import { ref } from 'vue';

const defects = ref({'first': 1,
                    'second': 2,
                    'third': 3,
                    'fourth': 4,
                    'fifth': 5,
})
</script>
<template>
<div class="main-div">
    <div class="title-div">
        <h1>Результат</h1>
    </div>
    <div class="statistic-blocks-div">
        <div class="block-div" v-for="(count, name) in defects">
            <p class="statistic-count">{{ count }}</p>
            <p class="statistic-name">{{ name }}</p>
        </div>
    </div>
    <div class="mark-div">

    </div>
    <div class="buttons-div">
        <button class="save-button">Сохранить</button>
        <button class="retry-button">Ещё раз</button>
    </div>
</div>
</template>

<style scoped>
.main-div {
    width: 100%;
    height: 100%;
    background-color: #3a3a3a;
    border: 2px solid #d93025;
    border-radius: 20px;
}

.title-div {
    text-align: center;
}

.title-div h1 {
    font-size: 32px;
    color: white;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.buttons-div {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
}

.save-button {
    width: 150px;
    height: 50px;
    text-align: center;
    background-color: #d93025;
    border-radius: 10px;

    font-size: 20px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: white;

    border: 2px solid #d93025;
    outline: none; 
    transition: none;
}

.retry-button {
    width: 150px;
    height: 50px;
    text-align: center;
    background-color: #3a3a3a;

    font-size: 20px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: white;

    border: 2px solid #d93025;
    border-radius: 10px;

    outline: none; 
    transition: none;
}

.statistic-blocks-div {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 40px;
    margin: 0px 20px 20px 20px;
}

.block-div {
    width: 220px;
    height: 100px;
    background-color: #ffe9cc;
    border: 2px solid #d93025;
    border-radius: 10px;

    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0px;
    padding: 5px;
}

.statistic-count {
    font-size: 32px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: #d93025;
    margin: 5px;
    font-weight: 700;
}

.statistic-name {
    font-size: 20px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: black;
    margin: 5px;
}
</style>