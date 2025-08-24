"""Gestion du personnel / staff."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, Mapping, Optional

from game_engine.domain.types_VO import RestaurantType

# IMPORTANT : pas d'import du package domain complet ici (pour éviter les cycles)
# Si tu dois typer Restaurant ailleurs, fais-le avec TYPE_CHECKING dans ce fichier-là.


class Role(str, Enum):
    SERVEUR = "SERVEUR"
    CUISINIER = "CUISINIER"
    MANAGER = "MANAGER"


# Pour les endroits du code qui faisaient référence à “ALLOWED_ROLES”
ALLOWED_ROLES = {Role.SERVEUR, Role.CUISINIER, Role.MANAGER}

# Productivité “minutes par tour” de base par rôle
# (8h * 60min = 480min ; le manager file un coup de main léger aux deux)
ROLE_PRODUCTIVITY: Dict[Role, Dict[str, int]] = {
    Role.SERVEUR: {"service_minutes": 480, "kitchen_minutes": 0},
    Role.CUISINIER: {"service_minutes": 0, "kitchen_minutes": 480},
    Role.MANAGER: {"service_minutes": 120, "kitchen_minutes": 120},
}

# Certains modules faisaient allusion à ROLE_BANK — on l'expose “vide” pour compat,
# ou catégorisation front/back si tu veux t'en servir plus tard.
ROLE_BANK: Dict[Role, str] = {
    Role.SERVEUR: "front",
    Role.CUISINIER: "back",
    Role.MANAGER: "both",
}


@dataclass
class Employe:
    nom: str
    role: Role
    salaire_total: float = 0.0  # coût total mensuel/“tour”
    productivite_bonus: float = 1.0  # multiplicateur (ex : 1.1 = +10%)
    present: bool = True  # si absent/malade …

    # Etats calculés (optionnels)
    service_minutes: int = field(default=0, init=False)
    kitchen_minutes: int = field(default=0, init=False)

    def compute_minutes(self) -> None:
        """Calcule les minutes dispo pour ce tour selon le rôle et le bonus."""
        base = ROLE_PRODUCTIVITY.get(
            self.role, {"service_minutes": 0, "kitchen_minutes": 0}
        )
        if not self.present:
            self.service_minutes = 0
            self.kitchen_minutes = 0
            return
        sm = int(base["service_minutes"] * float(self.productivite_bonus))
        km = int(base["kitchen_minutes"] * float(self.productivite_bonus))
        self.service_minutes = max(0, sm)
        self.kitchen_minutes = max(0, km)


class Department(Enum):
    CUISINE = "CUISINE"
    SALLE = "SALLE"
    SUPPORT = "SUPPORT"


class ProductivityBank(Enum):
    PROD = "prod"
    SERVICE = "service"


class Role(Enum):
    # value = (code, Department, minutes_productives_par_heure, bank)
    COMMIS = ("COMMIS", Department.CUISINE, 55, ProductivityBank.PROD)
    CUISINIER = ("CUISINIER", Department.CUISINE, 60, ProductivityBank.PROD)
    CHEF = ("CHEF", Department.CUISINE, 65, ProductivityBank.PROD)
    PLONGE = ("PLONGE", Department.CUISINE, 45, ProductivityBank.PROD)
    CAISSIER = ("CAISSIER", Department.SALLE, 60, ProductivityBank.SERVICE)
    SERVEUR = ("SERVEUR", Department.SALLE, 55, ProductivityBank.SERVICE)
    RUNNER = ("RUNNER", Department.SALLE, 60, ProductivityBank.SERVICE)
    MAITRE_D = ("MAITRE_D", Department.SALLE, 45, ProductivityBank.SERVICE)
    MANAGER = ("MANAGER", Department.SUPPORT, 20, None)

    def __new__(
        cls,
        code: str,
        department: Department,
        prod_min: int,
        bank: Optional[ProductivityBank] = None,
    ):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.department = department
        obj.prod_minutes_per_hour = prod_min
        obj.bank = bank
        return obj

    def __str__(self) -> str:
        return self.value  # "COMMIS", etc.


ALLOWED_ROLES: Mapping[RestaurantType, FrozenSet[Role]] = {
    RestaurantType.FAST_FOOD: frozenset(
        {
            Role.CUISINIER,
            Role.COMMIS,
            Role.PLONGE,
            Role.CAISSIER,
            Role.RUNNER,
            Role.MANAGER,
        }
    ),
    RestaurantType.BISTRO: frozenset(
        {
            Role.CUISINIER,
            Role.COMMIS,
            Role.CHEF,
            Role.PLONGE,
            Role.CAISSIER,
            Role.SERVEUR,
            Role.RUNNER,
            Role.MANAGER,
        }
    ),
    RestaurantType.GASTRO: frozenset(
        {
            Role.CUISINIER,
            Role.CHEF,
            Role.COMMIS,
            Role.PLONGE,
            Role.SERVEUR,
            Role.MAITRE_D,
            Role.RUNNER,
            Role.MANAGER,
        }
    ),
}


def role_allowed(restaurant_type: RestaurantType, role: Role) -> bool:
    return role in ALLOWED_ROLES[restaurant_type]


@dataclass(frozen=True, slots=True)
class StaffMember:
    nom: str
    role: Role
    heures_par_tour: float  # ex. 160
    salaire_total: float

    @property
    def cout_horaire(self) -> float:
        return self.salaire_total / self.heures_par_tour

    @property
    def minutes_productives_par_heure(self) -> int:
        return self.role.prod_minutes_per_hour

    @property
    def bank(self) -> Optional[ProductivityBank]:
        return self.role.bank
