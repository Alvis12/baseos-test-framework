pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
        cron('H 2 * * *')
    }

    stages {
        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install pytest
                '''
            }
        }

        stage('Build images') {
            steps {
                sh 'docker build -t mini-baseos:24.04 baseos/'
                sh 'docker build --build-arg UBUNTU_VERSION=22.04 -t mini-baseos:22.04 baseos/'
            }
        }

        stage('Test') {
            parallel {
                stage('Ubuntu 22.04') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            pytest --image mini-baseos:22.04 --junitxml=reports/ubuntu-22.04.xml
                        '''
                    }
                }
                stage('Ubuntu 24.04') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            pytest --image mini-baseos:24.04 --junitxml=reports/ubuntu-24.04.xml
                        '''
                    }
                }
            }
            
        }
        stage('Security scan') {
                steps {
                    sh '''
                        for v in 22.04 24.04; do
                            docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v trivy-cache:/root/.cache/ \
                            aquasec/trivy:latest image \
                            --scanners vuln \
                            --severity HIGH,CRITICAL \
                            --ignore-unfixed \
                            --exit-code 1 \
                            mini-baseos:$v
                        done
                    '''
                }
        }
    }

    post {
        always {
            junit 'reports/*.xml'
        }
    }
}