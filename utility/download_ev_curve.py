import inspect
import json
import sys

from dataclasses import asdict, dataclass

from mp_api.client import MPRester
from dacite import from_dict

from eos import Eos, EosFit
from ev_curve import EvCurve


@dataclass
class InputData:
    material_id: str


def download_ev_curve(material_id, eos):
    with MPRester() as mpr:
        data = mpr.eos.get_data_by_id(material_id)
        values = sorted(zip(data.volumes, data.energies), key=lambda x: x[0])
        param_names = list(inspect.signature(eos.f).parameters.keys())[1:]
        params = dict(map(lambda k: (k, data.eos[eos.id][k]), param_names))
        eos_fit = EosFit(eos, params)
        ev_curve = EvCurve(material_id, values, eos_fit)

        return ev_curve


def main():
    data = from_dict(data_class=InputData, data=json.load(sys.stdin))

    ev_curve = download_ev_curve(data.material_id, Eos.MIE_GRUNEISEN)

    json.dump(asdict(ev_curve), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
