from dataclasses import dataclass
from typing import Optional

import pandas as pd

from eos import EosFit


@dataclass
class EvCurve:
    values: list[tuple[float, float]]
    eos_fit: EosFit
    label: Optional[str] = None
