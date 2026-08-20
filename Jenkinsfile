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
                    // smoke test 追加 test 配置
                    env.COMPOSE_FULL = "${env.COMPOSE_CMD} -f docker-compose.test.yml"

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
                    docker compose ${COMPOSE_FULL} --profile test down --remove-orphans 2>/dev/null || true

                    # 只停应用端口，不动 mysql8 等基础设施
                    for name in careerlens-ai careerlens-backend careerlens-bff careerlens-frontend careerlens-smoke-test; do
                        docker rm -f $name 2>/dev/null || true
                    done

                    # 确保 mysql8 还在跑（CI 复用模式下）
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
                        sh 'docker compose ${COMPOSE_CMD} up -d --build --wait 2>&1'
                    } else {
                        echo "增量构建: ${services}"

                        // 确保 ai-service 启动（backend 依赖它）
                        sh 'docker compose ${COMPOSE_CMD} up -d ai-service 2>&1'

                        // 只构建变更的服务
                        def toBuild = []
                        if (services.contains('backend'))    toBuild << 'backend'
                        if (services.contains('bff'))        toBuild << 'bff'
                        if (services.contains('ai-service')) toBuild << 'ai-service'
                        if (services.contains('frontend'))   toBuild << 'frontend'

                        sh "docker compose ${env.COMPOSE_CMD} up -d --build ${toBuild.join(' ')} 2>&1"

                        // 等待服务就绪
                        echo "等待服务启动..."
                        sleep 15
                        sh 'docker compose ${COMPOSE_CMD} ps 2>&1'
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
                        sh 'docker compose ${COMPOSE_CMD} up -d --wait 2>&1'
                    }
                }
                sh '''
                    echo "运行冒烟测试..."
                    docker compose ${COMPOSE_FULL} --profile test up smoke-test 2>&1
                    EXIT_CODE=$(docker inspect careerlens-smoke-test --format '{{.State.ExitCode}}' 2>/dev/null || echo "1")
                    echo "冒烟测试退出码: ${EXIT_CODE}"
                    docker compose ${COMPOSE_FULL} --profile test logs smoke-test
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
                docker compose ${COMPOSE_FULL} --profile test down --remove-orphans 2>/dev/null || true
                # 不删 mysql8 等基础设施
                docker image prune -f 2>/dev/null || true
            '''
        }
        success {
            echo "✅ CI Pipeline 通过 | 模式: ${params.PIPELINE_MODE} | 构建: ${env.CHANGED_SERVICES}"
        }
        failure {
            echo "❌ CI Pipeline 失败"
            sh 'docker compose ${COMPOSE_FULL} logs --tail=30 2>/dev/null || true'
        }
    }
}
