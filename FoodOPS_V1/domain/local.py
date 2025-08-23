import json
from typing import List

from pydantic import BaseModel, ValidationError


class Local(BaseModel):
    nom: str
    surface: float
    capacite_clients: int
    loyer: float
    prix_fond: float
    visibility: float

    @property
    def visibility_normalized(self) -> float:
        """
        Normalise la visibilité du local en [0..1].
        # On suppose local.visibility ~ 0..5 (adapter si autre échelle).
        """
        return float(self.visibility) / 5.0


def load_local_config(filepath: str) -> List[Local]:
    """Charge la configuration des locaux depuis un fichier JSON.

    Lit un fichier JSON contenant la configuration des locaux organisée par
    type de restaurant et retourne un dictionnaire structuré.

    Paramètres
    ----------
    filepath : str
        Chemin vers le fichier JSON de configuration des locaux.

    Retour
    ------
    Dict[LocalType, List[Local]]
        Dictionnaire mappant chaque type de restaurant à sa liste de locaux
        disponibles.

    Exemple
    -------
    >>> config = load_local_config("local_config.json")
    >>> LocalType.BISTRO in config
    True
    >>> isinstance(config[LocalType.BISTRO][0], Local)
    True

    Lève
    ----
    FileNotFoundError
        Si le fichier de configuration n'existe pas.
    ValueError
        Si le type de restaurant dans le JSON n'est pas valide.
    KeyError
        Si les champs requis pour Local sont manquants dans le JSON.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    config: List[Local] = []
    for local_data in raw_data:
        try:
            config.append(Local.model_validate(local_data))
        except ValidationError as e:
            raise ValueError(
                f"Validation error for local type {local_data['nom']}: {e}"
            )

    return config


# Usage
path = (
    "/home/lepagnol/Documents/Perso/Games/foodopsV0TL/FoodOPS_V1/data/local_config.json"
)
CATALOG_LOCALS = load_local_config(path)
