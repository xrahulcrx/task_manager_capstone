pipeline {
    agent any

    options {
        skipDefaultCheckout true
    }

    environment {
        APP_NAME          = "task-manager-fastapi"
        RELEASE           = "1.0"
        IMAGE_TAG         = "${RELEASE}.${BUILD_NUMBER}"

        // Jenkins container → SonarQube container
        SONAR_HOST_URL    = "http://sonarqube:9000"

        // Browser link
        SONAR_BROWSER_URL = "http://localhost:9000"
    }

    stages {
        stage("Cleanup Workspace") {
            steps { cleanWs() }
        }

        stage("Checkout") {
            steps { checkout scm }
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

        stage("DockerHub Login") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                        set -euxo pipefail
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                    '''
                }
            }
        }

        stage("Build Docker Image") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                        set -euxo pipefail
                        IMAGE_NAME="$DOCKERHUB_USER/$APP_NAME"
                        echo "Building image: $IMAGE_NAME:$IMAGE_TAG"
                        docker build -t $IMAGE_NAME:$IMAGE_TAG .
                        docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage("SonarQube Scan") {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        set -euxo pipefail
                        sonar-scanner \
                          -Dsonar.projectKey=$APP_NAME \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=$SONAR_HOST_URL \
                          -Dsonar.token=$SONAR_TOKEN
                    '''
                }
            }
        }

        stage("Show SonarQube Dashboard Link") {
            steps {
                echo "SonarQube Dashboard: ${SONAR_BROWSER_URL}/dashboard?id=${APP_NAME}"
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
                        IMAGE_NAME="$DOCKERHUB_USER/$APP_NAME"
                        echo "Pushing image: $IMAGE_NAME:$IMAGE_TAG"
                        docker push $IMAGE_NAME:$IMAGE_TAG
                        docker push $IMAGE_NAME:latest
                    '''
                }
            }
        }
    }

    post {
        success { echo "Pipeline completed successfully!" }
        failure { echo "Pipeline failed!" }
    }
}
