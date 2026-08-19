#!/usr/bin/env bash
# CareerLens 一键启动脚本：MySQL(复用) → Python AI → Java 后端 → Node BFF → Vue 前端
# 用法（Git Bash）：
#     bash scripts/start_all.sh
# 日志输出到 logs/ 目录，各服务后台运行，Ctrl+C 或运行 scripts/stop_all.sh 停止。

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
LOGDIR="$ROOT/logs"
mkdir -p "$LOGDIR"

log() { printf '[start_all] %s\n' "$*"; }
fail() { printf '[start_all][错误] %s\n' "$*" >&2; exit 1; }

# 0) MySQL：复用已有 mysql8 容器，确保 careerlens 库存在
if docker ps --filter "name=mysql8" --format '{{.Names}}' | grep -q mysql8; then
  log "MySQL 容器 mysql8 已在运行，确保 careerlens 库存在…"
  docker exec mysql8 mysql -uroot -p123456 \
    -e "CREATE DATABASE IF NOT EXISTS careerlens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
    || fail "创建 careerlens 库失败"
else
  fail "未找到运行中的 mysql8 容器，请先启动 MySQL（如 docker start mysql8）"
fi

# 1) Python AI 服务 :8001
log "启动 AI 服务 (uvicorn :8001)…"
if [ -f "ai-service/venv/Scripts/python.exe" ]; then PY="ai-service/venv/Scripts/python.exe"; else PY="python"; fi
(cd ai-service && "$ROOT/$PY" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 \
  >"$LOGDIR/ai-service.log" 2>&1) &
echo $! > "$LOGDIR/ai-service.pid"

# 2) Java 后端 :8080（启动时自动导入 630 条岗位）
log "启动 Java 后端 (Spring Boot :8080)…"
(cd backend && mvn spring-boot:run >"$LOGDIR/backend.log" 2>&1) &
echo $! > "$LOGDIR/backend.pid"

# 3) Node BFF :3000
log "启动 BFF (Express :3000)…"
(cd bff && npm start >"$LOGDIR/bff.log" 2>&1) &
echo $! > "$LOGDIR/bff.pid"

# 4) Vue 前端 :5173
log "启动前端 (Vite :5173)…"
(cd frontend && npm run dev >"$LOGDIR/frontend.log" 2>&1) &
echo $! > "$LOGDIR/frontend.pid"

log "全部服务已在后台启动，日志目录：$LOGDIR"
log "访问：http://localhost:5173  （BFF :3000 / 后端 :8080 / AI :8001）"
log "查看日志：tail -f logs/<服务>.log ；停止：bash scripts/stop_all.sh"
