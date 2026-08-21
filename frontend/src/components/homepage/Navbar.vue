<script setup>
import { ref } from 'vue';

const activeLang = ref('中文');

function switchLang(lang) {
  activeLang.value = lang;
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-left">
      <div class="logo">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="#4F6EF7" opacity="0.15"/>
          <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" fill="#4F6EF7"/>
        </svg>
        <span class="logo-text">deepseek</span>
      </div>
    </div>
    <div class="navbar-right">
      <button class="btn-app" type="button">获取 APP</button>
      <div class="lang-toggle">
        <button
          type="button"
          :class="{ active: activeLang === '中文' }"
          @click="switchLang('中文')"
        >
          中文
        </button>
        <button
          type="button"
          :class="{ active: activeLang === 'EN' }"
          @click="switchLang('EN')"
        >
          EN
        </button>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 40px;
  background: transparent;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #4F6EF7;
  letter-spacing: -0.5px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-app {
  background: transparent;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 14px;
  color: #344054;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-app:hover {
  border-color: #4F6EF7;
  color: #4F6EF7;
}

.lang-toggle {
  display: flex;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  overflow: hidden;
}

.lang-toggle button {
  background: transparent;
  border: none;
  padding: 6px 16px;
  font-size: 13px;
  color: #667085;
  cursor: pointer;
  transition: all 0.2s;
}

.lang-toggle button.active {
  background: #4F6EF7;
  color: #fff;
}

.lang-toggle button:hover:not(.active) {
  background: #f2f4f7;
}
</style>
