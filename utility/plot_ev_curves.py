import json
import sys

from dataclasses import dataclass, replace
from functools import reduce
from typing import Optional

from dacite import Config, from_dict
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import muni_theme

from eos import Eos, EosFit
from ev_curve import EvCurve


pio.templates.default = "plotly_white"


@dataclass
class InputData:
    title: Optional[str]
    ev_curves: list[EvCurve]


def shift_ev_curve(ev_curve):
    values = np.array(ev_curve.values)
    values[:,1] -= np.min(values[:,1])
    params = {**ev_curve.eos_fit.params, "E0": 0}
    eos_fit = replace(ev_curve.eos_fit, params=params)
    shifted = replace(ev_curve, values=values.tolist(), eos_fit=eos_fit)

    return shifted


def main():
    data = from_dict(
        data_class=InputData,
        data=json.load(sys.stdin),
        config=Config(type_hooks={Eos: Eos.from_id}, cast=[tuple])
    )

    ev_curves = data.ev_curves

    if len(ev_curves) > 1:
        ev_curves = list(map(shift_ev_curve, ev_curves))

    colors = iter(muni_theme.colors)
    figure = go.Figure()

    for ev_curve in ev_curves:
        color = next(colors)
        values = np.array(ev_curve.values)
        eos_fit = ev_curve.eos_fit
        v, e = values[:,0], values[:,1]
        v_p = np.linspace(np.min(v), np.max(v), 100)
        e_p = eos_fit.f(v_p)

        figure.add_trace(
            go.Scatter(
                x=v,
                y=e,
                mode="markers",
                marker_color=color,
                name=ev_curve.label
            )
        )

        figure.add_trace(
            go.Scatter(
                x=v_p,
                y=e_p,
                mode="lines",
                marker_color=color,
                name=f"{eos_fit.eos.title()} fit"
            )
        )

    figure.update_layout(
        title=data.title,
        xaxis_title=r"$V \, [\mathrm{Å}]$",
        yaxis_title=r"$E \, [\mathrm{eV}]$"
    )

    figure.write_image(sys.stdout.buffer, format="jpg")


if __name__ == "__main__":
    main()
