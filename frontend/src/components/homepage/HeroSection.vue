<script setup>
defineProps({
  title: { type: String, default: '' },
});
</script>

<template>
  <div class="hero-section">
    <h1 class="hero-title">{{ title }}</h1>
  </div>
</template>

<style scoped>
.hero-section {
  padding: 40px 0 20px;
}

.hero-title {
  font-size: 52px;
  font-weight: 300;
  color: #1a1a2e;
  letter-spacing: 12px;
  margin: 0;
  line-height: 1.3;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
    letter-spacing: 6px;
  }
}
</style>
