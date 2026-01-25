pipeline {
    agent any

    options {
        skipDefaultCheckout false
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        APP_NAME   = "task-manager-fastapi"
        RELEASE    = "1.0"
        IMAGE_TAG  = "${RELEASE}.${BUILD_NUMBER}"
    }

    stages {
        stage("Cleanup Workspace") {
            steps {
                cleanWs()
            }
        }

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Install Dependencies") {
            steps {
                sh '''
                    set -euxo pipefail
                    poetry --version
                    poetry install --no-interaction --no-ansi
                '''
            }
        }

        stage("Run Tests") {
            steps {
                sh '''
                    set -euxo pipefail
                    poetry run pytest -v
                '''
            }
        }

        stage("Build Docker Image") {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PASS'
                    )]) {
                        env.IMAGE_NAME = "${DOCKERHUB_USER}/${env.APP_NAME}"
                    }
                }
                sh '''
                    set -euxo pipefail
                    echo "Building image: ${IMAGE_NAME}:${IMAGE_TAG}"
                    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
                    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:latest"
                '''
            }
        }

        stage("SonarQube Scan") {
            steps {
                // Requires SonarQube server configured in Jenkins as "SonarQube"
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        set -euxo pipefail
                        sonar-scanner \
                          -Dsonar.projectKey=${APP_NAME} \
                          -Dsonar.sources=. \
                    '''
                }
            }
        }

        stage("Wait for Quality Gate") {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage("Push Docker Image") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                        set -euxo pipefail
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        echo "Pushing image: ${IMAGE_NAME}:${IMAGE_TAG}"
                        docker push "${IMAGE_NAME}:${IMAGE_TAG}"
                        docker push "${IMAGE_NAME}:latest"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
            script {
                currentBuild.description = "Success: Build ${BUILD_NUMBER}"
            }
        }
        failure {
            echo "Pipeline failed!"
            script {
                currentBuild.description = "Failed: Build ${BUILD_NUMBER}"
            }
        }
        always {
            cleanWs()
        }
    }
}