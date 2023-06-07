FROM python:3.10

# Set up code directory

RUN pip3 install eth-brownie
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY neon-brownie.patch /tmp/
COPY neon-brownie2.patch /tmp/
RUN cd /usr/local/lib/python3.10/site-packages && patch -p0 < /tmp/neon-brownie.patch && patch -p0 < /tmp/neon-brownie2.patch

# Install linux dependencies
RUN apt-get update \
 && apt-get install -y libssl-dev npm

RUN npm install n -g \
 && npm install -g npm@latest

WORKDIR /app
COPY . .
RUN brownie compile