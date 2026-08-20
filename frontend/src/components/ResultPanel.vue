<script setup>
import { computed } from 'vue';

const props = defineProps({ result: { type: Object, default: null } });

const levelMeta = computed(() => {
  const map = {
    high: { label: '高度匹配', color: '#10b981' },
    medium: { label: '中等匹配', color: '#f59e0b' },
    low: { label: '匹配度较低', color: '#ef4444' },
  };
  return map[props.result?.level] || { label: '-', color: '#7c809a' };
});

function importanceLabel(v) {
  return v === 'high' ? '高' : v === 'medium' ? '中' : '低';
}

function severityLabel(v) {
  const map = { error: '错误', warn: '提醒', info: '提示' };
  return map[v] || v;
}
</script>

<template>
  <div v-if="result" class="result-panel">
    <!-- 分数 -->
    <div class="score-card" :style="{ borderColor: levelMeta.color }">
      <div class="score-num" :style="{ color: levelMeta.color }">{{ result.match_score }}</div>
      <div class="score-side">
        <div class="level" :style="{ color: levelMeta.color }">{{ levelMeta.label }}</div>
        <div class="chips">
          <span :class="result.degree_match ? 'ok' : 'no'">
            {{ result.degree_match ? '✓' : '✗' }} 学历匹配
          </span>
          <span :class="result.experience_match ? 'ok' : 'no'">
            {{ result.experience_match ? '✓' : '✗' }} 经验匹配
          </span>
        </div>
      </div>
    </div>

    <!-- 结构化简历 -->
    <div class="section" v-if="result.structured_resume">
      <h4>简历解析</h4>
      <div class="kv">
        <div><b>技能</b>：{{ (result.structured_resume.skills || []).join('、') || '未识别' }}</div>
        <div><b>经验</b>：{{ result.structured_resume.experience_years ?? '未识别' }} 年</div>
        <div><b>学历</b>：{{ result.structured_resume.degree || '未识别' }}</div>
        <div><b>求职方向</b>：{{ result.structured_resume.role || '未识别' }}</div>
        <div v-if="result.structured_resume.summary"><b>摘要</b>：{{ result.structured_resume.summary }}</div>
      </div>
    </div>

    <!-- 命中 -->
    <div class="section">
      <h4>命中技能（{{ result.hits.length }}）</h4>
      <div class="skill-tags">
        <span v-for="h in result.hits" :key="h.skill" class="hit">{{ h.skill }}</span>
        <span v-if="!result.hits.length" class="muted">无</span>
      </div>
    </div>

    <!-- 缺口 -->
    <div class="section">
      <h4>能力缺口（{{ result.gaps.length }}）</h4>
      <ul class="gap-list">
        <li v-for="g in result.gaps" :key="g.skill">
          <span class="gap-skill">{{ g.skill }}</span>
          <span class="gap-importance">重要度 {{ importanceLabel(g.importance) }}</span>
          <div class="gap-suggestion">{{ g.suggestion }}</div>
        </li>
        <li v-if="!result.gaps.length" class="muted">无，技能全部命中</li>
      </ul>
    </div>

    <!-- 简历问题 -->
    <div class="section" v-if="result.issues && result.issues.length">
      <h4>简历问题（{{ result.issues.length }}）</h4>
      <ul class="issue-list">
        <li v-for="(it, i) in result.issues" :key="i" :class="it.severity">
          <span class="issue-field">[{{ severityLabel(it.severity) }}] {{ it.field }}</span>
          {{ it.message }}
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.score-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 2px solid;
  border-radius: 12px;
  background: #fff;
}
.score-num {
  font-size: 56px;
  font-weight: 700;
  line-height: 1;
}
.score-side .level {
  font-size: 20px;
  font-weight: 600;
}
.chips {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}
.chips span {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 13px;
}
.chips .ok {
  background: #ecfdf5;
  color: #10b981;
}
.chips .no {
  background: #fef2f2;
  color: #ef4444;
}
.section {
  margin-top: 16px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
}
.section h4 {
  margin: 0 0 10px;
  font-size: 15px;
}
.kv {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}
.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-tags .hit {
  background: #ecfdf5;
  color: #10b981;
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 13px;
}
.gap-list,
.issue-list {
  margin: 0;
  padding-left: 18px;
}
.gap-list li {
  margin-bottom: 10px;
}
.gap-skill {
  font-weight: 600;
}
.gap-importance {
  margin-left: 8px;
  font-size: 12px;
  color: var(--muted);
}
.gap-suggestion {
  color: var(--muted);
  font-size: 13px;
}
.issue-list li {
  margin-bottom: 6px;
  font-size: 13px;
}
.issue-list li.error {
  color: var(--danger);
}
.issue-list li.warn {
  color: var(--warn);
}
.issue-field {
  font-weight: 600;
}
.muted {
  color: var(--muted);
}
</style>
