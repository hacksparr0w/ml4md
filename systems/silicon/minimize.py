import os
import re
import subprocess
import sys

import numpy as np
import scipy.optimize


COHESIVE_ENERGY_PATTERN = re.compile(
    r"Cohesive energy \(eV\) = ([+-]?([0-9]*[.])?[0-9]+)"
)

FINAL_VOLUME_PATTERN = re.compile(
    r"Final volume \(angstrom\^3\) = ([+-]?([0-9]*[.])?[0-9]+)"
)


def run(command, env=None):
    return subprocess.run(command, capture_output=True, env=env)


def main():
    args = sys.argv[1:]
    data = []

    if len(args) != 1:
        raise ValueError(
            "Please specify exactly one argument for initial volume scale"
        )

    initial_volume_scale = float(args[0])

    for final_volume_scale in np.linspace(0.94, 1.06, 20):
        final_volume_scale = round(final_volume_scale, 3)

        env = {
            **os.environ,
            "MD_INITIAL_VOLUME_SCALE": str(initial_volume_scale),
            "MD_FINAL_VOLUME_SCALE": str(final_volume_scale)
        }

        process = run(
            ["/root/.local/bin/lmp", "-in", "./baseline/minimize.lmp"],
            env=env
        )

        output = process.stdout.decode()
        final_volume_match = FINAL_VOLUME_PATTERN.search(output)
        cohesive_energy_match = COHESIVE_ENERGY_PATTERN.search(output)

        if not final_volume_match or not cohesive_energy_match:
            raise RuntimeError

        final_volume = float(final_volume_match.group(1))
        cohesive_energy = float(cohesive_energy_match.group(1))

        data.append([final_volume, cohesive_energy])

    data = np.array(data)
    np.savetxt("./baseline/minimize.csv", data)


if __name__ == "__main__":
    main()
