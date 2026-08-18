import express from 'express';
import cors from 'cors';
import multer from 'multer';
import { config } from './config.js';

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
});

/** 健康检查。 */
app.get('/health', (req, res) => res.json({ status: 'ok', service: 'bff' }));

/** 岗位列表（透传 Java）。 */
app.get('/api/jobs', (req, res) => {
  const qs = new URLSearchParams(req.query).toString();
  forward(res, `${config.backendBaseUrl}/api/v1/jobs${qs ? `?${qs}` : ''}`);
});

/** 岗位详情（透传 Java）。 */
app.get('/api/jobs/:id', (req, res) => {
  forward(res, `${config.backendBaseUrl}/api/v1/jobs/${encodeURIComponent(req.params.id)}`);
});

/** 匹配分析（透传 Java，Java 内部调用 Python）。 */
app.post('/api/analyze', (req, res) => {
  forward(res, `${config.backendBaseUrl}/api/v1/analyze`, { method: 'POST', body: req.body });
});

/** PDF 文本提取（透传 Python）。 */
app.post('/api/extract-pdf', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ code: 'BAD_REQUEST', message: '缺少 PDF 文件' });
  }
  const form = new FormData();
  form.append('file', new Blob([req.file.buffer], { type: req.file.mimetype }), req.file.originalname || 'resume.pdf');
  try {
    const r = await fetch(`${config.aiServiceUrl}/api/v1/extract-pdf`, { method: 'POST', body: form });
    const data = await r.json();
    res.status(r.status).json(data);
  } catch (e) {
    res.status(502).json({ code: 'UPSTREAM_ERROR', message: `AI 服务调用失败: ${e.message}` });
  }
});

/** 通用 JSON 转发。 */
async function forward(res, url, opts = {}) {
  try {
    const r = await fetch(url, {
      method: opts.method || 'GET',
      headers: opts.body ? { 'Content-Type': 'application/json' } : undefined,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    const text = await r.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
    res.status(r.status).json(data);
  } catch (e) {
    res.status(502).json({ code: 'UPSTREAM_ERROR', message: `后端服务调用失败: ${e.message}` });
  }
}

app.listen(config.port, () => {
  console.log(`[bff] listening on :${config.port} (backend=${config.backendBaseUrl}, ai=${config.aiServiceUrl})`);
});
