FROM debian:11

ARG GIT_PRIVATE_KEY

RUN apt update
RUN apt install -y \
  build-essential \
  cmake \
  gfortran \
  git \
  python3 \
  python3-pip \
  rsync

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install poetry

RUN mkdir -p /root/.ssh && \
  chmod 0700 /root/.ssh && \
  ssh-keyscan gitlab.com > /root/.ssh/known_hosts && \
  echo "$GIT_PRIVATE_KEY" > /root/.ssh/id_rsa && \
  chmod 0600 /root/.ssh/id_rsa

RUN mkdir /app
WORKDIR /app
COPY pyproject.toml .

RUN poetry config virtualenvs.create false
RUN poetry install

RUN anvil install mpich
RUN anvil install lammps
RUN anvil install mlip
RUN anvil install bazelisk
RUN anvil install tensorflow
RUN anvil install deepmd-kit
RUN anvil install lammps-mlip-interface

RUN rm /root/.ssh/id_rsa
