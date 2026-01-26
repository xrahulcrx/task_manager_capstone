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

        stage("Run Poetry Tests") {
            steps {
                sh '''
                    set -euxo pipefail
                    poetry run pytest -v
                '''
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

        stage("Build Docker Image") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]){
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

        stage("Push Docker Image") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                        set -euxo pipefail
                        # === CRITICAL: LOGIN TO DOCKER HUB ===
                        echo "Logging into Docker Hub as user: $DOCKERHUB_USER"
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        IMAGE_NAME="$DOCKERHUB_USER/$APP_NAME"
                        echo "Pushing image: $IMAGE_NAME:$IMAGE_TAG"
                        docker push $IMAGE_NAME:$IMAGE_TAG
                        docker push $IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage("Create k3d Cluster") {
            steps {
                sh '''
                    set -euxo pipefail

                    CLUSTER_NAME="devops-cluster"

                    echo "Checking k3d cluster..."
                    if k3d cluster list | grep -q "$CLUSTER_NAME"; then
                      echo "Cluster already exists: $CLUSTER_NAME"
                      # Just ensure we're using the right context
                      kubectl config use-context k3d-$CLUSTER_NAME
                    else
                      echo "Creating cluster: $CLUSTER_NAME"
                      k3d cluster create "$CLUSTER_NAME" \
                        --api-port 6550 \
                        -p "30080:30080@loadbalancer"
                      # k3d automatically switches context on creation
                    fi

                    echo "Current kubectl context:"
                    kubectl config current-context

                    echo "Kubernetes nodes:"
                    kubectl get nodes
                '''
            }
        }

        stage("App Links") {
            steps {
                echo "SonarQube Dashboard: ${SONAR_BROWSER_URL}/dashboard?id=${APP_NAME}"
                echo "App URL: http://localhost:30080/docs"
                echo "Tasks URL: http://localhost:30080/tasks"
            }
        }
    }

    post {
        success { echo "Pipeline completed successfully!" }
        failure { echo "Pipeline failed!" }
        always  { cleanWs() }
    }
}
