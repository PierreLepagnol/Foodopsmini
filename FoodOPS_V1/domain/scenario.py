"""
Scénarios de population (par tour = 1 mois).
Ces données sont affichées au début et utilisées par le moteur de demande.
"""

import json
from pathlib import Path
from typing import Dict, Mapping, Optional

from pydantic import BaseModel, Field

from FoodOPS_V1.domain.market import Segment


class Scenario(BaseModel):
    """
    Profil de demande du marché pour un tour de jeu (1 mois).

    Exemple de scénario:
    {
    "quartier_etudiant": {
        "name": "Quartier étudiant animé",
        "population_total": 5000,
        "segments_share": {
            Segment.ETUDIANT: 0.6,
            Segment.ACTIF: 0.2,
            Segment.FAMILLE: 0.1,
            Segment.TOURISTE: 0.05,
            Segment.SENIOR: 0.05
        },
        "note": "Fort volume midi, sensibilité prix élevée."
    }
    """

    name: str
    nb_tours: int = Field(ge=1, description="Nombre de tours (1 tour = 1 mois)")
    population_total: int = Field(ge=0, description="Clients potentiels / mois")
    segments_share: Dict[Segment, float]
    note: str = ""

    def show_scenario(self) -> None:
        print(f"📍 Scénario : {self.name}")
        population_total = self.population_total
        population_total = f"{population_total:,}".replace(",", " ")
        if self.note:
            print(f"📝 {self.note}")
        print(f"👥 Population totale potentielle (mois) : {population_total}")
        print("🔎 Répartition :")
        for k in ("étudiant", "actif", "famille", "touriste", "senior"):
            share = self.segments_share[k]
            print(f"- {k.capitalize():9s} : {int(share * 100)}%")

    def compute_segment_quantities(self) -> Dict[Segment, int]:
        """Convertit les parts du scénario en volumes entiers par segment."""
        demand = {
            segment: int(round(self.population_total * share))
            for segment, share in self.segments_share.items()
        }
        return demand


def load_scenarios(json_path: Optional[Path | str] = None) -> Dict[str, Scenario]:
    """Charge les scénarios depuis le JSON et valide via Pydantic.

    Structure JSON attendue: { "code": { "name": ..., "population_total": ..., "segments_share": {...}, "note": ... }, ... }
    """

    path = Path(json_path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, Mapping):
        raise ValueError(
            "Le fichier scenarios.json doit contenir un objet JSON racine (mapping code -> scenario)."
        )
    scenarios: Dict[str, Scenario] = {}
    for code, payload in data.items():
        new_payload = {**payload, "nb_tours": 12}
        scenarios[code] = Scenario(**new_payload)
    return scenarios


path = "/home/lepagnol/Documents/Perso/Games/foodopsV0TL/FoodOPS_V1/data/scenarios.json"
CATALOG_SCENARIOS: Dict[str, Scenario] = load_scenarios(path)


def get_default_scenario() -> Scenario:
    """Retourne le scénario par défaut (centre-ville si disponible)."""
    if CATALOG_SCENARIOS:
        return CATALOG_SCENARIOS.get("centre_ville") or next(
            iter(CATALOG_SCENARIOS.values())
        )
    # Si rien n'est chargé (ex: fichier manquant), on renvoie un stub minimal
    return Scenario(
        name="Centre-ville mixte",
        population_total=8000,
        segments_share={
            Segment.ETUDIANT: 0.25,
            Segment.ACTIF: 0.40,
            Segment.FAMILLE: 0.15,
            Segment.TOURISTE: 0.10,
            Segment.SENIOR: 0.10,
        },
        note="Mix équilibré, budgets variés.",
    )


# Plan de Financement


class FinancingPlan(BaseModel):
    """Simple plan de financement retourné par `propose_financing`.

    Champs clés: apports, prêts (banque/BPI), encours, mensualités et cash initial.
    """

    apport: float
    bank_loan: float
    bpi_loan: float
    frais_dossier: float
    bank_monthly: float
    bpi_monthly: float
    bank_outstanding: float
    bpi_outstanding: float
    cash_initial: float


def propose_financing(fonds_price: float, equip_default: float) -> FinancingPlan:
    """Calcule un plan de financement automatique selon des règles fixes.

    Applique les constantes APPORT_FIXE, BANQUE_FIXE, BPI_MAX pour calculer
    les prêts nécessaires, les mensualités et la trésorerie initiale disponible.

    Args:
        fonds_price: Prix du fonds de commerce
        equip_default: Investissement équipement par défaut

    Returns:
        FinancingPlan complet avec tous les montants et mensualités
    """
    APPORT_FIXE = 50_000.0
    BANQUE_FIXE = 250_000.0
    BPI_MAX = 20_000.0
    FRAIS_PCT = 0.03
    TAUX_BANQUE = 0.045  # annuel
    TAUX_BPI = 0.025  # annuel
    DUREE_BANQUE = 60  # mois
    DUREE_BPI = 48  # mois

    besoin_total = fonds_price + equip_default

    apport = APPORT_FIXE
    bank_loan = BANQUE_FIXE
    reste = besoin_total - (apport + bank_loan)

    bpi_loan = max(0.0, min(BPI_MAX, reste))
    frais_dossier = (bank_loan + bpi_loan) * FRAIS_PCT

    # mensualités simples (amortissement constant sur durée, intérêt moyen)
    bank_monthly = (bank_loan / DUREE_BANQUE) + (bank_loan * TAUX_BANQUE / 12)
    bpi_monthly = (bpi_loan / DUREE_BPI) + (bpi_loan * TAUX_BPI / 12)

    cash_initial = apport + bank_loan + bpi_loan - besoin_total - frais_dossier

    return FinancingPlan(
        apport=apport,
        bank_loan=bank_loan,
        bpi_loan=bpi_loan,
        frais_dossier=frais_dossier,
        bank_monthly=bank_monthly,
        bpi_monthly=bpi_monthly,
        bank_outstanding=bank_loan,
        bpi_outstanding=bpi_loan,
        cash_initial=cash_initial,
    )
