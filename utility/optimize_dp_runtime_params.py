import itertools
import json
import multiprocessing
import os
import re
import subprocess
import sys

from dataclasses import asdict, dataclass
from numbers import Number
from pathlib import Path
from typing import Sequence

from dacite import from_dict


TRAINING_TIME_PATTERN = re.compile(
    r"training time ([+-]?([0-9]*[.])?[0-9]+) s"
)

MODEL_DIR = Path(__file__).parent.parent.resolve() / "model"


@dataclass
class InputData:
    model: str


@dataclass
class OutputData:
    params: tuple[int, int, int]
    training_time: float


def avg(n: Sequence[Number]) -> float:
    return sum(n) / len(n)


def measure_training_time(
        model: str,
        omp_threads: int,
        tf_intra_threads: int,
        tf_inter_threads: int
) -> float:
    working_dir = MODEL_DIR / model
    env = {
        **os.environ,
        "OMP_NUM_THREADS": str(omp_threads),
        "TF_INTRA_OP_PARALLELISM_THREADS": str(tf_intra_threads),
        "TF_INTER_OP_PARALLELISM_THREADS": str(tf_inter_threads)
    }

    proc = subprocess.Popen(
        ["dp", "train", "input.json"],
        cwd=str(working_dir),
        env=env,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )

    times = []

    for line in proc.stderr:
        match = TRAINING_TIME_PATTERN.search(line)

        if not match:
            continue

        time = float(match.group(1))
        times.append(time)

        if len(times) == 5:
            break

    proc.kill()

    avg_time = avg(times)

    return avg_time


def main() -> None:
    data = from_dict(data_class=InputData, data=json.load(sys.stdin))
    params = itertools.product(
        range(1, multiprocessing.cpu_count() + 1),
        repeat=3
    )

    last_params = None
    last_training_time = None

    for item in params:
        training_time = measure_training_time(data.model, *item)

        print(
            f"Measured {training_time}s for training with {item} params.",
            file=sys.stderr,
            flush=True
        )

        if last_training_time is None or last_training_time > training_time:
            last_training_time = training_time
            last_params = item

    output = OutputData(last_params, last_training_time)
    json.dump(asdict(output), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
