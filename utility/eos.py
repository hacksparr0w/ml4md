from dataclasses import dataclass
from enum import Enum

import numpy as np


def birch_murnaghan(v, E0: float, V0: float, B0: float, B0P: float):
    return (
        E0 +
        ((9 / 16) * V0 * B0) * (
            ((V0 / v) ** (2 / 3) - 1) ** 3 * B0P +
            ((V0 / v) ** (2 / 3) - 1) ** 2 * (6 - 4 * (V0 / v) ** (2 / 3))
        )
    )


def birch_murnaghan_p0(v, e):
    return np.min(e), np.min(v), 1, 1


def mie_gruneisen(v, E0, V0, B, C):
    nu = v / V0

    return (
        E0 +
        (B * V0 / C) -
        ((B * V0 / (C - 1)) * (nu ** (-1 / 3) - nu ** (-C / 3) / C))
    )


class Eos(Enum):
    BIRCH_MURNAGHAN = ("birch_murnaghan", birch_murnaghan, birch_murnaghan_p0)
    MIE_GRUNEISEN = ("mie_gruneisen", mie_gruneisen, None)

    def __init__(self, id: str, f, p0) -> None:
        self.id = id
        self.f = f
        self.p0 = p0

    def __deepcopy__(self, memo):
        return self.id

    def title(self):
        return "-".join(map(lambda x: x.capitalize(), self.id.split("_")))

    @classmethod
    def from_id(cls, id: str) -> "Eos":
        for equation in list(cls):
            if equation.id == id:
                return equation

        raise ValueError


@dataclass
class EosFit:
    eos: Eos
    params: dict

    def __post_init__(self) -> None:
        self.f = lambda v: self.eos.f(v, **self.params)
