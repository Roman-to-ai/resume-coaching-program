# CareerLens 全栈笔试 — 执行计划

> 目标：跑通「简历文本 + 选岗 → 结构化简历问题 / 命中项 / 能力缺口 / 匹配度」的最小纵向闭环，并按 README 提交要求交付。

## 1. 目标与范围

**业务闭环**（来自 README）：

```
学生提交简历文本 + 选择岗位(JD) 
  → 简历数据清洗 → 技能归一化 → 岗位匹配分析(轻度算法)
  → 返回：结构化简历问题、可解释命中项、能力缺口、岗位匹配度
```

**请求链**：`Vue 3 → Node.js BFF → Java/Spring Boot → Python → LLM`

**已锁定的决策**：

| 决策项 | 选择 |
|--------|------|
| LLM 接入 | OpenAI-compatible 接口，有 `OPENAI_API_KEY` 走真实模型，无 key/失败自动降级规则算法 |
| 简历输入 | 主路径文本粘贴，PDF 用 pdfplumber 抽取做成可选加分项 |
| 时间预算 | 1 天（约 8h），优先跑通闭环 + 基础测试，文档从简 |
| commit 规范 | 全中文，Conventional Commits，见 `.claude/skills/git-commit/` |

## 2. 前置发现

1. `TASK.md`、`contracts/openapi.yaml`、`contracts/fixtures/` **缺失** → 接口契约需自行定义（阶段 0）。
2. `.env.example` 缺失 → 需新建。
3. JD 数据已备好：`Java-JD-data/`（1-3年 / 3-5年 / 5-10年，每档约 210 条，`_details.json` 含完整 HTML 描述）。
4. 简历为脱敏 PDF：`脱敏资料/` 20 份（`_qa_report.txt` 记录脱敏情况）。
5. 环境就绪：Docker + MySQL(root/123456) + Node20 + Python3.9+ + JDK17。
6. 端口：前端 5173 / BFF 3000 / 后端 8080 / AI 8001 / MySQL 3306。
7. Git 已初始化：`origin → git@github.com:Roman-to-ai/resume-coaching-program.git`（远程为空仓库）。

## 3. 服务架构

```
Frontend (Vue 3 + Vite)        :5173
    ↓
BFF (Node.js / Express)        :3000   ← 校验 / 编排 / 超时 / 错误映射
    ↓
Backend (Java / Spring Boot)   :8080   ← 岗位领域 API / 编排 / DTO / JPA
    ↓
AI Service (Python / FastAPI)  :8001   ← 清洗 / 归一化 / 匹配 / 打分 / LLM
    ↓
MySQL (careerlens)             :3306
```

## 4. 契约骨架（补缺失的 openapi）

四个服务共用的 3 个接口 + 1 个结果 DTO：

```
GET  /api/jobs            ← 岗位查询（keyword / experience / page）
GET  /api/jobs/{id}       ← 岗位详情
POST /api/analyze         ← { resume_text, job_id } → 匹配结果
```

**匹配结果 DTO**（BFF / Java / Python 对齐）：

```json
{
  "match_score": 82,              // 0-100
  "level": "高",                   // 高 / 中 / 低
  "hits": [                       // 可解释命中项
    { "skill": "Java", "matched_skill": "Java", "source": "简历技能" }
  ],
  "gaps": [                       // 能力缺口
    { "skill": "Spring Cloud", "importance": "高", "suggestion": "..." }
  ],
  "degree_match": true,
  "experience_match": true,
  "structured_resume": {          // 清洗后的结构化简历
    "skills": ["Java", "MySQL"],
    "experience_years": 3,
    "degree": "本科",
    "role": "后端开发"
  },
  "issues": [                     // 简历结构化问题
    { "field": "experience", "severity": "warn", "message": "..." }
  ]
}
```

**数据表**（`careerlens` 库）：

- `jobs`：id、job_id、title、company、salary、location、experience、degree、skills、description、industry、scale …
- `analysis_record`（可选）：匹配历史落库

## 5. 分阶段执行计划（总 ≈ 8h）

| 阶段 | 产出 | 具体任务 | 验收标准 | 时间 |
|------|------|---------|---------|------|
| **0 契约+数据** | OpenAPI + 建库 + JD 导入 | 建 `contracts/openapi.yaml`、`.env.example`、`.gitignore`；建 `careerlens` 库；写脚本导入 `Java-JD-data/*_details.json` 到 `jobs` 表；抽 3~5 份 PDF 简历文本作 fixture | 4 服务字段一致；`jobs` 表有数据 | 1h |
| **1 Python :8001** | AI 分析服务 | `/api/v1/analyze`：清洗 → 技能归一化(词典+LLM) → 匹配打分 → 命中/缺口/结构化问题；LLM 失败降级规则；pytest + fixture | 输入简历+JD 输出结构化结果；pytest 通过 | 1.5h |
| **2 Java :8080** | 岗位+编排 | `Job` 实体/JPA；`GET /api/jobs`、`GET /api/jobs/{id}`；`POST /api/analyze` 编排（取 JD → 调 Python → 合并 DTO）；启动时导入数据 | `mvn test` 通过；查询可用 | 1.5h |
| **3 BFF :3000** | 编排+容错 | 入参校验、30s 超时、错误映射、统一响应；代理 jobs | 串起 Java→Python 链路 | 0.5h |
| **4 前端 :5173** | 有风格 UI | Vite+Vue3，手写设计系统（非裸 AI）；简历输入 + JD 选择/搜索 + 结果页（环形匹配度 + 命中项 + 缺口 + 简历问题） | 结果可解释展示 | 1.5h |
| **5 Docker/Compose** | 一键启动 | 5 服务编排 + healthcheck + `.env` | `docker compose up` 全链路可用 | 0.5h |
| **6 测试+Git** | 全绿+历史 | 各层单测跑通；feature 分支 + 规范 commit | 全绿 + 提交历史完整 | 0.5h |
| **7 交付+答辩** | 文档 | `DELIVERY.md`（启动/测试/部署回滚/取舍/缺口）+ `AI_LOG.md` + 15min 演示脚本 | README 提交要求逐条覆盖 | 1h |

**MVP 路径**：0 → 1 → 2 → 3 → 4 先跑通最小闭环，5/6/7 再补工程化与交付。任意时刻中断都有一个能演示的东西。

## 6. 关键技术点

- **技能归一化**：词典（同义词表，如 `Spring Boot`/`SpringBoot`/`springboot` → `Spring Boot`）+ LLM（有 key 时）。
- **匹配打分**：技能重合度（加权）× 经验年限 × 学历，可解释地输出命中/缺口；分数区间映射 高/中/低。
- **降级策略**：LLM 调用失败或超时 → 自动回退规则算法，保证无 key 环境可跑通。
- **PDF 抽取**（可选加分项）：pdfplumber 提取文本，前端可选上传。

## 7. 交付物 → README 提交要求

| README 要求 | 对应阶段 |
|-------------|---------|
| 1. Git 仓库 + 计时提交历史 | 阶段 6 |
| 2. 可运行代码 + 测试 + Docker/Compose + `DELIVERY.md` | 阶段 1–7 |
| 3. `AI_LOG.md` 会话记录 | 阶段 7 |
| 4. 15 分钟答辩演示请求链 | 阶段 7 |

## 8. Git 工作流

- 分支：`main` + `feature/*`
- commit 规范：全中文 Conventional Commits（见 `.claude/skills/git-commit/`）
- 签名：`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`
- `.gitignore`：`node_modules/`、`venv/`、`target/`、`.env`、`__pycache__/`、`.claude/skills/hue/`（vendored 技能自带 .git）

## 9. 风险与已知缺口（预期）

| 风险 | 缓解 |
|------|------|
| 无 `OPENAI_API_KEY` | 规则算法兜底，保证可跑 |
| PDF 脱敏简历文本质量 | 主路径文本粘贴；PDF 仅加分项 |
| 1 天预算紧张 | MVP 优先，砍非必要加分项 |
| 契约自定与真实题面可能偏差 | 按 README 语义 + 公开 fixture 对齐，`DELIVERY.md` 注明取舍 |
