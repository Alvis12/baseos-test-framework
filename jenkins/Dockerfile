FROM jenkins/jenkins:lts

USER root

COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-venv && \
    rm -rf /var/lib/apt/lists/*

USER jenkins