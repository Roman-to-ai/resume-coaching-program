# vibcoding — AI 求职平台全栈笔试

## 业务背景

CareerLens 是面向高校学生的 AI 求职辅导平台，围绕简历优化、岗位匹配、模拟面试和 Agent 服务，帮助学生把经历转化为可执行的求职行动。

本题聚焦一个最小纵向闭环：学生提交简历文本并选择岗位（boos上copy一些JD摘要），系统完成简历数据清洗、技能归一化和岗位匹配分析，返回简历结构化问题，可解释的命中项、能力缺口与岗位匹配度（轻度算法）。完整请求链为：

`Vue 3 → Node.js BFF → Java/Spring Boot → Python → LLM`
## 题目资料

- 详见目录内：\脱敏资料

## 技术栈选择

- **Vue 
- **Node.js BFF**：隔离浏览器与内部服务，集中处理输入校验、请求编排、超时和错误映射。
- **Java + Spring Boot**：承载稳定的岗位领域 API、服务编排和 DTO 契约。
- **Python + LLM ：适合文本清洗、技能归一化和匹配分析；通过 OpenAI-compatible LLM API 接入模型，也可经兼容网关接入 Claude 等模型。
- **Docker/Compose**：提供可重复的本地运行、健康检查、测试。

详细题面、接口契约和公开 fixture 见 [`TASK.md`](TASK.md)、[`contracts/openapi.yaml`](contracts/openapi.yaml) 与 [`contracts/fixtures/`](contracts/fixtures/)。

## 交付基础

- 最大理解能力下完善业务需求
- 前端建议使用有风格的组件或经vibcoding改造，请勿纯ai出来的UI
- 测试分支管理，git工作流


## 提交要求

1. 结束时提交 Git 仓库链接或压缩包，并保留计时期间的提交历史；
2. 提交可运行代码、测试、Docker/Compose ，并在 `DELIVERY.md` 写明实际验证过的启动、测试、部署/回滚、架构取舍和已知缺口。
3. 与 AI 的会话历史，记录到 `AI_LOG.md`
4. 准备 15 分钟答辩，演示请求链。

