import json
import os
import re
import subprocess
import sys

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from dacite import from_dict


DEFAULT_SCRIPT_FILE_NAME = "minimize.lmp"
DEFAULT_MODEL_FILE_NAME = "graph_compressed.pb"
LOCAL_LMP_EXECUTABLE = "/root/.local/bin/lmp"
GLOBAL_LMP_EXECUTABLE = "lmp"
SYSTEM_DIR = Path(__file__).parent.parent.resolve() / "system"
MODEL_DIR = Path(__file__).parent.parent.resolve() / "model"

COHESIVE_ENERGY_PATTERN = re.compile(
    r"Cohesive energy \(eV\) = ([+-]?([0-9]*[.])?[0-9]+)"
)

FINAL_VOLUME_PATTERN = re.compile(
    r"Final volume \(angstrom\^3\) = ([+-]?([0-9]*[.])?[0-9]+)"
)


@dataclass
class BaselineInputData:
    system: str
    a_initial: float
    mode: str = "baseline"


@dataclass
class DeepMdInputData:
    model: str
    system: str
    a_initial: float
    mode: str = "deepmd"


@dataclass
class OutputData:
    values: list[tuple[float, float]]


def run(command, env=None):
    return subprocess.run(command, capture_output=True, env=env)


def main():
    raw_data = json.load(sys.stdin)
    mode = raw_data.get("mode")
    data_class = None

    if mode == "baseline":
        data_class = BaselineInputData
    elif mode == "deepmd":
        data_class = DeepMdInputData
    else:
        raise ValueError

    parsed_data = from_dict(data_class=data_class, data=raw_data)
    lmp_executable = (
        LOCAL_LMP_EXECUTABLE if Path(LOCAL_LMP_EXECUTABLE).is_file()
        else GLOBAL_LMP_EXECUTABLE
    )

    script_file = (
        SYSTEM_DIR /
        parsed_data.system /
        parsed_data.mode /
        DEFAULT_SCRIPT_FILE_NAME
    )

    values = []
    a_initial = parsed_data.a_initial

    for volume_scale in np.linspace(0.94, 1.06, 20):
        a_final = round(a_initial * volume_scale ** (1 / 3), 3)

        env = {
            **os.environ,
            "MD_A_INITIAL": str(a_initial),
            "MD_A_FINAL": str(a_final)
        }

        if parsed_data.mode == "deepmd":
            model_file = (
                MODEL_DIR /
                parsed_data.model /
                DEFAULT_MODEL_FILE_NAME
            )

            env["MD_DEEPMD_MODEL"] = str(model_file)

        process = run([lmp_executable, "-in", str(script_file)], env=env)
        output = process.stdout.decode()
        final_volume_match = FINAL_VOLUME_PATTERN.search(output)
        cohesive_energy_match = COHESIVE_ENERGY_PATTERN.search(output)

        if not final_volume_match or not cohesive_energy_match:
            raise RuntimeError

        final_volume = float(final_volume_match.group(1))
        cohesive_energy = float(cohesive_energy_match.group(1))

        values.append((final_volume, cohesive_energy))

    output = OutputData(values)
    json.dump(asdict(output), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
