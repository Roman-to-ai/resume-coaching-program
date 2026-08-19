# DELIVERY.md — 交付说明

> CareerLens AI 求职平台全栈笔试交付文档。
> 覆盖：架构、快速启动、接口契约、核心算法、测试、验证结果、取舍、README 提交要求对照、答辩脚本。

---

## 1. 项目概述

「简历投递 + 岗位匹配」最小纵向闭环：

```
学生提交简历文本 + 选择岗位(JD)
  → 简历数据清洗 → 技能归一化 → 岗位匹配分析（轻度算法）
  → 返回：结构化简历问题、可解释命中项、能力缺口、岗位匹配度
```

**技术栈**：Vue 3 (Vite) → Node.js/Express BFF → Java/Spring Boot → Python/FastAPI → MySQL，LLM 为 OpenAI-compatible 接口 + 规则兜底。

---

## 2. 架构与请求链

```
Frontend (Vue 3 + Vite)        :5173  简历输入 / 岗位搜索 / 结果展示
    ↓  /api/*
BFF (Node.js / Express)        :3000  统一入口 / 转发 / 错误映射 / 超时
    ↓  /api/v1/jobs, /api/v1/analyze
Backend (Java / Spring Boot)   :8080  岗位领域 API / 编排 / JPA / JD 导入
    ↓  POST /api/v1/analyze
AI Service (Python / FastAPI)  :8001  清洗 / 归一化 / 匹配打分 / PDF 提取 / LLM
    ↓
MySQL (careerlens)             :3306  jobs 表（630 条岗位）
```

| 服务 | 端口 | 职责 | 关键文件 |
|------|------|------|---------|
| frontend | 5173 | Vue3 单页 UI | `frontend/src/App.vue`、`components/*` |
| bff | 3000 | 聚合/转发/错误映射 | `bff/src/server.js` |
| backend | 8080 | 岗位查询 + 分析编排 + JD 种数 | `backend/src/main/java/com/carelens/backend/` |
| ai-service | 8001 | 清洗/归一化/匹配/PDF | `ai-service/app/{cleaner,normalizer,matcher,llm}.py` |
| mysql | 3306 | 岗位数据 | `db/schema.sql` |

---

## 3. 目录结构

```
resume-coaching-program/
├── frontend/            Vue 3 + Vite 前端
├── bff/                 Node.js/Express 聚合层
├── backend/             Java/Spring Boot 后端（含 H2 集成测试）
├── ai-service/          Python/FastAPI AI 服务（含 pytest）
├── contracts/           openapi.yaml（接口契约）
├── db/                  schema.sql（建库脚本）
├── data/                JD 抓取数据 + 简历 fixture + 抽取脚本
├── scripts/             smoke_test.py（端到端冒烟测试）
├── docs/references/     COMMIT.md（提交规范）
├── .claude/skills/      git-commit 技能
├── docker-compose.yml   五服务一键编排
├── PLAN.md              执行计划
├── AI_LOG.md            AI 协作会话记录
└── DELIVERY.md          本文档
```

---

## 4. 快速启动

### 方式 A：Docker Compose（一键）

```bash
docker compose up --build
```

> 注：需 Docker 可访问镜像仓库。国内环境请在 Docker Desktop 配置 registry 镜像加速（如 DaoCloud/阿里云），否则拉取 `mysql:8.0` 等基础镜像会超时。

### 方式 B：本地启动（无需 Docker 构建，复用已有 MySQL）

依赖：JDK 17、Maven 3.9、Node 20、Python 3.11（venv）、MySQL（`root/123456`，库 `careerlens`）。

```bash
# 0) 建库（若不存在）
docker exec mysql8 mysql -uroot -p123456 \
  -e "CREATE DATABASE IF NOT EXISTS careerlens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 1) AI 服务
cd ai-service && python -m venv venv && ./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python -m uvicorn app.main:app --port 8001

# 2) 后端（启动时自动导入 630 条岗位）
cd backend && mvn spring-boot:run

# 3) BFF
cd bff && npm install && npm start

# 4) 前端
cd frontend && npm install && npm run dev
# 浏览器打开 http://localhost:5173
```

环境变量见根目录 `.env.example`（OPENAI_API_KEY 缺省时自动走规则算法兜底）。

> 快捷方式（Git Bash，复用已有 mysql8 容器）：`bash scripts/start_all.sh` 一键后台拉起四服务，`bash scripts/stop_all.sh` 停止；日志在 `logs/*.log`。

---

## 5. 接口契约

完整定义见 `contracts/openapi.yaml`，字段统一 **snake_case**。

```
GET  /api/v1/jobs?keyword=&experience=&page=&size=   → JobListResponse
GET  /api/v1/jobs/{job_id}                          → JobDetail
POST /api/v1/analyze   { resume_text, job_id }      → MatchResult
POST /api/v1/extract-pdf  (multipart file)          → { text }
```

**MatchResult**（四服务对齐）：

```json
{
  "match_score": 70,
  "level": "high",              // high / medium / low
  "hits":   [{"skill":"Java","matched_skill":"Java","source":"技能列表"}],
  "gaps":   [{"skill":"大数据","importance":"high","suggestion":"建议…"}],
  "degree_match": true,
  "experience_match": true,
  "structured_resume": {
    "skills": ["Java","MySQL"], "experience_years": 3,
    "degree": "本科", "role": null, "summary": "…"
  },
  "issues": [{"field":"role","severity":"info","message":"未识别到求职意向"}]
}
```

---

## 6. 核心算法（Python 侧，确定性、可解释）

| 环节 | 实现 | 文件 |
|------|------|------|
| 数据清洗 | 去除 PDF 残片/base64 噪声；抽取学历/年限/求职方向/摘要 | `cleaner.py` |
| 技能归一化 | 词典别名 → 规范名（~50 技能）；LLM 优先、规则兜底 | `normalizer.py` |
| 匹配打分 | 技能 60 + 经验 25 + 学历 15；分数映射 high(≥70)/medium(≥40)/low | `matcher.py` |
| 命中/缺口 | JD 技能逐一比对简历技能集；前 3 项重要度 high | `matcher.py` |
| LLM 接入 | OpenAI-compatible `/chat/completions`，失败/无 key 自动降级规则 | `llm.py` |

打分公式：`score = round(60 * hits/n + 25*[经验匹配] + 15*[学历匹配])`

---

## 7. 测试

| 层 | 命令 | 结果 |
|----|------|------|
| Python 单测 | `cd ai-service && pytest` | 15/15 通过 |
| Java 单测 + H2 集成 | `cd backend && mvn test` | 5/5 通过（含 JD 导入、岗位接口、snake_case 反序列化、分析编排） |
| 前端构建 | `cd frontend && npm run build` | 通过 |
| 端到端冒烟 | `python scripts/smoke_test.py` | 见 §8 |

---

## 8. 验证结果（实际联调）

本次联调（本地 MySQL + 本地四服务）实测：

```
jobs list : 200, total=630
detail    : 200, 含 description
analyze   : 200
  → match_score=70, level=high
  → hits   = [Java, Docker, MySQL]
  → gaps   = [大数据, PostgreSQL, Python]
  → degree_match=true, experience_match=true
  → structured_resume.skills=[Spring Boot, MyBatis, Spring, Docker, MySQL, Redis, Java, Git]
  → issues = [未识别到求职意向]
```

PDF 提取：`/api/v1/extract-pdf` 返回结构化中文简历文本（3517 字符）。

---

## 9. 取舍与已知缺口

| 项 | 取舍 | 说明 |
|----|------|------|
| LLM 无 key | 规则算法兜底 | 保证无 `OPENAI_API_KEY` 环境可完整跑通 |
| 简历输入 | 文本粘贴为主，PDF 可选 | PDF 经 pypdf 提取（非 pdfplumber，更轻） |
| JD 数据导入 | Java 启动时 `CommandLineRunner` 读 classpath JSON | 免去 Python 的 MySQL 驱动依赖 |
| MatchResult 建模 | Java 以 `Map` 透传 Python 结果 | 避免 6 个嵌套 DTO 的重复建模 |
| `analysis_record` 表 | 未实现 | schema.sql 中保留为可选项，未接入代码 |
| 真实 LLM 效果 | 未实测 | 无 API key，仅验证规则路径与 LLM 调用代码路径 |
| 分支策略 | 直提 `main` | 1 天预算下简化，提交历史仍符合 Conventional Commits |

---

## 10. README 提交要求对照

| 要求 | 交付 |
|------|------|
| 1. Git 仓库 + 计时提交历史 | 本仓库，全中文 Conventional Commits + `Co-Authored-By`，随开发逐步提交 |
| 2. 可运行代码 + 测试 + Docker/Compose + DELIVERY.md | 五服务 + 20 项测试 + `docker-compose.yml` + 本文档 |
| 3. AI_LOG.md 会话记录 | `AI_LOG.md` |
