pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }

    triggers {
        cron('H 8 * * *')
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PYTHONPATH = '.'

        BASE_UI_URL = 'https://parabank.parasoft.com/parabank'
        BASE_API_URL = 'https://parabank.parasoft.com/parabank/services/bank'

        BROWSER = 'chrome'
        HEADLESS = 'true'

        SELENIUM_REMOTE_URL = 'http://selenium-chrome:4444/wd/hub'

        UI_TIMEOUT = '15'
        API_TIMEOUT = '15'
    }

    stages {
        stage('Checkout') {
            steps {
                git(
                    branch: '001',
                    url: 'https://github.com/DianaTsa/parabank_project.git'
                )
            }
        }

        stage('Prepare environment') {
            steps {
                sh '''
                    set -e

                    rm -rf .venv
                    rm -rf allure-results

                    python3 -m venv .venv
                    . .venv/bin/activate

                    python -m pip install --upgrade pip
                    pip install -r requirements.txt

                    mkdir -p allure-results
                '''
            }
        }

        stage('Wait for Selenium') {
            steps {
                sh '''
                    set -e

                    echo "Waiting for Selenium..."

                    for attempt in $(seq 1 30); do
                        if curl -fsS \
                            http://selenium-chrome:4444/status \
                            > /dev/null; then
                            echo "Selenium is ready"
                            exit 0
                        fi

                        echo "Waiting for Selenium: attempt ${attempt}/30"
                        sleep 2
                    done

                    echo "Selenium did not become ready"
                    exit 1
                '''
            }
        }

        stage('API tests') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    sh '''
                        . .venv/bin/activate

                        python -m pytest \
                            tests/api \
                            -m api \
                            -v \
                            --tb=short \
                            --alluredir=allure-results
                    '''
                }
            }
        }

        stage('UI tests') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    sh '''
                        . .venv/bin/activate

                        python -m pytest \
                            tests/ui \
                            -m ui \
                            -v \
                            --tb=short \
                            --alluredir=allure-results
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                sh '''
                    echo "Allure result files:"
                    find allure-results -maxdepth 1 -type f 2>/dev/null || true
                '''

                archiveArtifacts(
                    artifacts: 'allure-results/**',
                    allowEmptyArchive: true,
                    fingerprint: true
                )

                if (fileExists('allure-results')) {
                    allure(
                        includeProperties: false,
                        jdk: '',
                        results: [
                            [path: 'allure-results']
                        ]
                    )
                } else {
                    echo 'Directory allure-results does not exist'
                }
            }
        }

        cleanup {
            deleteDir()
        }
    }
}