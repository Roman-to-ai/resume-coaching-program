<script setup>
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  subDescription: { type: String, default: '' },
});
</script>

<template>
  <div class="feature-card">
    <h3 class="feature-title">{{ title }}</h3>
    <p class="feature-desc">{{ description }}</p>
    <p class="feature-sub-desc">{{ subDescription }}</p>
  </div>
</template>

<style scoped>
.feature-card {
  background: #fff;
  border: 1px solid #e4e7ec;
  border-radius: 16px;
  padding: 28px 32px;
  flex: 1;
  min-width: 260px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.feature-card:hover {
  box-shadow: 0 4px 20px rgba(79, 110, 247, 0.1);
  border-color: #c7d2fe;
  transform: translateY(-2px);
}

.feature-title {
  font-size: 20px;
  font-weight: 700;
  color: #4F6EF7;
  margin: 0 0 12px;
}

.feature-desc {
  font-size: 15px;
  color: #344054;
  margin: 0 0 4px;
  line-height: 1.6;
}

.feature-sub-desc {
  font-size: 14px;
  color: #667085;
  margin: 0;
  line-height: 1.6;
}
</style>
