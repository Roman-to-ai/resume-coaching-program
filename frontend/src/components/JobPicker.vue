<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  jobs: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  size: { type: Number, default: 20 },
  selectedJobId: { type: String, default: null },
});

const emit = defineEmits(['search', 'select']);

const keyword = ref('');
const experience = ref('');

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.size)));

function onSearch() {
  emit('search', { keyword: keyword.value, experience: experience.value, page: 1 });
}

function onExperienceChange() {
  emit('search', { keyword: keyword.value, experience: experience.value, page: 1 });
}

function goPage(p) {
  if (p < 1 || p > totalPages.value || p === props.page) return;
  emit('search', { keyword: keyword.value, experience: experience.value, page: p });
}
</script>

<template>
  <div class="job-picker">
    <div class="filters">
      <input
        v-model="keyword"
        placeholder="搜索岗位 / 公司 / 技能"
        @keyup.enter="onSearch"
      />
      <select v-model="experience" @change="onExperienceChange">
        <option value="">全部经验</option>
        <option value="1-3年">1-3年</option>
        <option value="3-5年">3-5年</option>
        <option value="5-10年">5-10年</option>
      </select>
      <button class="primary" type="button" @click="onSearch">搜索</button>
    </div>

    <div class="meta">共 {{ total }} 个岗位</div>

    <ul class="job-list">
      <li
        v-for="job in jobs"
        :key="job.job_id"
        :class="{ active: job.job_id === selectedJobId }"
        @click="emit('select', job.job_id)"
      >
        <div class="title">{{ job.title }}</div>
        <div class="sub">
          <span>{{ job.company }}</span>
          <span class="salary">{{ job.salary }}</span>
        </div>
        <div class="tags">
          <span>{{ job.location }}</span>
          <span>{{ job.experience }}</span>
          <span>{{ job.degree }}</span>
        </div>
      </li>
      <li v-if="!jobs.length" class="empty">暂无匹配岗位</li>
    </ul>

    <div class="pager">
      <button type="button" :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button type="button" :disabled="page >= totalPages" @click="goPage(page + 1)">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 8px;
}
.filters input {
  flex: 1;
}
.filters select {
  width: 120px;
}
.meta {
  margin: 10px 0 6px;
  color: var(--muted);
  font-size: 13px;
}
.job-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 460px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
}
.job-list li {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
}
.job-list li:last-child {
  border-bottom: none;
}
.job-list li:hover {
  background: var(--primary-soft);
}
.job-list li.active {
  background: var(--primary-soft);
  border-left: 3px solid var(--primary);
}
.job-list .title {
  font-weight: 600;
}
.job-list .sub {
  display: flex;
  justify-content: space-between;
  color: var(--muted);
  font-size: 13px;
}
.job-list .salary {
  color: var(--danger);
  font-weight: 600;
}
.job-list .tags {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
}
.job-list .tags span {
  background: #f0f2f7;
  padding: 1px 8px;
  border-radius: 999px;
}
.empty {
  text-align: center;
  color: var(--muted);
  padding: 24px !important;
  cursor: default !important;
}
.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 10px;
}
</style>
