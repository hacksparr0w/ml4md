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
  rsync \
  libglib2.0-0 \
  libgl1-mesa-dev \
  libxkbcommon-x11-0 \
  libdbus-1-dev

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install poetry numpy

RUN mkdir -p /root/.ssh && \
  chmod 0700 /root/.ssh && \
  ssh-keyscan gitlab.com > /root/.ssh/known_hosts && \
  echo "$GIT_PRIVATE_KEY" > /root/.ssh/id_rsa && \
  chmod 0600 /root/.ssh/id_rsa

RUN mkdir /app
WORKDIR /app
COPY pyproject.toml .
COPY ml4md ml4md
COPY ml4md_lammps_scripts ml4md_lammps_scripts

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
