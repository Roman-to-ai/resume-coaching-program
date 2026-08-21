pipeline {
    agent any

    parameters {
        choice(
            name: 'PIPELINE_MODE',
            choices: ['smart', 'test-only', 'build-all', 'deploy'],
            description: '''
                smart     — 自动检测变更目录，按需构建（push 触发时默认）
                test-only — 仅运行冒烟测试，不重新构建
                build-all — 全量构建所有服务
                deploy    — 全量构建 + 部署 + 冒烟测试
            '''
        )
    }

    environment {
        COMPOSE_PROJECT_NAME = 'careerlens-ci'
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        // ========== 阶段 1：检测环境 & 变更 ==========
        stage('检测') {
            steps {
                script {
                    // ----- 检测已有基础设施 -----
                    def mysqlRunning = sh(
                        script: 'docker ps --format "{{.Names}}" | grep -qx mysql8 && echo yes || echo no',
                        returnStdout: true
                    ).trim()

                    if (mysqlRunning == 'yes') {
                        env.USE_CI_COMPOSE = 'true'
                        env.COMPOSE_CMD = '-f docker-compose.ci.yml'
                        echo "✓ 检测到已有 mysql8，复用（不重建）"
                    } else {
                        env.USE_CI_COMPOSE = 'false'
                        env.COMPOSE_CMD = '-f docker-compose.yml'
                        echo "✗ 未检测到 mysql8，将使用完整 compose 启动 MySQL"
                    }
                    // smoke test 用 docker run 直接执行（避免卷挂载路径问题）

                    // ----- 检测变更 -----
                    env.CHANGED_SERVICES = 'all'
                    env.HAS_CHANGES = 'true'

                    if (params.PIPELINE_MODE == 'build-all' || params.PIPELINE_MODE == 'deploy') {
                        env.CHANGED_SERVICES = 'all'
                        echo "模式: ${params.PIPELINE_MODE} → 全量构建"
                    } else if (params.PIPELINE_MODE == 'test-only') {
                        env.HAS_CHANGES = 'false'
                        env.CHANGED_SERVICES = 'none'
                        echo "模式: test-only → 仅运行冒烟测试"
                    } else {
                        // smart 模式：git diff 检测变更
                        def changedFiles = sh(
                            script: '''
                                if git rev-parse HEAD~1 >/dev/null 2>&1; then
                                    git diff --name-only HEAD~1 HEAD
                                else
                                    echo "INITIAL_COMMIT"
                                fi
                            ''',
                            returnStdout: true
                        ).trim()

                        echo "变更文件:\n${changedFiles}"

                        def services = [] as Set

                        if (changedFiles == 'INITIAL_COMMIT' || changedFiles.contains('docker-compose') ||
                            changedFiles.contains('Jenkinsfile') || changedFiles.contains('db/') ||
                            changedFiles.contains('contracts/')) {
                            services = ['frontend', 'bff', 'backend', 'ai-service']
                        } else {
                            changedFiles.split('\n').each { file ->
                                if (file.startsWith('frontend/'))   services << 'frontend'
                                if (file.startsWith('bff/'))        services << 'bff'
                                if (file.startsWith('backend/'))    services << 'backend'
                                if (file.startsWith('ai-service/')) services << 'ai-service'
                            }
                        }

                        // 依赖链传播
                        if (services.contains('backend') || services.contains('ai-service')) {
                            services << 'bff'
                            services << 'frontend'
                        }
                        if (services.contains('bff')) {
                            services << 'frontend'
                        }

                        if (services.isEmpty()) {
                            env.HAS_CHANGES = 'false'
                            env.CHANGED_SERVICES = 'none'
                        } else {
                            env.CHANGED_SERVICES = services.join(',')
                        }
                    }

                    echo "=== Pipeline 配置 ==="
                    echo "模式:      ${params.PIPELINE_MODE}"
                    echo "Compose:   ${env.COMPOSE_CMD}"
                    echo "构建服务:   ${env.CHANGED_SERVICES}"
                }
            }
        }

        // ========== 阶段 2：准备环境 ==========
        stage('准备环境') {
            when { expression { env.HAS_CHANGES == 'true' || params.PIPELINE_MODE in ['test-only', 'deploy'] } }
            steps {
                sh '''
                    echo "清理旧 CI 容器..."
                    # 用 -p 指定项目名，只删 CI 容器，不碰生产容器
                    docker compose -p careerlens-ci ${COMPOSE_CMD} down --remove-orphans 2>/dev/null || true

                    # 确保 mysql8 还在跑
                    if [ "${USE_CI_COMPOSE}" = "true" ]; then
                        docker start mysql8 2>/dev/null || true
                        echo "✓ mysql8 已就绪"
                    fi
                '''
            }
        }

        // ========== 阶段 3：构建 ==========
        stage('构建服务') {
            when { expression { env.HAS_CHANGES == 'true' } }
            steps {
                script {
                    def services = env.CHANGED_SERVICES

                    if (services == 'all') {
                        echo "全量构建..."
                        sh 'docker compose -p careerlens-ci ${COMPOSE_CMD} up -d --build --wait 2>&1'
                    } else {
                        echo "增量构建: ${services}"

                        // 确保 ai-service 启动（backend 依赖它）
                        sh 'docker compose -p careerlens-ci ${COMPOSE_CMD} up -d ai-service 2>&1'

                        // 只构建变更的服务
                        def toBuild = []
                        if (services.contains('backend'))    toBuild << 'backend'
                        if (services.contains('bff'))        toBuild << 'bff'
                        if (services.contains('ai-service')) toBuild << 'ai-service'
                        if (services.contains('frontend'))   toBuild << 'frontend'

                        sh "docker compose -p careerlens-ci ${env.COMPOSE_CMD} up -d --build ${toBuild.join(' ')} 2>&1"

                        // 等待服务就绪
                        echo "等待服务启动..."
                        sleep 15
                        sh 'docker compose -p careerlens-ci ${COMPOSE_CMD} ps 2>&1'
                    }
                }
            }
        }

        // ========== 阶段 4：冒烟测试 ==========
        stage('冒烟测试') {
            when {
                anyOf {
                    expression { params.PIPELINE_MODE == 'test-only' }
                    expression { params.PIPELINE_MODE == 'deploy' }
                    expression { env.HAS_CHANGES == 'true' }
                }
            }
            steps {
                script {
                    if (params.PIPELINE_MODE == 'test-only') {
                        echo "test-only：拉起服务..."
                        sh 'docker compose -p careerlens-ci ${COMPOSE_CMD} up -d --wait 2>&1'
                    }
                }
                sh '''
                    echo "运行冒烟测试..."

                    # 创建临时冒烟测试脚本到工作区
                    cat > smoke_test_ci.py << 'SMOKE_EOF'
import json, sys, urllib.request

BASE = "http://bff:3000"

def req(method, path, payload=None):
    url = BASE + path
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=30)
    return r.status, json.loads(r.read().decode("utf-8"))

ok = True
print("== CareerLens 冒烟测试 ==")

try:
    s, _ = req("GET", "/health")
    print("  [PASS] BFF 健康检查" if s == 200 else "  [FAIL] BFF 健康检查")
    ok = ok and s == 200
except Exception as e:
    print("  [FAIL] BFF 健康检查 " + str(e))
    sys.exit(1)

try:
    s, jobs = req("GET", "/api/jobs?size=3")
    passed = s == 200 and jobs.get("total", 0) > 0
    print("  [PASS] 岗位列表 total=" + str(jobs.get("total", 0)) if passed else "  [FAIL] 岗位列表")
    ok = ok and passed
    job_id = jobs["items"][0]["job_id"]
except Exception as e:
    print("  [FAIL] 岗位列表 " + str(e))
    sys.exit(1)

try:
    s, detail = req("GET", "/api/jobs/" + str(job_id))
    passed = s == 200 and bool(detail.get("description"))
    print("  [PASS] 岗位详情" if passed else "  [FAIL] 岗位详情")
    ok = ok and passed
except Exception as e:
    print("  [FAIL] 岗位详情 " + str(e))

resume = "3年Java开发经验，熟悉Spring Boot、MySQL、Redis、Docker"
try:
    s, res = req("POST", "/api/analyze", {"resume_text": resume, "job_id": job_id})
    passed = s == 200 and "match_score" in res
    score = res.get("match_score", "?")
    print("  [PASS] 匹配分析 score=" + str(score) if passed else "  [FAIL] 匹配分析")
    ok = ok and passed
except Exception as e:
    print("  [FAIL] 匹配分析 " + str(e))

print("== 结果：" + ("全部通过" if ok else "存在失败") + " ==")
sys.exit(0 if ok else 1)
SMOKE_EOF

                    # 通过 CI compose 网络访问 BFF 服务
                    cat smoke_test_ci.py | docker run --rm --network careerlens-ci_default -i python:3.11-slim python -
                    rm -f smoke_test_ci.py
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker compose -p careerlens-ci ${COMPOSE_CMD} down --remove-orphans 2>/dev/null || true
                docker image prune -f 2>/dev/null || true
            '''
        }
        success {
            echo "✅ CI Pipeline 通过 | 模式: ${params.PIPELINE_MODE} | 构建: ${env.CHANGED_SERVICES}"
        }
        failure {
            echo "❌ CI Pipeline 失败"
            sh 'docker compose -p careerlens-ci ${COMPOSE_CMD} logs --tail=30 2>/dev/null || true'
        }
    }
}
