<script setup>
import { ref } from 'vue';

const history = ref([{
    'name': 'Название 1',
    'date': '01.01.2000',
    'count': 3,
    'statistic': {
        'first': 1,
        'second': 2,
        'third': 3,
    }
}])
</script>

<template>
<div class="main-history-div">
    <div class="header-div">
        <h1>История</h1>
    </div>
    <div class="history-list-div">
        <div v-for="his in history" class="history-div">
            <div class="info-div">
                <div class="his-header-div">
                    <h1>{{ his.name }}</h1>
                    <p>Дата: {{ his.date }} Фото: {{ his.count }}</p>
                </div>
                <div class="button-div">
                    <button>Загрузить</button>
                </div>
            </div>
            <div class="statistic-div">
                <div v-for="(count, name) in his.statistic" class="block-div">
                    <p class="statistic-count">{{ count }}</p>
                    <p class="statistic-name">{{ name }}</p>
                </div>
            </div>
        </div>
    </div>
</div>
</template>
<style scoped>
.main-history-div {
    width: 100%;
    min-width: 1000px;
    height: 100%;
    background-color: #3a3a3a;
    border: 2px solid #d93025;
    border-radius: 10px;

    display: flex;
    flex-direction: column;
    padding: 20px;
}

.header-div h1 {
    font-size: 24px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: white;
}

.info-div {
    display: flex;
    flex-direction: row;
    width: 100%;
    justify-content: space-around;
}

.his-header-div {
    width: 100%;
    padding: 10px;
}

.his-header-div h1 {
    color: white;
    font-size: 24px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.button-div {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 20px;
}

.button-div button {
    width: 200px;
    height: 50px;
    background-color: #d93025;
    border-radius: 10px;
    color: white;
    font-size: 16px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;

    outline: none; 
    transition: none;
    border: none ;
}

.his-header-div p {
    color: white;
    font-size: 16px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.history-div {
    width: 100%;
    height: 100%;
    background-color: #2a2a2a;
    border:  2px solid #d93025;
    border-radius: 10px;

    display: flex;
    flex-direction: column;
    align-items: center;
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

.statistic-div {
    width: 100%;
    display: flex;
    flex-direction: row;
    gap: 5px;
    align-items: center;
    justify-content: space-around;
    margin: 15px;
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