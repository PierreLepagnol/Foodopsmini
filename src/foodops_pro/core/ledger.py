"""
Système comptable français (PCG simplifié) pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional
from decimal import Decimal
from enum import Enum


class AccountType(Enum):
    """Types de comptes selon le PCG."""

    ASSET = "asset"  # Actif (classe 2)
    LIABILITY = "liability"  # Passif (classe 4)
    EQUITY = "equity"  # Capitaux propres (classe 1)
    REVENUE = "revenue"  # Produits (classe 7)
    EXPENSE = "expense"  # Charges (classe 6)


@dataclass
class AccountingEntry:
    """
    Écriture comptable avec débit et crédit.

    Attributes:
        date: Date de l'écriture
        description: Libellé de l'opération
        debit_account: Compte débité
        credit_account: Compte crédité
        amount: Montant de l'écriture
        reference: Référence de la pièce comptable
    """

    date: date
    description: str
    debit_account: str
    credit_account: str
    amount: Decimal
    reference: str = ""

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.amount <= 0:
            raise ValueError(f"Le montant doit être positif: {self.amount}")
        if not self.debit_account or not self.credit_account:
            raise ValueError("Les comptes débit et crédit sont obligatoires")
        if self.debit_account == self.credit_account:
            raise ValueError("Les comptes débit et crédit doivent être différents")


class VATCalculator:
    """Calculateur de TVA selon la réglementation française."""

    @staticmethod
    def calculate_vat_amounts(
        amount_ht: Decimal, vat_rate: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calcule les montants HT, TVA et TTC.

        Args:
            amount_ht: Montant hors taxes
            vat_rate: Taux de TVA (ex: 0.10 pour 10%)

        Returns:
            Dict avec 'ht', 'vat', 'ttc'
        """
        vat_amount = amount_ht * vat_rate
        amount_ttc = amount_ht + vat_amount

        return {"ht": amount_ht, "vat": vat_amount, "ttc": amount_ttc}

    @staticmethod
    def extract_vat_from_ttc(
        amount_ttc: Decimal, vat_rate: Decimal
    ) -> Dict[str, Decimal]:
        """
        Extrait la TVA d'un montant TTC.

        Args:
            amount_ttc: Montant toutes taxes comprises
            vat_rate: Taux de TVA

        Returns:
            Dict avec 'ht', 'vat', 'ttc'
        """
        amount_ht = amount_ttc / (1 + vat_rate)
        vat_amount = amount_ttc - amount_ht

        return {"ht": amount_ht, "vat": vat_amount, "ttc": amount_ttc}


@dataclass
class Account:
    """
    Compte comptable avec son solde.

    Attributes:
        number: Numéro de compte
        name: Nom du compte
        type: Type de compte
        balance: Solde actuel
    """

    number: str
    name: str
    type: AccountType
    balance: Decimal = Decimal("0")

    def debit(self, amount: Decimal) -> None:
        """Débite le compte."""
        if self.type in [AccountType.ASSET, AccountType.EXPENSE]:
            self.balance += amount
        else:
            self.balance -= amount

    def credit(self, amount: Decimal) -> None:
        """Crédite le compte."""
        if self.type in [AccountType.ASSET, AccountType.EXPENSE]:
            self.balance -= amount
        else:
            self.balance += amount


class Ledger:
    """
    Grand livre comptable simplifié pour FoodOps Pro.

    Implémente les comptes principaux selon le PCG français.
    """

    def __init__(self) -> None:
        self.accounts: Dict[str, Account] = {}
        self.entries: List[AccountingEntry] = []
        self._initialize_chart_of_accounts()

    def _initialize_chart_of_accounts(self) -> None:
        """Initialise le plan comptable de base."""
        # Comptes d'actif (classe 2)
        self.accounts["215"] = Account(
            "215", "Installations techniques", AccountType.ASSET
        )
        self.accounts["281"] = Account(
            "281", "Amortissements installations", AccountType.ASSET
        )

        # Comptes de trésorerie (classe 5)
        self.accounts["512"] = Account("512", "Banque", AccountType.ASSET)
        self.accounts["530"] = Account("530", "Caisse", AccountType.ASSET)

        # Comptes de tiers (classe 4)
        self.accounts["401"] = Account("401", "Fournisseurs", AccountType.LIABILITY)
        self.accounts["411"] = Account("411", "Clients", AccountType.LIABILITY)
        self.accounts["421"] = Account(
            "421", "Personnel - Rémunérations dues", AccountType.LIABILITY
        )
        self.accounts["431"] = Account("431", "Sécurité sociale", AccountType.LIABILITY)
        self.accounts["44566"] = Account("44566", "TVA déductible", AccountType.ASSET)
        self.accounts["44571"] = Account(
            "44571", "TVA collectée", AccountType.LIABILITY
        )

        # Comptes de charges (classe 6)
        self.accounts["601"] = Account(
            "601", "Achats matières premières", AccountType.EXPENSE
        )
        self.accounts["613"] = Account("613", "Loyers", AccountType.EXPENSE)
        self.accounts["621"] = Account(
            "621", "Personnel extérieur", AccountType.EXPENSE
        )
        self.accounts["641"] = Account(
            "641", "Rémunérations du personnel", AccountType.EXPENSE
        )
        self.accounts["645"] = Account(
            "645", "Charges de sécurité sociale", AccountType.EXPENSE
        )
        self.accounts["681"] = Account(
            "681", "Dotations aux amortissements", AccountType.EXPENSE
        )

        # Comptes de produits (classe 7)
        self.accounts["701"] = Account(
            "701", "Ventes de marchandises", AccountType.REVENUE
        )
        self.accounts["706"] = Account(
            "706", "Prestations de services", AccountType.REVENUE
        )

    def add_entry(self, entry: AccountingEntry) -> None:
        """
        Ajoute une écriture comptable.

        Args:
            entry: Écriture à ajouter

        Raises:
            ValueError: Si les comptes n'existent pas
        """
        if entry.debit_account not in self.accounts:
            raise ValueError(f"Compte débit inexistant: {entry.debit_account}")
        if entry.credit_account not in self.accounts:
            raise ValueError(f"Compte crédit inexistant: {entry.credit_account}")

        # Enregistrement de l'écriture
        self.entries.append(entry)

        # Mise à jour des soldes
        self.accounts[entry.debit_account].debit(entry.amount)
        self.accounts[entry.credit_account].credit(entry.amount)

    def record_sale(
        self,
        amount_ttc: Decimal,
        vat_rate: Decimal,
        sale_date: date,
        description: str = "Vente",
    ) -> None:
        """
        Enregistre une vente avec TVA.

        Args:
            amount_ttc: Montant TTC de la vente
            vat_rate: Taux de TVA
            sale_date: Date de la vente
            description: Description de la vente
        """
        vat_calc = VATCalculator.extract_vat_from_ttc(amount_ttc, vat_rate)

        # Débit client, crédit vente HT
        self.add_entry(
            AccountingEntry(
                date=sale_date,
                description=f"{description} HT",
                debit_account="411",  # Clients
                credit_account="706",  # Prestations de services
                amount=vat_calc["ht"],
            )
        )

        # Débit client, crédit TVA collectée
        if vat_calc["vat"] > 0:
            self.add_entry(
                AccountingEntry(
                    date=sale_date,
                    description=f"{description} TVA",
                    debit_account="411",  # Clients
                    credit_account="44571",  # TVA collectée
                    amount=vat_calc["vat"],
                )
            )

    def record_purchase(
        self,
        amount_ht: Decimal,
        vat_rate: Decimal,
        purchase_date: date,
        description: str = "Achat",
    ) -> None:
        """
        Enregistre un achat avec TVA déductible.

        Args:
            amount_ht: Montant HT de l'achat
            vat_rate: Taux de TVA
            purchase_date: Date de l'achat
            description: Description de l'achat
        """
        vat_calc = VATCalculator.calculate_vat_amounts(amount_ht, vat_rate)

        # Débit achat, crédit fournisseur HT
        self.add_entry(
            AccountingEntry(
                date=purchase_date,
                description=f"{description} HT",
                debit_account="601",  # Achats matières premières
                credit_account="401",  # Fournisseurs
                amount=vat_calc["ht"],
            )
        )

        # Débit TVA déductible, crédit fournisseur TVA
        if vat_calc["vat"] > 0:
            self.add_entry(
                AccountingEntry(
                    date=purchase_date,
                    description=f"{description} TVA",
                    debit_account="44566",  # TVA déductible
                    credit_account="401",  # Fournisseurs
                    amount=vat_calc["vat"],
                )
            )

    def record_payroll(
        self,
        gross_salary: Decimal,
        social_charges: Decimal,
        payroll_date: date,
        description: str = "Paie",
    ) -> None:
        """
        Enregistre une paie avec charges sociales.

        Args:
            gross_salary: Salaire brut
            social_charges: Charges sociales patronales
            payroll_date: Date de la paie
            description: Description
        """
        # Débit charges de personnel, crédit personnel
        self.add_entry(
            AccountingEntry(
                date=payroll_date,
                description=f"{description} - Salaire brut",
                debit_account="641",  # Rémunérations du personnel
                credit_account="421",  # Personnel - Rémunérations dues
                amount=gross_salary,
            )
        )

        # Débit charges sociales, crédit sécurité sociale
        self.add_entry(
            AccountingEntry(
                date=payroll_date,
                description=f"{description} - Charges sociales",
                debit_account="645",  # Charges de sécurité sociale
                credit_account="431",  # Sécurité sociale
                amount=social_charges,
            )
        )

    def record_cash_payment(
        self,
        amount: Decimal,
        expense_account: str,
        payment_date: date,
        description: str,
    ) -> None:
        """
        Enregistre un paiement en espèces.

        Args:
            amount: Montant du paiement
            expense_account: Compte de charge
            payment_date: Date du paiement
            description: Description
        """
        self.add_entry(
            AccountingEntry(
                date=payment_date,
                description=description,
                debit_account=expense_account,
                credit_account="530",  # Caisse
                amount=amount,
            )
        )

    def get_balance(self, account_number: str) -> Decimal:
        """Retourne le solde d'un compte."""
        return self.accounts.get(
            account_number, Account("", "", AccountType.ASSET)
        ).balance

    def get_trial_balance(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Génère la balance comptable.

        Returns:
            Dict avec les soldes débiteurs et créditeurs
        """
        balance = {}
        for account_num, account in self.accounts.items():
            if account.balance != 0:
                balance[account_num] = {
                    "name": account.name,
                    "debit": account.balance if account.balance > 0 else Decimal("0"),
                    "credit": -account.balance if account.balance < 0 else Decimal("0"),
                }
        return balance

    def get_profit_loss(self) -> Dict[str, Decimal]:
        """
        Génère le compte de résultat simplifié.

        Returns:
            Dict avec produits, charges et résultat
        """
        revenues = Decimal("0")
        expenses = Decimal("0")

        for account in self.accounts.values():
            if account.type == AccountType.REVENUE:
                revenues += abs(account.balance)
            elif account.type == AccountType.EXPENSE:
                expenses += account.balance

        return {
            "revenues": revenues,
            "expenses": expenses,
            "profit": revenues - expenses,
        }
