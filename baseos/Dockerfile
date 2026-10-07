ARG UBUNTU_VERSION=24.04
FROM ubuntu:${UBUNTU_VERSION}

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        git \
        curl \
        ca-certificates \
        tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash svc-app

RUN chmod 640 /etc/shadow

CMD ["bash"]