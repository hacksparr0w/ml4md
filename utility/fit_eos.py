import inspect
import json
import sys

from dataclasses import asdict, dataclass

import numpy as np
import scipy.optimize

from dacite import Config, from_dict

from eos import Eos, EosFit
from ev_curve import EvCurve


@dataclass
class InputData:
    values: list[tuple[float, float]]


def fit_eos(values, eos):
    v, e = values[:,0], values[:,1]
    params, _ = scipy.optimize.curve_fit(eos.f, v, e, p0=eos.p0(v, e))
    param_names = list(inspect.signature(eos.f).parameters.keys())[1:]
    fit = EosFit(eos, dict(zip(param_names, params)))

    return fit


def main():
    data = from_dict(
        data_class=InputData,
        data=json.load(sys.stdin),
        config=Config(cast=[tuple])
    )

    values = np.array(data.values)
    eos = Eos.BIRCH_MURNAGHAN
    fit = fit_eos(values, eos)

    ev_curve = EvCurve(values=data.values, eos_fit=fit)

    json.dump(asdict(ev_curve), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
