# AI_LOG.md — AI 协作会话历史

> 记录本项目与 AI 的会话历史（README 提交要求第 3 条）。
> 每次有意义的问题/决策/产出都追加记录，保持时间顺序。

## 会话元信息

- 项目：CareerLens AI 求职平台全栈笔试（resume-coaching-program）
- 工作目录：`E:\resume-coaching-program`
- 模型：`deepseek-v4-flash`（用户通过 `/model` 手动设置）
- 远程仓库：`git@github.com:Roman-to-ai/resume-coaching-program.git`
- 记录起始：2026-08-18

---

## 时间线

### 2026-08-18

#### 1. 生成执行计划
- **用户提问**：根据 README.md 文件，生成一份可执行性完成业务的计划表给我确认。
- **AI 动作**：读取 README / TASK / LOCAL_SETUP / 脱敏资料 / Java-JD-data，发现 `TASK.md` 与 `contracts/` 缺失、`.env.example` 缺失；提出 8 阶段计划，并询问 3 个决策问题。
- **用户决策**：LLM + 规则兜底 / 简历文本粘贴 + PDF 可选 / 时间预算 1 天左右。
- **产出**：（对话中确认，后写入 `PLAN.md`）

#### 2. Git 仓库初始化
- **用户提问**：已初始化 git 仓库 `git@github.com:Roman-to-ai/resume-coaching-program.git`，帮忙把仓库拉取到本地。
- **AI 动作**：确认远程为空仓库（无 refs）；本地 `git init -b main`，关联 `origin`；确认 git 身份 `roman / 1121683285@qq.com`；指出 `.claude/skills/hue/.git` 嵌套仓库问题。
- **产出**：本地仓库与远程关联就绪。

#### 3. Git commit 规范 skill
- **用户提问**：找一个开源的 AI 代码，然后 git 提交规范的 skill，后期提交按此规范进行。
- **AI 动作**：检索并拉取开源 skill `rhino-ty/principled-git-commit`（MIT，基于 Conventional Commits 1.0.0），适配为本项目项目级 skill。
- **产出**：`.claude/skills/git-commit/SKILL.md` + `docs/references/COMMIT.md`

#### 4. commit 语言改为中文
- **用户提问**：全中文 commit。
- **AI 动作**：更新 `COMMIT.md` §1 语言规则为「默认中文，type/scope 令牌与英文技术词保留原文」；同步 SKILL.md 中全部 commit 示例为中文。
- **产出**：commit 规范落地为全中文。

#### 5. 输出计划文件
- **用户提问**：输出一份计划的 .md 我看看。
- **AI 动作**：将最终执行计划（含 8 阶段、契约骨架、交付物映射、风险）写入项目根目录。
- **产出**：`PLAN.md`

#### 6. 建立本记录
- **用户提问**：把刚刚的提问记录到 AI_LOG.md，后续所有对话都记录到此文件。
- **AI 动作**：创建本文件；约定后续所有会话持续追加记录。
- **产出**：`AI_LOG.md`（本文件）

#### 7. 初始化提交并开始执行
- **用户提问**：先提交一次 git 作为初始化，然后按计划执行。
- **AI 动作**：建 `.gitignore`；按 `git-commit` 规范显式暂存（排除 vendored 技能目录）；secrets grep 通过；完成初始提交。
- **产出**：commit `c3b0c76`（41 文件，全中文 Conventional Commits + Co-Authored-By）

#### 8. 阶段 0：契约与数据准备
- **AI 动作**：建 `contracts/openapi.yaml`（3 接口 + 共享 DTO）、`db/schema.sql`（jobs + analysis_record）、`.env.example`；写 `data/extract_resumes.py` 抽取 20 份脱敏简历 PDF 为 fixture。
- **决策**：JD 导入推迟到阶段 2，由 Java 后端 CommandLineRunner 读取 JSON 种入 MySQL（免去 Python 的 MySQL 驱动依赖）。
- **产出**：`contracts/openapi.yaml`、`db/schema.sql`、`.env.example`、`data/fixtures/resumes/*.txt`（20 份）

#### 9. 阶段 1：Python AI 服务
- **AI 动作**：实现 `cleaner/normalizer/matcher/llm` 四模块 + `/api/v1/analyze`；技能归一化词典（~50 技能）+ LLM 优先、规则兜底；打分 技能60+经验25+学历15。
- **产出**：`ai-service/app/*`，15 项 pytest 通过；修复 MyBatis-Plus 词典重复项。

#### 10. 阶段 2：Java 后端
- **AI 动作**：Job 实体/JPA、`GET /api/v1/jobs`（关键词/经验筛选+分页）、`GET /api/v1/jobs/{id}`、`POST /api/v1/analyze`（透传 Python MatchResult）；`JdDataImporter` 启动时从 classpath 导入 630 条岗位；Jackson 全局 SNAKE_CASE。
- **产出**：`backend/`，`mvn test` 通过（含无 DB 依赖的 JdDataParserTest）。

#### 11. 阶段 3：Node BFF
- **AI 动作**：Express 聚合层，转发 jobs/analyze 到 Java、extract-pdf 到 Python（multer 2.x），统一 502 错误映射。
- **产出**：`bff/`，smoke 测试 `/health` 通过。

#### 12. 阶段 4：Vue 3 前端
- **AI 动作**：简历输入（文本粘贴 + PDF 上传）+ 岗位搜索/筛选/分页 + 结果展示（分数/命中/缺口/问题）；Vite 代理 `/api` 到 BFF。
- **产出**：`frontend/`，`npm run build` 通过。

#### 13. 阶段 5：Docker/Compose
- **AI 动作**：五服务编排 + 各服务多阶段构建 + 前端 nginx 反代 + healthcheck；`docker compose config` 校验通过。
- **产出**：`docker-compose.yml` + 各 `Dockerfile`。

#### 14. 用户提问：远程 git 仓库怎么没有
- **用户提问**：远程 git 仓库怎么没有（看不到提交）。
- **AI 动作**：排查发现本地一直 `commit` 未 `push`；`git push -u origin main` 推送全部提交并建立上游跟踪。
- **结论**：本地提交 ≠ 远程可见；此后每阶段提交后一并 push。

#### 15. 端到端联调（含环境排障）
- **AI 动作**：`docker compose up --build` 失败——Docker Desktop 无法连接 Docker Hub（`registry-1.docker.io:443` 超时，国内网络）。
- **替代方案**：发现本机已有运行中的 `mysql8` 容器（`vitamojo/mysql8`，root/123456，映射 3306，镜像来自 DaoCloud 加速）；用 `docker exec` 创建 `careerlens` 库，四服务本地启动。
- **修复**：JDBC `characterEncoding=utf8mb4` 触发 `UnsupportedEncodingException`（connector 只认 Java 字符集），改为 `characterEncoding=UTF-8`。
- **验证**：全链路（前端→BFF→Java→Python→MySQL）实测通过：列表 total=630、详情含 description、分析 score=70/high、命中 [Java,Docker,MySQL]、缺口 [大数据,PostgreSQL,Python]、PDF 提取 3517 字符、中文往返无乱码。

#### 16. 阶段 6/7：测试 + 交付文档
- **AI 动作**：新增 `BackendIntegrationTest`（H2 内存库验证 JD 导入/接口/snake_case 反序列化，5/5 通过）；写 `scripts/smoke_test.py` 端到端冒烟；写 `DELIVERY.md`（架构/启动/契约/算法/测试/验证/取舍/答辩脚本）；更新本记录。
- **产出**：`scripts/smoke_test.py`、`DELIVERY.md`。

#### 17. 前端选岗详情修复
- **用户提问**：前端修复点击选择岗位，下方显示的是岗位详情。
- **AI 动作**：原先选岗后只展示 标题/薪资/公司/地点/经验/学历/行业/技能；改为在下方完整展示岗位详情——新增 `stripHtml`（HTML→纯文本）、`metaParts`（补齐公司规模/阶段）、`jobDescription` 计算属性，模板扩充 岗位描述/福利/公司规模/阶段/原文链接，并补对应 CSS。
- **验证**：`npm run build` 通过；curl 实测 `/api/jobs/{id}` 返回 description=1516 / welfare=147 / url=67 / company_scale / company_stage / company_industry 均有值；vite HMR 自动热更新。
- **产出**：commit `d9ad2bb`（`fix(frontend): 点击选岗后展示完整岗位详情`），已推送。

#### 18. 一键启动/停止脚本
- **用户提问**：全部启动脚本。
- **AI 动作**：后台启动的服务进程此前被回收，新增 `scripts/start_all.sh`（复用 mysql8 容器建库 → 依次后台拉起 Python :8001 / Java :8080 / BFF :3000 / Vue :5173，日志写 `logs/*.log`、PID 写 `logs/*.pid`）与 `scripts/stop_all.sh`（按 PID 连带子进程停止）。
- **验证**：运行脚本后四端 health 均 200，`smoke_test.py` 4/4 通过（total=630 / score=70/high）。
- **产出**：`scripts/start_all.sh`、`scripts/stop_all.sh`。

---

## 待办 / 下一步

- 全部 8 阶段已完成，全链路端到端验证通过。
- 可选后续：真实 LLM 简历优化建议、岗位倒排索引/推荐、分析历史落库。
