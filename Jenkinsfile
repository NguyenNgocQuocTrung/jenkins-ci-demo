
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.12-slim \
                      sh -c "pip install --no-cache-dir -r requirements.txt && pytest -q"
                '''
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        IMAGE="$DOCKERHUB_USER/jenkins-ci-demo:$IMAGE_TAG"

                        echo "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USER" \
                          --password-stdin

                        docker build -t "$IMAGE" .
                        docker push "$IMAGE"

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI pipeline succeeded!'
        }
        failure {
            echo 'CI pipeline failed. Check the stage logs.'
        }
    }
}
