"""
Journal, comptes, compte de résultat et bilan (format FR simplifié).
Sans TVA pour l'instant, focus pédagogie.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from enum import Enum
from pydantic import BaseModel


class TypeOperation(Enum):
    DEBIT = "D"
    CREDIT = "C"


@dataclass
class Entry:
    """Une écriture comptable regroupant plusieurs lignes.

    Chaque écriture appartient à un tour (1 tour = 1 mois dans le jeu) et
    contient un libellé ainsi qu'une liste de lignes débit/crédit.

    Attributes:
        tour: Numéro du tour auquel l'écriture se rattache.
        lines: Lignes de l'écriture sous la forme `(compte, montant, 'D'|'C')`.
        label: Libellé lisible par l'humain décrivant l'opération.
    """

    tour: int
    lines: List[Tuple[str, float, TypeOperation]]  # (compte, montant, 'D'|'C')
    label: str = ""


# ------- États (compte de résultat / bilan) -------


class Actif(BaseModel):
    immobilisations_brutes: float
    amortissements_cumules: float
    trésorerie: float
    immobilisations_nettes: float
    total: float


class Passif(BaseModel):
    capitaux_propres: float
    emprunts: float
    total: float


class BalanceSheet(BaseModel):
    actif: Actif
    passif: Passif


@dataclass
class Ledger:
    """Livre de compte"""

    entries: List[Entry] = field(default_factory=list)

    def post(
        self, tour: int, label: str, lines: List[Tuple[str, float, TypeOperation]]
    ):
        """Ajoute une écriture au grand livre après contrôle d'équilibre.

        Args:
            tour: Numéro de tour (1 tour = 1 mois).
            label: Description courte de l'opération.
            lines: Liste de tuples `(compte, montant, 'D'|'C')`.

        Raises:
            ValueError: Si la somme des débits n'est pas égale à la somme des crédits.
        """
        # Contrôle d'équilibre (débit = crédit) avec un arrondi de sécurité
        d = sum(m for c, m, dc in lines if dc == TypeOperation.DEBIT)
        c = sum(m for c, m, dc in lines if dc == TypeOperation.CREDIT)
        if round(d - c, 2) != 0.0:
            raise ValueError(f"Écriture non équilibrée '{label}': {d} != {c}")

        self.entries.append(Entry(tour=tour, lines=lines, label=label))

    def balance_accounts(self, tour_max: int = None) -> Dict[str, float]:
        """Calcule les soldes des comptes au format (Débit - Crédit).

        Args:
            tour_max: Si fourni, ne prend en compte que les écritures du tour
                `<= tour_max`. Sinon, considère tout l'historique.

        Returns:
            Un dictionnaire `{numero_compte: solde}` selon la convention
            Débit moins Crédit.
        """

        account_balances: Dict[str, float] = {}

        if not tour_max:
            return {}

        def compute_balance(entry: Entry) -> Dict[str, float]:
            # Process each line in the entry
            for account_number, amount, operation_type in entry.lines:
                # Initialize account balance if not exists
                if account_number not in account_balances:
                    account_balances[account_number] = 0.0

                # Apply debit-credit convention: Debit adds, Credit subtracts
                if operation_type == TypeOperation.DEBIT:
                    account_balances[account_number] += amount
                else:  # TypeOperation.CREDIT
                    account_balances[account_number] -= amount
            return account_balances

        account_balances = [
            compute_balance(entry) for entry in self.entries if entry.tour > tour_max
        ]

        return account_balances

    def balance_sheet(self, tour_max: int = None) -> BalanceSheet:
        """Construit un bilan simplifié (actif/passif) à partir des soldes.

        Args:
            bal: Dictionnaire `{compte: solde}` (Débit - Crédit) tel que renvoyé
                par `Ledger.balance_accounts`.

        Returns:
            Un dictionnaire structuré avec deux clés `Actif` et `Passif`.
        """

        bal = self.balance_accounts(tour_max)
        immobilisations_brutes = bal.get("215", 0.0)
        amortissements_cumules = -bal.get("2815", 0.0)
        trésorerie = bal.get("512", 0.0)

        actif = Actif(
            immobilisations_brutes=immobilisations_brutes,
            amortissements_cumules=amortissements_cumules,
            trésorerie=trésorerie,
            immobilisations_nettes=immobilisations_brutes + amortissements_cumules,
            total=(immobilisations_brutes + amortissements_cumules) + trésorerie,
        )

        passif = Passif(
            capitaux_propres=-bal.get("101", 0.0),
            emprunts=-bal.get("164", 0.0),
            total=bal.get("101", 0.0) + bal.get("164", 0.0),
        )

        return BalanceSheet(
            actif=actif,
            passif=passif,
        )


# ------- Générateurs d'écritures types (par tour) -------


def post_opening(
    cash: float,
    equipment: float,
    loans_total: float,
    equity: Optional[float] = None,
):
    """Passe l'écriture d'ouverture en équilibrant actifs et passifs.

    Args:
        equity: Capitaux propres injectés au démarrage (compte 101).
            Si None, il sera calculé pour équilibrer Débit et Crédit.
        cash: Trésorerie initiale en banque (compte 512).
        equipment: Valeur brute des immobilisations (compte 215).
        loans_total: Encours d'emprunts au passif (compte 164).
    """
    lines: List[Tuple[str, float, TypeOperation]] = []
    if cash > 0:
        lines.append(("512", cash, TypeOperation.DEBIT))
    if equipment > 0:
        lines.append(("215", equipment, TypeOperation.DEBIT))
    if loans_total > 0:
        lines.append(("164", loans_total, TypeOperation.CREDIT))

    # Capitaux propres = équilibre
    # Total D - Total C = capitaux propres (C si D>C)

    total_d = sum(m for a, m, dc in lines if dc == TypeOperation.DEBIT)
    total_c = sum(m for a, m, dc in lines if dc == TypeOperation.CREDIT)

    # Si equity donné, on force l'équilibre avec 101 au passif
    if equity is not None:
        lines.append(("101", equity, TypeOperation.CREDIT))
    else:
        diff = total_d - total_c
        if diff > 0:
            lines.append(("101", diff, TypeOperation.CREDIT))
        elif diff < 0:
            lines.append(("101", -diff, TypeOperation.DEBIT))
    return lines


# Inutilisé pour l'instant


# def income_statement(bal: Dict[str, float]) -> Dict[str, float]:
#     """Construit un compte de résultat simple à partir des soldes.

#     Args:
#         bal: Dictionnaire `{compte: solde}` (Débit - Crédit) tel que renvoyé
#             par `Ledger.balance_accounts`.

#     Returns:
#         Un dictionnaire des principaux agrégats du compte de résultat.
#     """
#     ventes = -(bal.get("70", 0.0))  # 70 est créditor
#     cogs = bal.get("60", 0.0)
#     services = bal.get("61", 0.0)
#     payroll = bal.get("64", 0.0)
#     depreciation = bal.get("681", 0.0)
#     financial = bal.get("66", 0.0)

#     marge_brute = ventes - cogs
#     ebe_like = ventes - cogs - services - payroll
#     rex = ebe_like - depreciation
#     rca = rex - financial
#     res_net = rca  # pas d'IS ni exceptionnel dans cette V1

#     return {
#         "Chiffre d'affaires (70)": ventes,
#         "Achats consommés (60)": cogs,
#         "Services extérieurs (61)": services,
#         "Charges de personnel (64)": payroll,
#         "Dotations amort. (681)": depreciation,
#         "Charges financières (66)": financial,
#         "Marge brute": marge_brute,
#         "EBE (approx)": ebe_like,
#         "Résultat d'exploitation": rex,
#         "Résultat courant": rca,
#         "Résultat net": res_net,
#     }
