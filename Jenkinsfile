pipeline {

    environment {
        APP_NAME = "task-manager-fastapi"
        RELEASE = "1.0.0"
        DOCKER_USER = "rahulcrx"
        DOCKER_PASS = "docker-token"
        IMAGE_NAME = "${DOCKER_USER}" + "/" + "$(APP_NAME)"
        IMAGE_TAG = "${RELEASE}-${BUILD_NUMBER}"
    }




    stages {
        stage("Cleanup Workspace"){

            steps {
                CleanWs()
            }
        }
    }
}