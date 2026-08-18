const BASE = '/api';

async function request(path, opts = {}) {
  const r = await fetch(BASE + path, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    throw new Error(data.message || data.detail || `请求失败 (${r.status})`);
  }
  return data;
}

export function listJobs(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/jobs${qs ? `?${qs}` : ''}`);
}

export function getJob(id) {
  return request(`/jobs/${encodeURIComponent(id)}`);
}

export function analyze(resumeText, jobId) {
  return request('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, job_id: jobId }),
  });
}

export async function extractPdf(file) {
  const form = new FormData();
  form.append('file', file);
  const r = await fetch(`${BASE}/extract-pdf`, { method: 'POST', body: form });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    throw new Error(data.detail || data.message || 'PDF 解析失败');
  }
  return data.text;
}
