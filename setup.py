#!/usr/bin/env python3

import os
import sys


ROOT_DIRECTORY_PATH = os.path.join(os.getcwd(), "tools")

LAMMPS_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, "lammps")
MLIP_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, "mlip")
MLIP_LAMMPS_INTERFACE_DIRECTORY_PATH = os.path.join(
    ROOT_DIRECTORY_PATH,
    "mlip-lammps-interface"
)

MPICH_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, "mpich")

LAMMPS_REPOSITORY_URL = "https://github.com/lammps/lammps.git"
MLIP_REPOSITORY_URL = "git@gitlab.com:ashapeev/mlip-2.git"
MLIP_LAMMPS_INTERFACE_REPOSITORY_URL = (
    "https://gitlab.com/ashapeev/interface-lammps-mlip-2.git"
)

MPICH_DOWNLOAD_URL = (
    "https://www.mpich.org/static/downloads/4.0.2/mpich-4.0.2.tar.gz"
)

LAMMPS_BUILD_TARGET = "g++_mpich"


class DependencyError(Exception):
    def __init__(self, dependency):
        super().__init__(f"Dependency on '{dependency}' was not satisfied")


def run(*commands):
    for command in commands:
        result = os.system(command)

        if result != 0:
            raise RuntimeError(f"An error occurred while running '{command}'")


def clean_directory(path):
    if os.path.isdir(path):
        os.rmdir(path)


def clone_git_repository(url, path, branch=None):
    args = ["git", "clone"]

    if branch:
        args.extend(["-b", branch])

    args.extend([url, path])

    command = " ".join(args)

    run(command)


def download_file(url, path):
    run(f"curl {url} > {path}")


def untar_file(tar_path, directory_path):
    run(f"tar -xvzf {tar_path} -C {directory_path}")


def install_lammps():
    clean_directory(LAMMPS_DIRECTORY_PATH)

    clone_git_repository(
        LAMMPS_REPOSITORY_URL,
        LAMMPS_DIRECTORY_PATH,
        branch="stable"
    )

    current_directory_path = os.getcwd()
    src_directory_path = os.path.join(LAMMPS_DIRECTORY_PATH, "src")

    os.chdir(src_directory_path)
    run("make yes-openmp")

    os.chdir(current_directory_path)


def install_mpich():
    clean_directory(MPICH_DIRECTORY_PATH)

    current_directory_path = os.getcwd()
    archive_file_path = os.path.join(ROOT_DIRECTORY_PATH, "mpich.tar.gz")
    build_directory_path = os.path.join(MPICH_DIRECTORY_PATH, "build")

    download_file(MPICH_DOWNLOAD_URL, archive_file_path)
    untar_file(archive_file_path, ROOT_DIRECTORY_PATH)
    os.remove(archive_file_path)

    os.chdir(ROOT_DIRECTORY_PATH)
    run(f"ls -1 | grep mpich | xargs -I _ mv _ {MPICH_DIRECTORY_PATH}")

    os.chdir(MPICH_DIRECTORY_PATH)
    run(
        "FFLAGS=-fallow-argument-mismatch FCFLAGS=-fallow-argument-mismatch "
        f"./configure --prefix={build_directory_path}",
        "make",
        "make install"
    )

    os.chdir(current_directory_path)


def install_mlip():
    clean_directory(MLIP_DIRECTORY_PATH)

    current_directory_path = os.getcwd()

    clone_git_repository(MLIP_REPOSITORY_URL, MLIP_DIRECTORY_PATH)
    os.chdir(MLIP_DIRECTORY_PATH)
    run(
        "./configure --enable-debug",
        "make mlp",
        "make libinterface"
    )

    os.chdir(current_directory_path)


def install_mlip_lammps_interface():
    clean_directory(MLIP_LAMMPS_INTERFACE_DIRECTORY_PATH)

    current_directory_path = os.getcwd()
    mlip_libinterface_path = os.path.join(
        MLIP_DIRECTORY_PATH,
        "lib",
        "lib_mlip_interface.a"
    )

    mpich_bin_directory_path = os.path.join(
        MPICH_DIRECTORY_PATH,
        "build",
        "bin"
    )

    lmp_executable_file = os.path.join(
        MLIP_LAMMPS_INTERFACE_DIRECTORY_PATH,
        f"lmp_{LAMMPS_BUILD_TARGET}"
    )

    if not os.path.exists(mlip_libinterface_path):
        raise DependencyError("mlip")

    if not os.path.exists(LAMMPS_DIRECTORY_PATH):
        raise DependencyError("lammps")

    if not os.path.exists(mpich_bin_directory_path):
        raise DependencyError("mpich")

    path = os.environ["PATH"]
    path = path.split(":")
    path = [mpich_bin_directory_path, *path]
    path = ":".join(path)

    os.environ["PATH"] = path

    clone_git_repository(
        MLIP_LAMMPS_INTERFACE_REPOSITORY_URL,
        MLIP_LAMMPS_INTERFACE_DIRECTORY_PATH
    )

    os.chdir(MLIP_LAMMPS_INTERFACE_DIRECTORY_PATH)
    run(
        f"cp {mlip_libinterface_path} ./lib_mlip_interface.a",
        f"./install.sh {LAMMPS_DIRECTORY_PATH} {LAMMPS_BUILD_TARGET}",
        "mkdir ./bin",
        f"ln -s {lmp_executable_file} ./bin/lmp"
    )

    os.chdir(current_directory_path)


def main(args):
    if len(args) == 2 and args[0] == "install":
        option = args[1]

        if option == "all":
            install_mpich()
            install_lammps()
            install_mlip()
            install_mlip_lammps_interface()
            return

        if option == "lammps":
            install_lammps()
            return

        if option == "mpich":
            install_mpich()
            return

        if option == "mlip":
            install_mlip()
            return

        if option == "mlip-lammps-interface":
            install_mlip_lammps_interface()
            return

    print(
        "Invalid arguments specified.\n"
        "The following commands are currently supported:\n"
        "  setup.py install all                   - Downloads and install all"
        "  setup.py install lammps                - Downloads and installs "
        "LAMMPS locally\n"
        "  setup.py install mpich                 - Downloads and installs "
        "MPICH locally\n"
        "  setup.py install mlip                  - Downloads and installs "
        "MLIP locally\n"
        "  setup.py install mlip-lammps-interface - Downloads and installs "
        "MLIP-LAMMPS interface locally"
    )

    exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
