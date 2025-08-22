"""
Système de finance avancée pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from enum import Enum
from datetime import date, timedelta
import calendar


class AccountType(Enum):
    """Types de comptes comptables."""

    ASSET = "actif"
    LIABILITY = "passif"
    EQUITY = "capitaux_propres"
    REVENUE = "produits"
    EXPENSE = "charges"


class TransactionType(Enum):
    """Types de transactions."""

    SALE = "vente"
    PURCHASE = "achat"
    SALARY = "salaire"
    RENT = "loyer"
    MARKETING = "marketing"
    EQUIPMENT = "equipement"
    LOAN = "emprunt"
    INVESTMENT = "investissement"


@dataclass
class Account:
    """Compte comptable."""

    code: str
    name: str
    type: AccountType
    balance: Decimal = Decimal("0")
    parent_code: Optional[str] = None

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


@dataclass
class Transaction:
    """Transaction comptable avec écriture double."""

    id: str
    date: date
    description: str
    type: TransactionType
    debit_account: str
    credit_account: str
    amount: Decimal
    reference: Optional[str] = None

    def __post_init__(self) -> None:
        """Validation."""
        if self.amount <= 0:
            raise ValueError(f"Le montant doit être positif: {self.amount}")


@dataclass
class Budget:
    """Budget prévisionnel."""

    name: str
    period_start: date
    period_end: date
    revenue_forecast: Dict[str, Decimal] = field(default_factory=dict)
    expense_forecast: Dict[str, Decimal] = field(default_factory=dict)

    @property
    def total_revenue_forecast(self) -> Decimal:
        """Total des revenus prévisionnels."""
        return sum(self.revenue_forecast.values())

    @property
    def total_expense_forecast(self) -> Decimal:
        """Total des charges prévisionnelles."""
        return sum(self.expense_forecast.values())

    @property
    def profit_forecast(self) -> Decimal:
        """Résultat prévisionnel."""
        return self.total_revenue_forecast - self.total_expense_forecast


@dataclass
class RecipeProfitability:
    """Analyse de rentabilité par recette."""

    recipe_id: str
    recipe_name: str
    selling_price: Decimal
    ingredient_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    quantity_sold: int = 0

    @property
    def total_cost(self) -> Decimal:
        """Coût total unitaire."""
        return self.ingredient_cost + self.labor_cost + self.overhead_cost

    @property
    def unit_margin(self) -> Decimal:
        """Marge unitaire."""
        return self.selling_price - self.total_cost

    @property
    def margin_rate(self) -> Decimal:
        """Taux de marge."""
        if self.selling_price == 0:
            return Decimal("0")
        return self.unit_margin / self.selling_price

    @property
    def total_revenue(self) -> Decimal:
        """Chiffre d'affaires total."""
        return self.selling_price * Decimal(self.quantity_sold)

    @property
    def total_profit(self) -> Decimal:
        """Profit total."""
        return self.unit_margin * Decimal(self.quantity_sold)


class FinanceManager:
    """Gestionnaire de finance avancée."""

    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.transactions: List[Transaction] = []
        self.budgets: List[Budget] = []
        self.recipe_profitability: Dict[str, RecipeProfitability] = {}

        # Initialisation du plan comptable
        self._initialize_chart_of_accounts()

    def _initialize_chart_of_accounts(self) -> None:
        """Initialise le plan comptable restaurant."""
        accounts_data = [
            # ACTIFS
            ("101", "Capital", AccountType.EQUITY),
            ("161", "Emprunts", AccountType.LIABILITY),
            ("201", "Immobilisations", AccountType.ASSET),
            ("211", "Équipement cuisine", AccountType.ASSET, "201"),
            ("212", "Mobilier", AccountType.ASSET, "201"),
            ("213", "Matériel informatique", AccountType.ASSET, "201"),
            ("301", "Stocks matières premières", AccountType.ASSET),
            ("401", "Fournisseurs", AccountType.LIABILITY),
            ("411", "Clients", AccountType.ASSET),
            ("421", "Personnel - salaires", AccountType.LIABILITY),
            ("512", "Banque", AccountType.ASSET),
            ("530", "Caisse", AccountType.ASSET),
            # CHARGES
            ("601", "Achats matières premières", AccountType.EXPENSE),
            ("602", "Achats emballages", AccountType.EXPENSE),
            ("613", "Loyer", AccountType.EXPENSE),
            ("621", "Personnel", AccountType.EXPENSE),
            ("623", "Charges sociales", AccountType.EXPENSE),
            ("625", "Formation", AccountType.EXPENSE),
            ("626", "Assurances", AccountType.EXPENSE),
            ("627", "Entretien", AccountType.EXPENSE),
            ("628", "Marketing", AccountType.EXPENSE),
            ("661", "Charges financières", AccountType.EXPENSE),
            ("681", "Amortissements", AccountType.EXPENSE),
            # PRODUITS
            ("701", "Ventes restaurant", AccountType.REVENUE),
            ("702", "Ventes à emporter", AccountType.REVENUE),
            ("703", "Livraisons", AccountType.REVENUE),
            ("706", "Prestations services", AccountType.REVENUE),
            ("761", "Produits financiers", AccountType.REVENUE),
        ]

        for data in accounts_data:
            code, name, account_type = data[:3]
            parent_code = data[3] if len(data) > 3 else None

            self.accounts[code] = Account(
                code=code, name=name, type=account_type, parent_code=parent_code
            )

    def create_transaction(
        self,
        description: str,
        transaction_type: TransactionType,
        debit_account: str,
        credit_account: str,
        amount: Decimal,
        reference: str = None,
    ) -> Transaction:
        """
        Crée une transaction comptable.

        Args:
            description: Description de la transaction
            transaction_type: Type de transaction
            debit_account: Compte à débiter
            credit_account: Compte à créditer
            amount: Montant
            reference: Référence (optionnel)

        Returns:
            Transaction créée
        """
        if debit_account not in self.accounts:
            raise ValueError(f"Compte débiteur inexistant: {debit_account}")
        if credit_account not in self.accounts:
            raise ValueError(f"Compte créditeur inexistant: {credit_account}")

        transaction = Transaction(
            id=f"TXN{len(self.transactions) + 1:06d}",
            date=date.today(),
            description=description,
            type=transaction_type,
            debit_account=debit_account,
            credit_account=credit_account,
            amount=amount,
            reference=reference,
        )

        # Écriture comptable
        self.accounts[debit_account].debit(amount)
        self.accounts[credit_account].credit(amount)

        self.transactions.append(transaction)
        return transaction

    def record_sale(self, amount: Decimal, payment_method: str = "cash") -> Transaction:
        """Enregistre une vente."""
        credit_account = (
            "530" if payment_method == "cash" else "411"
        )  # Caisse ou Clients

        return self.create_transaction(
            description=f"Vente restaurant - {payment_method}",
            transaction_type=TransactionType.SALE,
            debit_account=credit_account,
            credit_account="701",
            amount=amount,
        )

    def record_purchase(
        self, amount: Decimal, supplier: str, category: str = "ingredients"
    ) -> Transaction:
        """Enregistre un achat."""
        expense_account = (
            "601" if category == "ingredients" else "602"
        )  # Matières premières ou emballages

        return self.create_transaction(
            description=f"Achat {category} - {supplier}",
            transaction_type=TransactionType.PURCHASE,
            debit_account=expense_account,
            credit_account="401",  # Fournisseurs
            amount=amount,
        )

    def record_salary_payment(self, amount: Decimal, employee_name: str) -> Transaction:
        """Enregistre un paiement de salaire."""
        return self.create_transaction(
            description=f"Salaire {employee_name}",
            transaction_type=TransactionType.SALARY,
            debit_account="621",  # Personnel
            credit_account="512",  # Banque
            amount=amount,
        )

    def record_marketing_expense(
        self, amount: Decimal, campaign_name: str
    ) -> Transaction:
        """Enregistre une dépense marketing."""
        return self.create_transaction(
            description=f"Marketing - {campaign_name}",
            transaction_type=TransactionType.MARKETING,
            debit_account="628",  # Marketing
            credit_account="512",  # Banque
            amount=amount,
        )

    def get_balance_sheet(self) -> Dict[str, Dict[str, Decimal]]:
        """Génère le bilan comptable."""
        assets = Decimal("0")
        liabilities = Decimal("0")
        equity = Decimal("0")

        asset_accounts = {}
        liability_accounts = {}
        equity_accounts = {}

        for account in self.accounts.values():
            if account.type == AccountType.ASSET:
                assets += account.balance
                asset_accounts[account.name] = account.balance
            elif account.type == AccountType.LIABILITY:
                liabilities += account.balance
                liability_accounts[account.name] = account.balance
            elif account.type == AccountType.EQUITY:
                equity += account.balance
                equity_accounts[account.name] = account.balance

        return {
            "assets": asset_accounts,
            "liabilities": liability_accounts,
            "equity": equity_accounts,
            "totals": {"assets": assets, "liabilities": liabilities, "equity": equity},
        }

    def get_income_statement(
        self, start_date: date = None, end_date: date = None
    ) -> Dict[str, any]:
        """Génère le compte de résultat."""
        if start_date is None:
            start_date = date.today().replace(day=1)  # Début du mois
        if end_date is None:
            end_date = date.today()

        revenues = Decimal("0")
        expenses = Decimal("0")

        revenue_accounts = {}
        expense_accounts = {}

        # Filtrer les transactions par période
        period_transactions = [
            t for t in self.transactions if start_date <= t.date <= end_date
        ]

        for account in self.accounts.values():
            if account.type == AccountType.REVENUE:
                # Calculer le solde pour la période
                period_balance = sum(
                    t.amount
                    for t in period_transactions
                    if t.credit_account == account.code
                ) - sum(
                    t.amount
                    for t in period_transactions
                    if t.debit_account == account.code
                )

                revenues += period_balance
                revenue_accounts[account.name] = period_balance

            elif account.type == AccountType.EXPENSE:
                period_balance = sum(
                    t.amount
                    for t in period_transactions
                    if t.debit_account == account.code
                ) - sum(
                    t.amount
                    for t in period_transactions
                    if t.credit_account == account.code
                )

                expenses += period_balance
                expense_accounts[account.name] = period_balance

        net_profit = revenues - expenses

        return {
            "period": {"start": start_date, "end": end_date},
            "revenues": revenue_accounts,
            "expenses": expense_accounts,
            "totals": {
                "revenues": revenues,
                "expenses": expenses,
                "net_profit": net_profit,
            },
            "margins": {
                "gross_margin": revenues
                - expense_accounts.get("Achats matières premières", Decimal("0")),
                "operating_margin": net_profit,
                "net_margin_rate": net_profit / revenues
                if revenues > 0
                else Decimal("0"),
            },
        }

    def create_budget(self, name: str, period_start: date, period_end: date) -> Budget:
        """Crée un budget prévisionnel."""
        budget = Budget(name=name, period_start=period_start, period_end=period_end)

        self.budgets.append(budget)
        return budget

    def update_recipe_profitability(
        self,
        recipe_id: str,
        recipe_name: str,
        selling_price: Decimal,
        ingredient_cost: Decimal,
        labor_cost: Decimal,
        overhead_cost: Decimal,
    ) -> None:
        """Met à jour l'analyse de rentabilité d'une recette."""
        self.recipe_profitability[recipe_id] = RecipeProfitability(
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            selling_price=selling_price,
            ingredient_cost=ingredient_cost,
            labor_cost=labor_cost,
            overhead_cost=overhead_cost,
        )

    def record_recipe_sale(self, recipe_id: str, quantity: int = 1) -> None:
        """Enregistre la vente d'une recette."""
        if recipe_id in self.recipe_profitability:
            self.recipe_profitability[recipe_id].quantity_sold += quantity

    def get_recipe_profitability_report(self) -> List[Dict[str, any]]:
        """Génère un rapport de rentabilité par recette."""
        report = []

        for recipe in self.recipe_profitability.values():
            report.append(
                {
                    "recipe_id": recipe.recipe_id,
                    "recipe_name": recipe.recipe_name,
                    "selling_price": recipe.selling_price,
                    "total_cost": recipe.total_cost,
                    "unit_margin": recipe.unit_margin,
                    "margin_rate": recipe.margin_rate,
                    "quantity_sold": recipe.quantity_sold,
                    "total_revenue": recipe.total_revenue,
                    "total_profit": recipe.total_profit,
                }
            )

        # Trier par profit total décroissant
        report.sort(key=lambda x: x["total_profit"], reverse=True)
        return report

    def get_cash_flow_forecast(self, days: int = 30) -> Dict[str, any]:
        """Prévision de trésorerie."""
        current_cash = self.accounts["512"].balance + self.accounts["530"].balance

        # Estimation basée sur l'historique récent
        recent_transactions = [
            t
            for t in self.transactions[-100:]  # 100 dernières transactions
        ]

        daily_inflows = (
            sum(t.amount for t in recent_transactions if t.type == TransactionType.SALE)
            / len(recent_transactions)
            if recent_transactions
            else Decimal("0")
        )

        daily_outflows = (
            sum(
                t.amount
                for t in recent_transactions
                if t.type in [TransactionType.PURCHASE, TransactionType.SALARY]
            )
            / len(recent_transactions)
            if recent_transactions
            else Decimal("0")
        )

        daily_net_flow = daily_inflows - daily_outflows

        forecast = []
        cash_position = current_cash

        for day in range(1, days + 1):
            cash_position += daily_net_flow
            forecast.append(
                {
                    "day": day,
                    "date": date.today() + timedelta(days=day),
                    "cash_position": cash_position,
                    "daily_flow": daily_net_flow,
                }
            )

        return {
            "current_cash": current_cash,
            "daily_inflows": daily_inflows,
            "daily_outflows": daily_outflows,
            "daily_net_flow": daily_net_flow,
            "forecast": forecast,
            "min_cash_position": min(f["cash_position"] for f in forecast),
            "max_cash_position": max(f["cash_position"] for f in forecast),
        }

    def get_financial_ratios(self) -> Dict[str, Decimal]:
        """Calcule les ratios financiers clés."""
        balance_sheet = self.get_balance_sheet()
        income_statement = self.get_income_statement()

        assets = balance_sheet["totals"]["assets"]
        liabilities = balance_sheet["totals"]["liabilities"]
        equity = balance_sheet["totals"]["equity"]
        revenues = income_statement["totals"]["revenues"]
        net_profit = income_statement["totals"]["net_profit"]

        ratios = {}

        # Ratios de liquidité
        ratios["current_ratio"] = (
            assets / liabilities if liabilities > 0 else Decimal("0")
        )

        # Ratios de rentabilité
        ratios["net_margin"] = net_profit / revenues if revenues > 0 else Decimal("0")
        ratios["roe"] = (
            net_profit / equity if equity > 0 else Decimal("0")
        )  # Return on Equity
        ratios["roa"] = (
            net_profit / assets if assets > 0 else Decimal("0")
        )  # Return on Assets

        # Ratios d'endettement
        ratios["debt_ratio"] = liabilities / assets if assets > 0 else Decimal("0")
        ratios["equity_ratio"] = equity / assets if assets > 0 else Decimal("0")

        return ratios
