<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  linkText: { type: String, default: '查看岗位' },
  link: { type: String, default: '#' },
});
</script>

<template>
  <div class="recruit-card">
    <div class="recruit-content">
      <h3 class="recruit-title">{{ title }}</h3>
      <p class="recruit-subtitle">{{ subtitle }}</p>
      <a :href="link" class="recruit-link" target="_blank" rel="noopener">{{ linkText }}</a>
    </div>
  </div>
</template>

<style scoped>
.recruit-card {
  width: 340px;
  min-height: 380px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2d5a9e 0%, #1a3a6e 40%, #0f2847 100%);
  display: flex;
  align-items: flex-end;
  padding: 36px 32px;
  position: relative;
  overflow: hidden;
}

.recruit-card::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(100, 160, 255, 0.25) 0%, transparent 70%);
  border-radius: 50%;
}

.recruit-card::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: -10%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(80, 140, 240, 0.15) 0%, transparent 70%);
  border-radius: 50%;
}

.recruit-content {
  position: relative;
  z-index: 1;
}

.recruit-title {
  font-size: 26px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px;
  line-height: 1.4;
}

.recruit-subtitle {
  font-size: 22px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 24px;
  line-height: 1.4;
}

.recruit-link {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: color 0.2s;
}

.recruit-link:hover {
  color: #fff;
}
</style>
