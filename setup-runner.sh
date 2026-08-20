#!/bin/bash
# ==============================================
# GitHub Actions Self-Hosted Runner 安装脚本
# 仓库: Roman-to-ai/resume-coaching-program
# ==============================================

set -e

REPO_URL="https://github.com/Roman-to-ai/resume-coaching-program"
RUNNER_DIR="$HOME/actions-runner"

echo "=========================================="
echo " GitHub Actions Self-Hosted Runner 安装"
echo "=========================================="

# 1. 检查 WSL 环境
echo ""
echo "[1/5] 检查环境..."
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "✅ WSL 环境确认"
else
    echo "⚠️  未检测到 WSL，继续安装..."
fi

# 2. 安装依赖
echo ""
echo "[2/5] 安装依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq curl jq libicu72 > /dev/null 2>&1 || \
sudo apt-get install -y -qq curl jq libicu-dev > /dev/null 2>&1 || true

# 3. 下载 Runner
echo ""
echo "[3/5] 下载 GitHub Actions Runner..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

RUNNER_VERSION="2.321.0"
RUNNER_ARCH="linux-x64"
RUNNER_TAR="actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"

if [ ! -f "./config.sh" ]; then
    curl -sL "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_TAR}" -o "$RUNNER_TAR"
    tar xzf "$RUNNER_TAR"
    rm -f "$RUNNER_TAR"
    echo "✅ Runner 下载完成"
else
    echo "✅ Runner 已存在，跳过下载"
fi

# 4. 配置 Runner
echo ""
echo "[4/5] 配置 Runner..."
echo ""
echo "请按以下步骤操作："
echo "  1. 打开浏览器访问: ${REPO_URL}/settings/actions/runners"
echo "  2. 点击 'New self-hosted runner'"
echo "  3. 复制页面上显示的 --token 值"
echo ""
read -p "请输入从 GitHub 获取的 Token: " RUNNER_TOKEN

if [ -z "$RUNNER_TOKEN" ]; then
    echo "❌ Token 不能为空"
    exit 1
fi

./config.sh \
    --url "$REPO_URL" \
    --token "$RUNNER_TOKEN" \
    --labels "self-hosted,linux,local,jenkins" \
    --name "local-wsl-runner" \
    --unattended

echo "✅ Runner 配置完成"

# 5. 安装为系统服务（可选）
echo ""
echo "[5/5] 安装为系统服务..."
sudo ./svc.sh install 2>/dev/null || true
sudo ./svc.sh start 2>/dev/null || true
echo "✅ Runner 服务已启动"

echo ""
echo "=========================================="
echo " 安装完成!"
echo "=========================================="
echo ""
echo "Runner 目录: $RUNNER_DIR"
echo ""
echo "常用命令:"
echo "  启动: cd $RUNNER_DIR && ./run.sh"
echo "  服务: sudo ./svc.sh start|stop|status"
echo ""
echo "接下来请在 GitHub 仓库中设置 Secrets:"
echo "  Settings → Secrets → Actions → New repository secret"
echo "    JENKINS_USER  = admin"
echo "    JENKINS_TOKEN = 11b4c80329c869f295b81a6a2fc41bcc25"
echo ""
