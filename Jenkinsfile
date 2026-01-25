pipeline {
    agent any

    options {
        skipDefaultCheckout true
    }

    environment {
        APP_NAME          = "task-manager-fastapi"
        RELEASE           = "1.0"
        IMAGE_TAG         = "${RELEASE}.${BUILD_NUMBER}"

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
                withSonarQubeEnv('sonarqube') {
                    sh '''
                        set -euxo pipefail
                        sonar-scanner \
                          -Dsonar.projectKey=$APP_NAME \
                          -Dsonar.sources=.
                    '''
                }
            }
        }

        stage("Quality Gate") {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
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


        stage("Deploy to k3d") {
            steps {
                sh '''
                    set -eux
                    . ./image.env

                    # Ensure cluster exists
                    k3d cluster list | grep devops-cluster || k3d cluster create devops-cluster --api-port 6550 -p "30080:30080@loadbalancer"

                    # Replace image placeholder
                    sed "s|REPLACE_IMAGE|$IMAGE_NAME:$IMAGE_TAG|g" k8s/deployment.yaml > k8s/deployment.final.yaml

                    kubectl apply -f k8s/deployment.final.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl rollout status deployment/task-manager
                '''
            }
        }

        stage("App Link") {
            steps {
                echo "App URL: http://localhost:30080"
            }
        }
    }

    post {
        success { echo "Pipeline completed successfully!" }
        failure { echo "Pipeline failed!" }
        always  { cleanWs() }
    }
}
