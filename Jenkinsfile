pipeline {
    agent any

    environment {
        APP_IMAGE = "task-manager-fastapi:latest"
        SONAR_HOST_URL = "http://sonarqube:9000"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build FastAPI Docker Image") {
            steps {
                sh "docker build -t ${APP_IMAGE} ."
            }
        }

        stage("Run Container Test") {
            steps {
                sh """
                docker rm -f fastapi_test || true
                docker run -d --name fastapi_test -p 8001:8000 ${APP_IMAGE}
                sleep 5
                docker logs fastapi_test
                docker rm -f fastapi_test
                """
            }
        }

        stage("SonarQube Scan") {
            steps {
                sh """
                sonar-scanner \
                  -Dsonar.projectKey=task-manager-fastapi \
                  -Dsonar.sources=. \
                  -Dsonar.host.url=${SONAR_HOST_URL} \
                  -Dsonar.login=admin \
                  -Dsonar.password=admin
                """
            }
        }
    }

    post {
        always {
            echo "Pipeline finished!"
        }
    }
}
