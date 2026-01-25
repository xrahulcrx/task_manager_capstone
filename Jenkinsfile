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
                    // Store the username in an environment variable
                    script {
                        env.DOCKER_USER = "${DOCKERHUB_USER}"
                        env.IMAGE_NAME = "${DOCKERHUB_USER}/${APP_NAME}"
                    }
                    sh '''
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        echo "Logged into Docker Hub as: ${DOCKERHUB_USER}"
                    '''
                }
            }
        }

        stage("Build Docker Image") {
            steps {                
                script{
                    sh """
                        echo "Building image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                        docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} .
                        docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} ${env.IMAGE_TAG}:latest
                        echo "Image built successfully"
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

    post {
        success {
            echo "🎉 Pipeline completed successfully!"
            script {
                currentBuild.description = "Build ${BUILD_NUMBER}"
            }
        }

        failure {
            echo "Pipeline failed"
            script {
                currentBuild.description = "Build ${BUILD_NUMBER}"
            }
        }
    }
}
