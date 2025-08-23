"""
Domain market primitives: customer segments and budgets.

This module defines the Segment enum and the average budget per segment.
"""

from enum import Enum
from pathlib import Path
from typing import Dict

from pydantic import BaseModel, RootModel

from FoodOPS_V1.utils import load_and_validate


class Segment(Enum):
    """Segments de clientèle (valeurs textuelles alignées avec les données/scoring)."""

    ETUDIANT = "etudiant"
    ACTIF = "actif"
    FAMILLE = "famille"
    TOURISTE = "touriste"
    SENIOR = "senior"


class SegmentDataModel(BaseModel):
    budget_moyen: float
    description: str


class SegmentDataModel(RootModel[Dict[Segment, SegmentDataModel]]):
    pass


data_path = Path(__file__).parent.parent / "data" / "segment_clients.json"
SEGMENT_DATA = load_and_validate(data_path, SegmentDataModel)


print(SEGMENT_DATA)
# Extract budgets from loaded data
BUDGET_PER_SEGMENT: Dict[Segment, float] = {
    Segment(key): float(data["budget_moyen"])
    for key, data in SEGMENT_DATA.model_dump().items()
    if key in [segment.value for segment in Segment]
}
