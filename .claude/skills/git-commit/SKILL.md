---
name: git-commit
description: >
  Conventional Commits 1.0.0 + best-practice workflow for authoring git commit
  messages in this repo. Produces atomic, green-build, searchable history that
  serves four readers — `git log` scanners, `git blame` tracers, `git bisect`
  hunters, and AI agents rebuilding context after `/clear` or reviewing PRs.

  ALWAYS trigger when the user:
  (1) asks to write / generate / improve a commit message
  (2) pastes a commit-message draft for review
  (3) asks "what type / scope for this change?" or "should I split this commit?"
  (4) is finishing a logical unit of work and about to run `git commit`
  (5) mentions stage / amend / revert / fixup / cherry-pick in a commit context

  Triggers (EN/中文): commit, git commit, stage, commit message, breaking change,
  conventional commits, revert, amend; 提交, git 提交, 暂存, 提交信息, 提交消息,
  重大变更, 回滚, 修订.

  Do NOT trigger for: code generation unrelated to git, branch/merge/rebase
  mechanics not about message authoring, or non-git version control.

  Project-specific scope catalog, domain proper nouns, and AI co-author policy
  live in `docs/references/COMMIT.md` — load and apply it together with this file.
license: MIT
metadata:
  author: adapted from rhino-ty/principled-git-commit (MIT) for this project
---

# Git Commit Conventions

> Derived from [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) +
> Tim Pope's [note on commit messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
> adapted from the MIT-licensed `rhino-ty/principled-git-commit` skill.
> Project-specific extensions (scope catalog, proper nouns, co-author policy) are in
> [`docs/references/COMMIT.md`](../../../docs/references/COMMIT.md) — always load it with this file.

**TL;DR**: `type(scope): summary` (lowercase, imperative, ≤72 chars) + optional why-driven body
+ `- ` bullets + trailers. Atomic, leaves repo green, why-over-what.

---

## 0. Principles

A commit must satisfy four readers — humans **and** AI:

1. **`git log --oneline` scanner** — wants context from a single line.
2. **`git blame <file>` tracer** — wants "why is this line here?" while debugging.
3. **`git bisect` hunter** — wants to isolate the exact commit that broke the build.
4. **AI agent** — rebuilds context after `/clear`, reviews PRs, generates changelogs.
   Atomic units, concrete keywords, English default, and explicit trailers are decisive.

### 0.1 Atomic — one commit, one intent

Bundle exactly one logical change. Never mix "fix + style + docs" in one commit.
Test: "If I revert this commit, do I drag along unrelated changes?" If yes, split.

### 0.2 Leaves repo green — every commit builds

Each commit, taken alone, must pass the project's checks (see the per-service test
commands in `LOCAL_SETUP.md`). No "WIP, next commit will fix this."

### 0.3 Why over what — body explains motivation

The diff already shows **what**. The body's job is **why** — motivation, trade-off,
constraint that forced the approach.

```
❌ Body: "给 DTO 加 match_score 字段"              (diff 已说明)
✅ Body: "暴露 match_score，让前端直接渲染环形     (说明 WHY)
        仪表盘，避免客户端重复计算"
```

### 0.4 Imperative mood — "If applied, this commit will..."

Summary in imperative, matching git's own messages (`Merge`, `Revert`).

```
✅ 为 analyze 接口新增幂等性
✅ 修复 matcher 中空技能导致的崩溃
❌ 新增了 / 正在新增（过去式 / 进行式）
```

### 0.5 Searchable — keyword-rich summary and body

Name domain nouns, function/field names, file paths, service names explicitly.
Vague verbs (`improve`, `update`, `cleanup`) must pair with a concrete noun.

```
❌ feat(backend): 改进匹配
✅ feat(backend): 在 MatchService 中新增技能加权重叠打分
```

---

## 1. Format

```
type(scope): summary

[optional 1-2 line context — why]

- bullet: concept- or file-level change
- bullet: ...

[optional trailers]
```

| Property | Rule |
|---|---|
| Summary length | ≤72 chars (soft), never >100 |
| Form | `type(scope): summary` — scope optional but almost always present |
| Case | lowercase, imperative; proper nouns keep their case |
| Language | 中文（type/scope 与英文技术词保留原文，见 dialect §1） |
| Trailing punctuation | none |
| Body | `- ` bullets, `path: change` pairs, `Section:` plain labels; **no `##` headers** |

---

## 2. Types

| Type | Use |
|---|---|
| `feat` | New feature / endpoint / domain / column |
| `fix` | Bug fix / regression repair |
| `refactor` | Behavior unchanged, structure changed |
| `docs` | Documentation only |
| `style` | Visual/formatting only, no logic |
| `test` | Test additions / baselines |
| `perf` | Performance-only change |
| `build` | Build / bundler / compiler / Docker config |
| `ci` | CI / pipeline config |
| `chore` | Tooling / scaffold / dependency bumps |
| `revert` | Output of `git revert` |

When ambiguous, pick the **largest impact** (e.g. `refactor` + incidental `fix` → `refactor`).

---

## 3. Scopes

Project scope catalog lives in `docs/references/COMMIT.md` §2. Canonical scopes:

```
feat(ai-service): 新增技能归一化接口
fix(backend):    处理 match DTO 中 skills 为 null 的情况
refactor(bff):   抽取错误映射中间件
feat(frontend):  渲染匹配度环形仪表盘
docs(contracts): 补充 /api/analyze 响应 DTO 文档
chore(docker):   为 compose 中的 mysql 增加健康检查
```

Slash for sub-scope (`contracts/openapi`, `backend/match`), comma for ≤3 multi-scope.

---

## 4. Workflow (5-step)

1. **Inspect diff** — `git diff` / `git diff --staged` / `git status --porcelain`. Never guess.
2. **Stage explicitly** — `git add <path>` / glob / `-p` hunks. ❌ `git add -A` (risks secrets + unrelated files).
3. **Decide type** (§2) + scope (§3).
4. **Secrets grep** — staged files must not hit:
   ```bash
   git diff --staged --name-only | grep -iE '\.(env|pem|key|p12|pfx|jar)$|credentials\.|id_rsa'
   ```
   (`.env` is gitignored — never commit it.)
5. **Pre-commit checklist**:
   ```
   [ ] Atomic — one intent                          [ ] No console.log / debugger
   [ ] Leaves repo green (tests pass)                [ ] Explicit path stage (not -A)
   [ ] Why-over-what body                            [ ] Summary ≤72 chars, imperative
   [ ] Searchable keywords                           [ ] BREAKING CHANGE if compat broken
   [ ] No secrets (grep returns 0)                   [ ] AI co-author trailer added
   ```

---

## 5. Breaking Changes

Signal API / DTO / DB-schema / env-var changes that break callers — `!` notation
and/or `BREAKING CHANGE:` footer:

```
feat(contracts)!: 将 matchResult.matchScore 重命名为 match_score
```

Flag when: DTO request/response shape changes, DB column drop / NOT NULL added,
env var rename, public API URL change. Do **not** flag internal-only changes or
backward-compatible additions.

---

## 6. Trailers

Blank line before the trailer block; tokens run consecutively, no blank lines inside.

| Token | Use |
|---|---|
| `Co-Authored-By:` | AI co-authoring — see dialect §3 for the exact identity |
| `Refs:` | issue reference without auto-close |
| `Closes:` / `Fixes:` | GitHub auto-close |
| `BREAKING CHANGE:` | §5 |

**AI co-author policy**: this project's commits that AI materially shaped end with
the trailer in `docs/references/COMMIT.md` §3 (currently `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).
AI wrote ≥30% of diff, proposed the approach, or authored the message → add it.

---

## 7. Amend / Revert

- `--amend`: only the most recent commit, **before push**. After push → new commit.
- `revert`: `git revert <hash>`, keep auto summary, add a **reason** paragraph + `Refs:` hash.

---

## 8. Anti-patterns

| Anti-pattern | Replacement |
|---|---|
| `## ` headers in body | plain `Section:` label |
| `更新文件` / `wip` / `修 bug` / `优化表单`（空泛） | 具体名词 + scope 路径 |
| Mixing concerns | atomic commits |
| `git add -A` | explicit path stage |
| WHAT-only body | center the WHY |
| past/gerund tense | imperative |
| missing `Co-Authored-By:` | add per dialect §3 |

---

## 9. Quick Reference

```
type(scope): summary            ← lowercase, imperative, ≤72 chars
<blank>
why-driven context (optional)
<blank>
- concept-level bullet          ← no ## headers, no file dump
<blank>
Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

1. Inspect diff → 2. stage explicit path → 3. type+scope → 4. secrets grep → 5. checklist.

---

## Source Attribution

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- Tim Pope, [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
- [`rhino-ty/principled-git-commit`](https://github.com/rhino-ty/principled-git-commit) (MIT) — primary source, adapted for this project.
