FROM debian:11

ARG GIT_PRIVATE_KEY

RUN apt update
RUN apt install -y \
  build-essential \
  gfortran \
  curl \
  git \
  python3

RUN mkdir -p /root/.ssh && \
  chmod 0700 /root/.ssh && \
  ssh-keyscan gitlab.com > /root/.ssh/known_hosts && \
  echo "$GIT_PRIVATE_KEY" > /root/.ssh/id_rsa && \
  chmod 0600 /root/.ssh/id_rsa

RUN mkdir /app
WORKDIR /app
COPY setup.py .
COPY tools tools
RUN python3 ./setup.py install all
RUN rm /root/.ssh/id_rsa
