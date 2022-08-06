# ml4md

Implementation of various machine learning methods for molecular dynamics

## Installation

The following Debian packages are required to install and run ml4md.

```sh
apt install build-essential gfortran curl git python3
```

After setting up these dependencies, run the following command to locally
compile the MD tool infrastructure used by ml4md.

```sh
python3 ./setup.py install all
```

You can also use Docker for containing the whole environment. The following
command builds a Docker image for running ml4md virtually.

```sh
docker build -t ml4md --build-arg GIT_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" .
```

## Examples

The following example runs LAMMPS through MPI utilizing 12 cores and 2
threads.

```sh
mpirun -np 12 lmp -sf omp -pk omp 2 -in in.script
```

## Resources
 - [MLIP2 Tutorial][1]
 - [MLIP2 User Manual][2]

[1]: https://gitlab.com/ashapeev/mlip-2-tutorials
[2]: https://gitlab.com/ashapeev/mlip-2-paper-supp-info/-/blob/master/manual.pdf
