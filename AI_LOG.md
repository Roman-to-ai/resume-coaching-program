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

---

## 待办 / 下一步

- 阶段 1：Python AI 服务（清洗/归一化/匹配/打分，LLM 兜底）
- 后续按 `PLAN.md` 执行，commit 遵循 `git-commit` 规范
