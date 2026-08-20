pipeline {
    agent any

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
        stage('准备环境') {
            steps {
                echo "=== CareerLens CI Pipeline ==="
                echo "Build #${env.BUILD_NUMBER}"
                echo "Git Commit: ${env.GIT_COMMIT?.take(8) ?: 'N/A'}"

                sh '''
                    echo "清理可能冲突的旧容器..."
                    docker compose ${COMPOSE_FILES} --profile test down --volumes --remove-orphans 2>/dev/null || true
                    docker ps -q --filter "publish=3306" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=8080" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=3000" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=8001" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=5173" | xargs -r docker stop 2>/dev/null || true
                    sleep 2
                    echo "环境清理完成"
                '''
            }
        }

        stage('Docker 构建 & 部署') {
            steps {
                sh '''
                    echo "构建并启动所有服务..."
                    docker compose ${COMPOSE_FILES} up -d --build 2>&1
                    echo "等待服务就绪 (MySQL healthcheck + 依赖启动)..."
                    sleep 20
                    echo "当前运行的容器:"
                    docker compose ${COMPOSE_FILES} ps
                '''
            }
        }

        stage('冒烟测试') {
            steps {
                sh '''
                    echo "运行端到端冒烟测试..."
                    docker compose ${COMPOSE_FILES} --profile test up smoke-test 2>&1
                    RESULT=$(docker compose ${COMPOSE_FILES} --profile test ps smoke-test --format json 2>/dev/null || echo '{}')

                    # 检查退出码
                    EXIT_CODE=$(docker inspect careerlens-smoke-test --format '{{.State.ExitCode}}' 2>/dev/null || echo "1")
                    echo "冒烟测试退出码: ${EXIT_CODE}"

                    # 显示测试输出
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
                echo "清理 CI Docker 环境..."
                docker compose ${COMPOSE_FILES} --profile test down --volumes --remove-orphans 2>/dev/null || true
                docker image prune -f 2>/dev/null || true
            '''
        }
        success {
            echo "✅ CI Pipeline 全部通过!"
        }
        failure {
            echo "❌ CI Pipeline 失败"
            sh '''
                echo "=== 各服务最后 30 行日志 ==="
                docker compose ${COMPOSE_FILES} logs --tail=30 2>/dev/null || true
            '''
        }
    }
}
