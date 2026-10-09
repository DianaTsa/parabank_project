FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
    && apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt

RUN jenkins-plugin-cli \
    --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins