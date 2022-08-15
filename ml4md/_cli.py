from pathlib import Path

import click
import ovito.io
import ovito.vis
import psutil

from anvil import Paths, run


@click.command("render")
@click.argument(
    "dump_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True
)
@click.argument(
    "output_file",
    type=click.Path(path_type=Path),
    required=True
)
def render_command(dump_file: Path, output_file: Path) -> None:
    pipeline = ovito.io.import_file(str(dump_file))
    pipeline.add_to_scene()

    viewport = ovito.vis.Viewport(
        type=ovito.vis.Viewport.Type.Ortho,
        camera_dir=(2, 1, -1)
    )

    viewport.zoom_all()
    viewport.render_anim(
        renderer=ovito.vis.TachyonRenderer(),
        size=(800, 600),
        fps=30,
        filename=str(output_file)
    )


@click.command("run")
@click.argument(
    "script_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True
)
def run_command(script_file: Path) -> None:
    paths = Paths(Path.cwd() / "packages", None)
    cpu_count = psutil.cpu_count(logical=False)
    thread_count = psutil.cpu_count() // cpu_count
    mpich_executable = (
        paths.of("mpich").current_package_build_directory
        / "bin"
        / "mpirun"
    )

    lammps_executable = (
        paths.of("lammps-mlip-interface").current_package_build_directory
        / "bin"
        / "lmp"
    )

    run([
        str(mpich_executable),
        "-np",
        str(cpu_count),
        str(lammps_executable),
        "-sf",
        "omp",
        "-pk",
        "omp",
        str(thread_count),
        "-in",
        str(script_file)
    ])


@click.group()
def cli():
    pass


cli.add_command(render_command)
cli.add_command(run_command)
