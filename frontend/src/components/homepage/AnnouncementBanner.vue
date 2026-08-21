<script setup>
defineProps({
  message: { type: String, default: '' },
  link: { type: String, default: '#' },
});
</script>

<template>
  <div class="announcement">
    <span class="sparkle">&#10024;</span>
    <span class="announcement-text">{{ message }}</span>
    <a v-if="link" :href="link" class="announcement-link" target="_blank" rel="noopener">&#8594;</a>
  </div>
</template>

<style scoped>
.announcement {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  font-size: 15px;
  color: #344054;
}

.sparkle {
  font-size: 14px;
  color: #4F6EF7;
}

.announcement-text {
  line-height: 1.6;
}

.announcement-link {
  color: #4F6EF7;
  text-decoration: none;
  font-size: 16px;
  transition: transform 0.2s;
}

.announcement-link:hover {
  transform: translateX(3px);
}
</style>
