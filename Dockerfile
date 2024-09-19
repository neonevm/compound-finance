FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# Install common dependencies
RUN apt update && \
    apt upgrade -y && \
# Prepare repo for node 18
    apt install -y software-properties-common python-dev ca-certificates curl gnupg git && \
    mkdir /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
# Install py3.10 from deadsnakes repository and pip from standard ubuntu packages
    add-apt-repository ppa:deadsnakes/ppa && apt update && \
    apt install -y python3.10 python3.10-distutils nodejs build-essential

RUN update-alternatives --install /usr/bin/python3 python /usr/bin/python3.10 2
RUN update-alternatives --install /usr/bin/python3 python /usr/bin/python3.8 1

# Install allure
RUN apt install default-jdk -y

# Install UI libs
RUN apt install -y libxkbcommon0 \
    libxdamage1 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    xvfb


RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 && \
    pip3 install uv && \
    uv venv

ENV VIRTUAL_ENV=/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Download solc separatly as hardhat implementation is flucky
ENV DOWNLOAD_PATH="/root/.cache/hardhat-nodejs/compilers-v2/linux-amd64" \
    REPOSITORY_PATH="https://binaries.soliditylang.org/linux-amd64" \
    SOLC_BINARY="solc-linux-amd64-v0.8.10+commit.fc410830"
RUN mkdir -p ${DOWNLOAD_PATH} && \
    curl -o ${DOWNLOAD_PATH}/${SOLC_BINARY} ${REPOSITORY_PATH}/${SOLC_BINARY} && \
    curl -o ${DOWNLOAD_PATH}/list.json ${REPOSITORY_PATH}/list.json && \
    chmod -R 755 ${DOWNLOAD_PATH}
RUN apt -y install python3.10-dev
RUN uv pip install "cython<3.0.0" wheel setuptools ipfshttpclient==0.8.0a2 py-solc-x==1.1.1

RUN uv pip install "pyyaml==5.4.1" --no-build-isolation
RUN uv pip install eth-brownie==1.19.3


COPY neon-brownie.patch /tmp/
COPY neon-brownie2.patch /tmp/

RUN cd /.venv/lib/python3.10/site-packages && patch -p0 < /tmp/neon-brownie.patch && patch -p0 < /tmp/neon-brownie2.patch



WORKDIR /app
COPY . .
RUN brownie compile