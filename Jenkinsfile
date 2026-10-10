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
                        set -eu
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
        
        stage('Update GitOps') {
            steps {
                withCredentials([
                    gitUsernamePassword(
                        credentialsId: 'github-gitops',
                        gitToolName: 'Default'
                    )
                ]) {
                    sh '''
                        set -eu

                        rm -rf gitops

                        git clone \
                          https://github.com/NguyenNgocQuocTrung/argocd-lab.git \
                          gitops

                        cd gitops

                        git config user.name "Jenkins CI"
                        git config user.email "jenkins-ci@users.noreply.github.com"

                        IMAGE="goodboynhatrang/jenkins-ci-demo:$IMAGE_TAG"
                        export IMAGE

                        python3 "$WORKSPACE/update_image.py" \
                          jenkins-demo/deployment.yaml

                        git add jenkins-demo/deployment.yaml

                        if git diff --cached --quiet; then
                            echo "Image unchanged; nothing to commit."
                        else
                            git commit -m "Update demo image to $IMAGE_TAG"
                            git push origin HEAD:main
                        fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed. Check the stage logs.'
        }
    }
}
