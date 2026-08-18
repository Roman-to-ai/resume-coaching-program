<script setup>
import { ref, onMounted, computed } from 'vue';
import { listJobs, getJob, analyze } from './api';
import ResumeInput from './components/ResumeInput.vue';
import JobPicker from './components/JobPicker.vue';
import ResultPanel from './components/ResultPanel.vue';

const resumeText = ref('');
const jobs = ref([]);
const total = ref(0);
const page = ref(1);
const size = 20;
const selectedJob = ref(null);
const result = ref(null);
const analyzing = ref(false);
const error = ref('');

const canAnalyze = computed(() => resumeText.value.trim() && selectedJob.value);

const metaParts = computed(() => {
  const j = selectedJob.value;
  if (!j) return [];
  return [j.company, j.location, j.experience, j.degree, j.company_industry, j.company_scale, j.company_stage]
    .filter(Boolean);
});

const jobDescription = computed(() => stripHtml(selectedJob.value?.description || ''));

function stripHtml(html) {
  if (!html) return '';
  return html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|li|h[1-6]|tr|section)>/gi, '\n')
    .replace(/<li[^>]*>/gi, '• ')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

async function loadJobs({ keyword = '', experience = '', page: p = 1 } = {}) {
  try {
    const data = await listJobs({ keyword, experience, page: p, size });
    jobs.value = data.items;
    total.value = data.total;
    page.value = p;
  } catch (e) {
    error.value = `岗位加载失败：${e.message}`;
  }
}

async function selectJob(jobId) {
  try {
    selectedJob.value = await getJob(jobId);
    result.value = null;
  } catch (e) {
    error.value = `岗位详情加载失败：${e.message}`;
  }
}

async function runAnalyze() {
  error.value = '';
  if (!resumeText.value.trim()) {
    error.value = '请先填写简历内容';
    return;
  }
  if (!selectedJob.value) {
    error.value = '请先选择目标岗位';
    return;
  }
  analyzing.value = true;
  try {
    result.value = await analyze(resumeText.value, selectedJob.value.job_id);
    document.getElementById('result')?.scrollIntoView({ behavior: 'smooth' });
  } catch (e) {
    error.value = `分析失败：${e.message}`;
  } finally {
    analyzing.value = false;
  }
}

onMounted(() => loadJobs());
</script>

<template>
  <header class="header">
    <div class="brand">
      <span class="logo">CL</span>
      <h1>CareerLens · AI 求职平台</h1>
    </div>
    <p class="tagline">粘贴简历 → 选择岗位 → 获得可解释的匹配分析与改进建议</p>
  </header>

  <main>
    <div class="grid">
      <section class="card">
        <h2>① 填写简历</h2>
        <ResumeInput v-model="resumeText" />
      </section>

      <section class="card">
        <h2>② 选择岗位</h2>
        <JobPicker
          :jobs="jobs"
          :total="total"
          :page="page"
          :size="size"
          :selected-job-id="selectedJob?.job_id"
          @search="loadJobs"
          @select="selectJob"
        />
      </section>
    </div>

    <div v-if="selectedJob" class="card selected-job">
      <h3 class="sj-heading">岗位详情</h3>
      <div class="sj-title">
        <b>{{ selectedJob.title }}</b>
        <span class="salary">{{ selectedJob.salary }}</span>
      </div>
      <div class="sj-meta">{{ metaParts.join(' · ') }}</div>
      <div class="sj-skills">技能：{{ selectedJob.skills }}</div>
      <div v-if="selectedJob.welfare" class="sj-welfare">福利：{{ selectedJob.welfare }}</div>
      <div class="sj-desc">
        <h4>岗位描述</h4>
        <pre class="sj-desc-body">{{ jobDescription }}</pre>
      </div>
      <a v-if="selectedJob.url" class="sj-url" :href="selectedJob.url" target="_blank" rel="noopener">查看原岗位 →</a>
    </div>

    <div class="analyze-bar">
      <button class="primary big" type="button" :disabled="!canAnalyze || analyzing" @click="runAnalyze">
        {{ analyzing ? '分析中…' : '开始匹配分析' }}
      </button>
      <span v-if="error" class="error">{{ error }}</span>
    </div>

    <section id="result" class="card">
      <h2>③ 分析结果</h2>
      <ResultPanel :result="result" />
      <p v-if="!result" class="placeholder">填写简历并选择岗位后，点击「开始匹配分析」查看结果</p>
    </section>
  </main>
</template>

<style scoped>
.header {
  padding: 8px 0 20px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--primary);
  color: #fff;
  font-weight: 700;
  border-radius: 10px;
}
h1 {
  margin: 0;
  font-size: 22px;
}
.tagline {
  margin: 6px 0 0 52px;
  color: var(--muted);
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
h2 {
  margin: 0 0 14px;
  font-size: 16px;
}
.selected-job {
  margin-top: 20px;
}
.sj-heading {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--muted);
  font-weight: 600;
}
.sj-title {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
}
.sj-title .salary {
  color: var(--danger);
  font-weight: 700;
}
.sj-meta {
  margin-top: 6px;
  color: var(--muted);
  font-size: 13px;
}
.sj-skills {
  margin-top: 6px;
  font-size: 13px;
  color: var(--muted);
}
.sj-welfare {
  margin-top: 6px;
  font-size: 13px;
  color: var(--muted);
}
.sj-desc {
  margin-top: 12px;
}
.sj-desc h4 {
  margin: 0 0 8px;
  font-size: 14px;
}
.sj-desc-body {
  margin: 0;
  padding: 12px;
  max-height: 280px;
  overflow-y: auto;
  background: #fafbfd;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
}
.sj-url {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
  color: var(--primary);
  text-decoration: none;
}
.sj-url:hover {
  text-decoration: underline;
}
.analyze-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 20px 0;
}
button.big {
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
}
.error {
  color: var(--danger);
  font-size: 13px;
}
#result {
  scroll-margin-top: 20px;
}
.placeholder {
  color: var(--muted);
  text-align: center;
  padding: 30px 0;
}
</style>
