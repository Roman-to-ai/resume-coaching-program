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
        COMPOSE_FILES = '-f docker-compose.yml -f docker-compose.test.yml'
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        // ========== 阶段 1：检测变更 ==========
        stage('检测变更') {
            steps {
                script {
                    // 默认：全量构建（手动触发或首次构建时无历史）
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
                        // smart 模式：用 git diff 检测变更
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
                            // 基础设施变更 → 全量构建
                            services = ['frontend', 'bff', 'backend', 'ai-service']
                        } else {
                            // 按目录匹配服务
                            changedFiles.split('\n').each { file ->
                                if (file.startsWith('frontend/'))   services << 'frontend'
                                if (file.startsWith('bff/'))        services << 'bff'
                                if (file.startsWith('backend/'))    services << 'backend'
                                if (file.startsWith('ai-service/')) services << 'ai-service'
                                // scripts/ 变更 → 需要冒烟测试，但不重建服务
                            }
                        }

                        // 依赖链：backend 变了 → bff + frontend 也要重新构建
                        // （因为 BFF 依赖 Backend API，前端通过 BFF 间接依赖）
                        if (services.contains('backend') || services.contains('ai-service')) {
                            services << 'bff'
                            services << 'frontend'
                        }
                        // bff 变了 → frontend 也要重新构建
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
                    echo "模式: ${params.PIPELINE_MODE}"
                    echo "需要构建的服务: ${env.CHANGED_SERVICES}"
                    echo "有变更: ${env.HAS_CHANGES}"
                }
            }
        }

        // ========== 阶段 2：准备环境 ==========
        stage('准备环境') {
            when { expression { env.HAS_CHANGES == 'true' || params.PIPELINE_MODE == 'test-only' || params.PIPELINE_MODE == 'deploy' } }
            steps {
                echo "清理旧容器..."
                sh '''
                    docker compose ${COMPOSE_FILES} --profile test down --volumes --remove-orphans 2>/dev/null || true
                    for port in 3306 8080 3000 8001 5173; do
                        docker ps -q --filter "publish=$port" | xargs -r docker stop 2>/dev/null || true
                    done
                    sleep 2
                '''
            }
        }

        // ========== 阶段 3：构建（按服务分） ==========
        stage('构建服务') {
            when { expression { env.HAS_CHANGES == 'true' } }
            steps {
                script {
                    def services = env.CHANGED_SERVICES

                    if (services == 'all') {
                        echo "全量构建所有服务..."
                        sh 'docker compose ${COMPOSE_FILES} up -d --build --wait 2>&1'
                    } else {
                        echo "增量构建: ${services}"

                        // 先启动不需构建的基础服务（mysql, ai-service 如果没改的话）
                        if (!services.contains('ai-service')) {
                            sh 'docker compose up -d mysql ai-service 2>&1'
                        }

                        // 逐个构建变更的服务
                        if (services.contains('backend')) {
                            echo "→ 构建 Backend..."
                            sh 'docker compose up -d --build mysql backend 2>&1'
                        }
                        if (services.contains('bff')) {
                            echo "→ 构建 BFF..."
                            sh 'docker compose up -d --build bff 2>&1'
                        }
                        if (services.contains('ai-service')) {
                            echo "→ 构建 AI Service..."
                            sh 'docker compose up -d --build ai-service 2>&1'
                        }
                        if (services.contains('frontend')) {
                            echo "→ 构建 Frontend..."
                            sh 'docker compose up -d --build frontend 2>&1'
                        }

                        // 等待所有服务健康
                        echo "等待服务就绪..."
                        sh 'docker compose ps 2>&1'
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
                // test-only 模式：先拉起已有服务
                script {
                    if (params.PIPELINE_MODE == 'test-only') {
                        echo "test-only 模式：拉起服务..."
                        sh 'docker compose up -d --wait 2>&1'
                    }
                }

                sh '''
                    echo "运行冒烟测试..."
                    docker compose ${COMPOSE_FILES} --profile test up smoke-test 2>&1
                    EXIT_CODE=$(docker inspect careerlens-smoke-test --format '{{.State.ExitCode}}' 2>/dev/null || echo "1")
                    echo "冒烟测试退出码: ${EXIT_CODE}"
                    docker compose ${COMPOSE_FILES} --profile test logs smoke-test
                    if [ "${EXIT_CODE}" != "0" ]; then
                        echo "冒烟测试失败!"
                        exit 1
                    fi
                    echo "冒烟测试通过!"
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker compose ${COMPOSE_FILES} --profile test down --volumes --remove-orphans 2>/dev/null || true
                docker image prune -f 2>/dev/null || true
            '''
        }
        success {
            echo """
╔═══════════════════════════════════════╗
║  ✅ CI Pipeline 全部通过              ║
║  模式: ${params.PIPELINE_MODE}                    ║
║  构建: ${env.CHANGED_SERVICES}       ║
╚═══════════════════════════════════════╝
"""
        }
        failure {
            echo "❌ CI Pipeline 失败"
            sh 'docker compose ${COMPOSE_FILES} logs --tail=30 2>/dev/null || true'
        }
    }
}
