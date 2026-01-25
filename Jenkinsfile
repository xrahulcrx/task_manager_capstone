pipeline {
    agent any

    options {
        skipDefaultCheckout false  // Let Jenkins handle the checkout
    }

    environment {
        APP_NAME   = "task-manager-fastapi"
        RELEASE    = "1.0.0"
        IMAGE_TAG  = "${RELEASE}-${BUILD_NUMBER}"
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
                    sh '''
                        poetry run pytest -v
                    '''
                }

            }
        }

        stage("DockerHub Login (for build + push)") {
            steps{
                script{
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) 
                    {
                        sh '''
                            echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                            echo "Logged into Docker Hub as: ${DOCKERHUB_USER}"
                        '''
                        // Save variables to file
                        sh '''
                        echo "IMAGE_NAME=${DOCKERHUB_USER}/${APP_NAME}" > docker_vars.txt
                        echo "Image: ${DOCKERHUB_USER}/${APP_NAME}:${IMAGE_TAG}"
                        '''
                    }
                }
            }
        }

        stage("Build Docker Image") {
            steps {                
                script{

                    sh '''
                        if [ ! -f docker_vars.txt ]; then
                            echo "docker_vars not found"
                            exit 1
                        fi 
                    '''



                    sh '''
                        . docker_vars.txt
                        echo "Building image: ${IMAGE_NAME}:${IMAGE_TAG}"
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        echo "Image built successfully"
                    '''
                }

            }
        }

        stage("SonarQube Scan") {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                    sonar-scanner \
                      -Dsonar.projectKey=${APP_NAME} \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=${SONAR_HOST_URL} \
                      -Dsonar.token=${SONAR_TOKEN}
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
                    . docker_vars.txt
                    sh '''
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                    echo "Image pushed successfully"
                    '''
            }
        }  
    }

    post {
        success {
            echo "Pipeline completed successfully!"
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
        
        always {
            // Clean up temp file
            sh '''
                rm -f docker_vars.txt || true
                echo "Pipeline finished"
            '''
        }
    }
}
