# CareerLens AI - 本地开发指南

## 环境要求

- **Docker**: 已安装
- **MySQL 8.0**: 本地已安装（root/123456）
- **Node.js**: v20+
- **Python**: 3.9+
- **Java**: JDK 17+

## 快速启动

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置你的 OPENAI_API_KEY
```

### 2. 初始化数据库

```bash
# 确保 MySQL 服务已启动
mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS careerlens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 3. 启动各服务

#### Python AI 服务 (端口 8001)
```bash
cd ai-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### Java 后端服务 (端口 8080)
```bash
cd backend
mvn clean install
mvn spring-boot:run
```

#### Node.js BFF 层 (端口 3000)
```bash
cd bff
npm install
npm run dev
```

#### Vue 3 前端 (端口 5173)
```bash
cd frontend
npm install
npm run dev
```

## 服务架构

```
Frontend (Vue 3)         :5173
    ↓
BFF (Node.js/Express)    :3000
    ↓
Backend (Spring Boot)    :8080
    ↓
AI Service (FastAPI)     :8001
    ↓
MySQL Database           :3306
```

## API 端点

- **前端界面**: http://localhost:5173
- **BFF API**: http://localhost:3000/api
- **后端 API**: http://localhost:8080/api
- **AI 服务 API**: http://localhost:8001/api

## 开发工作流

1. 遵循 Git Flow 分支策略
2. 功能开发在 `feature/*` 分支
3. 提交前运行测试和 lint
4. 使用规范的 commit message

## 测试

```bash
# Python 测试
cd ai-service && pytest

# Java 测试
cd backend && mvn test

# Node.js 测试
cd bff && npm test

# Vue 测试
cd frontend && npm test
```

## 故障排查

- **端口占用**: 确保各端口未被占用
- **数据库连接**: 检查 MySQL 服务状态
- **依赖问题**: 清理并重新安装依赖
