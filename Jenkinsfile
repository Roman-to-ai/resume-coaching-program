pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'careerlens-ci'
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('准备环境') {
            steps {
                echo "=== CI Pipeline 开始 ==="
                echo "Build #${env.BUILD_NUMBER}"
                echo "Git Commit: ${env.GIT_COMMIT?.take(8) ?: 'N/A'}"

                // 释放端口：停掉宿主机可能占用 3306/8080/3000/8001/5173 的容器
                sh '''
                    echo "清理可能冲突的旧容器..."
                    docker ps -q --filter "publish=3306" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=8080" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=3000" | xargs -r docker stop 2>/dev/null || true
                    docker ps -q --filter "publish=8001" | xargs -r docker stop 2>/dev/null || true
                    sleep 2
                '''
            }
        }

        stage('构建验证') {
            parallel {
                stage('Backend (Maven)') {
                    steps {
                        dir('backend') {
                            sh 'mvn clean package -DskipTests -B -q'
                            echo 'Backend 构建成功'
                        }
                    }
                }
                stage('Frontend (npm)') {
                    steps {
                        dir('frontend') {
                            sh 'npm ci --prefer-offline --no-audit --silent'
                            sh 'npm run build'
                            echo 'Frontend 构建成功'
                        }
                    }
                }
                stage('BFF (npm)') {
                    steps {
                        dir('bff') {
                            sh 'npm ci --prefer-offline --no-audit --silent'
                            echo 'BFF 构建成功'
                        }
                    }
                }
                stage('AI Service (pip)') {
                    steps {
                        dir('ai-service') {
                            sh '''
                                python -m venv .venv
                                . .venv/bin/activate
                                pip install -r requirements.txt -q
                            '''
                            echo 'AI Service 依赖安装成功'
                        }
                    }
                }
            }
        }

        stage('Docker Compose 部署') {
            steps {
                sh '''
                    echo "构建并启动所有服务..."
                    docker compose -f docker-compose.yml up -d --build --wait
                    echo "等待服务就绪..."
                    sleep 15
                '''
            }
        }

        stage('冒烟测试') {
            steps {
                sh '''
                    echo "运行端到端冒烟测试..."
                    python scripts/smoke_test.py http://localhost:3000
                '''
            }
        }
    }

    post {
        always {
            echo "清理 Docker Compose 环境..."
            sh '''
                docker compose -f docker-compose.yml down --volumes --remove-orphans 2>/dev/null || true
                # 清理 CI 构建镜像
                docker image prune -f 2>/dev/null || true
            '''
        }
        success {
            echo "✅ CI Pipeline 全部通过!"
        }
        failure {
            echo "❌ CI Pipeline 失败，查看上方日志定位问题"
            // 输出各服务日志便于排查
            sh '''
                echo "=== 服务日志 ==="
                docker compose -f docker-compose.yml logs --tail=20 2>/dev/null || true
            '''
        }
    }
}
