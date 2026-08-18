# Commit Dialect — CareerLens (resume-coaching-program)

Project-specific extensions to `.claude/skills/git-commit/SKILL.md`. Load together.

## §1 语言

- **默认中文**：summary 与 body 一律用中文书写。
- **type / scope 令牌保持英文**（属于 Conventional Commits 格式本身），如 `feat(backend): ...`。
- **保留原文的英文技术词**（不翻译）：服务名、scope 名、文件名、路径、函数/字段名、专有名词。
  例如 `MatchService`、`match_score`、`openapi.yaml`、`docker-compose`、`Java-JD-data`、
  `CareerLens`、`脱敏资料`、`vibcoding`、`boss`。
- 祈使语气用中文动词原形：新增 / 修复 / 重构 / 更新 / 移除 / 重命名。

## §2 Scope Catalog

| Scope | Maps to |
|---|---|
| `ai-service` | Python FastAPI service (`ai-service/`, port 8001) |
| `backend` | Java Spring Boot service (`backend/`, port 8080) |
| `bff` | Node.js Express BFF (`bff/`, port 3000) |
| `frontend` | Vue 3 app (`frontend/`, port 5173) |
| `contracts` | `contracts/openapi.yaml`, shared DTO contract |
| `data` | JD import scripts, `Java-JD-data/`, MySQL seed |
| `docker` | Dockerfile / docker-compose / healthchecks |
| `docs` | `README.md`, `DELIVERY.md`, `AI_LOG.md`, `LOCAL_SETUP.md`, `docs/` |
| `chore` | root-level tooling, `.env.example`, `.gitignore`, CI |
| `test` | cross-service test fixtures / baselines |

Sub-scope via `/` (e.g. `backend/match`, `contracts/openapi`, `ai-service/normalizer`).
Multi-scope comma-separated, ≤3.

## §3 AI Co-Author Policy

- When Claude materially shapes a commit (≥30% of diff, proposed the approach, or
  authored the message), end the message with exactly:

  ```
  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
  ```

- This is the **canonical** identity for this project. Do not substitute
  `Co-authored-by: Claude <noreply@anthropic.com>` or any other variant.
- Omit only for purely mechanical commits (renames, `git revert` output) or
  commits where AI contributed no substantive work.

## §4 Green-Build Checks

Per-service, before committing (from `LOCAL_SETUP.md`):

```bash
cd ai-service && pytest          # Python
cd backend && mvn test           # Java
cd bff && npm test               # Node BFF
cd frontend && npm test          # Vue
```

A commit touching a service must leave that service's tests passing.
