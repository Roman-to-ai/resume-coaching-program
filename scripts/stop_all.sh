#!/usr/bin/env bash
# CareerLens 一键停止脚本：按 start_all.sh 记录的 PID 停止各服务。
# 用法（Git Bash）：bash scripts/stop_all.sh
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGDIR="$ROOT/logs"

for svc in ai-service backend bff frontend; do
  pidfile="$LOGDIR/$svc.pid"
  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile" 2>/dev/null)"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      # 连带结束其子进程（如 mvn 的 java 子进程、vite 的 esbuild）
      pkill -P "$pid" 2>/dev/null
      kill "$pid" 2>/dev/null
      printf '[stop_all] 已停止 %s (pid=%s)\n' "$svc" "$pid"
    else
      printf '[stop_all] %s 未在运行\n' "$svc"
    fi
    rm -f "$pidfile"
  fi
done

printf '[stop_all] 完成。MySQL 容器 mysql8 未改动（如无需保留可手动 docker stop mysql8）\n'
