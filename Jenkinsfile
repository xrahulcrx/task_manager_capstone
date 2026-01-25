pipeline {
    agent any

    options {
        skipDefaultCheckout false  // Let Jenkins handle the checkout
    }

    environment {
        APP_NAME   = "task-manager-fastapi"
        RELEASE    = "1.0.0"
        IMAGE_TAG  = "${RELEASE}-${BUILD_NUMBER}"
        IMAGE_NAME = ""
        SONAR_HOST_URL = "http://sonarqube:9000"
        SONAR_BROWSER_URL = "http://localhost:9000"
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

        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        # Check Poetry installation
                        poetry --version
                        
                        # For [project] format, use pip install instead
                        # Or configure Poetry to handle it
                        poetry install --no-interaction --no-ansi || true

                    '''
                }
            }
        }

        stage("Run Tests") {
            steps {
                script{
                    sh """
                        poetry run pytest -v
                    """
                }

            }
        }

        stage("DockerHub Login (for build + push)") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
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
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                    '''
                }
                
                script{
                    sh """
                        IMAGE_NAME=\$DOCKERHUB_USER/${APP_NAME}
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    """
                }

            }
        }

        stage("SonarQube Scan") {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh """
                    sonar-scanner \
                      -Dsonar.projectKey=${APP_NAME} \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=${SONAR_HOST_URL} \
                      -Dsonar.token=${SONAR_TOKEN}
                    """
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
                    sh """
                    IMAGE_NAME=\$DOCKERHUB_USER/${APP_NAME}
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                    """
            }
        }
        
    }
}
