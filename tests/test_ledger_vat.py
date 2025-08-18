"""
Tests pour la comptabilité et la gestion de la TVA.
"""

import pytest
from decimal import Decimal
from datetime import date

from src.foodops_pro.core.ledger import (
    Ledger, AccountingEntry, VATCalculator, Account, AccountType
)


class TestVATCalculator:
    """Tests du calculateur de TVA."""
    
    def test_calculate_vat_amounts_basic(self):
        """Test de calcul de TVA de base."""
        amount_ht = Decimal("100.00")
        vat_rate = Decimal("0.20")  # 20%
        
        result = VATCalculator.calculate_vat_amounts(amount_ht, vat_rate)
        
        assert result['ht'] == Decimal("100.00")
        assert result['vat'] == Decimal("20.00")
        assert result['ttc'] == Decimal("120.00")
    
    def test_calculate_vat_amounts_reduced_rate(self):
        """Test avec taux réduit (restauration)."""
        amount_ht = Decimal("50.00")
        vat_rate = Decimal("0.10")  # 10%
        
        result = VATCalculator.calculate_vat_amounts(amount_ht, vat_rate)
        
        assert result['ht'] == Decimal("50.00")
        assert result['vat'] == Decimal("5.00")
        assert result['ttc'] == Decimal("55.00")
    
    def test_calculate_vat_amounts_super_reduced_rate(self):
        """Test avec taux super réduit (produits alimentaires)."""
        amount_ht = Decimal("200.00")
        vat_rate = Decimal("0.055")  # 5.5%
        
        result = VATCalculator.calculate_vat_amounts(amount_ht, vat_rate)
        
        assert result['ht'] == Decimal("200.00")
        assert result['vat'] == Decimal("11.00")
        assert result['ttc'] == Decimal("211.00")
    
    def test_extract_vat_from_ttc_basic(self):
        """Test d'extraction de TVA depuis un montant TTC."""
        amount_ttc = Decimal("120.00")
        vat_rate = Decimal("0.20")
        
        result = VATCalculator.extract_vat_from_ttc(amount_ttc, vat_rate)
        
        assert abs(result['ht'] - Decimal("100.00")) < Decimal("0.01")
        assert abs(result['vat'] - Decimal("20.00")) < Decimal("0.01")
        assert result['ttc'] == Decimal("120.00")
    
    def test_extract_vat_from_ttc_reduced_rate(self):
        """Test d'extraction avec taux réduit."""
        amount_ttc = Decimal("110.00")
        vat_rate = Decimal("0.10")
        
        result = VATCalculator.extract_vat_from_ttc(amount_ttc, vat_rate)
        
        expected_ht = Decimal("110.00") / Decimal("1.10")
        expected_vat = Decimal("110.00") - expected_ht
        
        assert abs(result['ht'] - expected_ht) < Decimal("0.01")
        assert abs(result['vat'] - expected_vat) < Decimal("0.01")
        assert result['ttc'] == Decimal("110.00")
    
    def test_vat_calculation_precision(self):
        """Test de précision des calculs de TVA."""
        # Montant avec beaucoup de décimales
        amount_ht = Decimal("123.456789")
        vat_rate = Decimal("0.196")  # Taux inhabituel
        
        result = VATCalculator.calculate_vat_amounts(amount_ht, vat_rate)
        
        # Vérification de la cohérence
        assert result['ht'] + result['vat'] == result['ttc']
        assert result['vat'] == amount_ht * vat_rate


class TestAccount:
    """Tests de la classe Account."""
    
    def test_account_creation(self):
        """Test de création d'un compte."""
        account = Account(
            number="701",
            name="Ventes de marchandises",
            type=AccountType.REVENUE
        )
        
        assert account.number == "701"
        assert account.name == "Ventes de marchandises"
        assert account.type == AccountType.REVENUE
        assert account.balance == Decimal("0")
    
    def test_account_debit_asset(self):
        """Test de débit d'un compte d'actif."""
        account = Account("512", "Banque", AccountType.ASSET)
        
        account.debit(Decimal("1000"))
        assert account.balance == Decimal("1000")
        
        account.debit(Decimal("500"))
        assert account.balance == Decimal("1500")
    
    def test_account_credit_asset(self):
        """Test de crédit d'un compte d'actif."""
        account = Account("512", "Banque", AccountType.ASSET)
        account.balance = Decimal("1000")
        
        account.credit(Decimal("300"))
        assert account.balance == Decimal("700")
    
    def test_account_debit_liability(self):
        """Test de débit d'un compte de passif."""
        account = Account("401", "Fournisseurs", AccountType.LIABILITY)
        account.balance = Decimal("500")  # Solde créditeur
        
        account.debit(Decimal("200"))
        assert account.balance == Decimal("300")
    
    def test_account_credit_liability(self):
        """Test de crédit d'un compte de passif."""
        account = Account("401", "Fournisseurs", AccountType.LIABILITY)
        
        account.credit(Decimal("800"))
        assert account.balance == Decimal("800")
    
    def test_account_revenue_operations(self):
        """Test des opérations sur un compte de produits."""
        account = Account("701", "Ventes", AccountType.REVENUE)
        
        # Les produits augmentent au crédit
        account.credit(Decimal("1000"))
        assert account.balance == Decimal("1000")
        
        # Diminuent au débit
        account.debit(Decimal("100"))
        assert account.balance == Decimal("900")
    
    def test_account_expense_operations(self):
        """Test des opérations sur un compte de charges."""
        account = Account("601", "Achats", AccountType.EXPENSE)
        
        # Les charges augmentent au débit
        account.debit(Decimal("500"))
        assert account.balance == Decimal("500")
        
        # Diminuent au crédit
        account.credit(Decimal("50"))
        assert account.balance == Decimal("450")


class TestAccountingEntry:
    """Tests de la classe AccountingEntry."""
    
    def test_entry_creation_valid(self):
        """Test de création d'une écriture valide."""
        entry = AccountingEntry(
            date=date.today(),
            description="Test entry",
            debit_account="512",
            credit_account="701",
            amount=Decimal("100.00"),
            reference="TEST001"
        )
        
        assert entry.date == date.today()
        assert entry.description == "Test entry"
        assert entry.debit_account == "512"
        assert entry.credit_account == "701"
        assert entry.amount == Decimal("100.00")
        assert entry.reference == "TEST001"
    
    def test_entry_creation_invalid_amount(self):
        """Test de création avec montant invalide."""
        with pytest.raises(ValueError, match="Le montant doit être positif"):
            AccountingEntry(
                date=date.today(),
                description="Invalid entry",
                debit_account="512",
                credit_account="701",
                amount=Decimal("-100.00")
            )
    
    def test_entry_creation_same_accounts(self):
        """Test de création avec comptes identiques."""
        with pytest.raises(ValueError, match="Les comptes débit et crédit doivent être différents"):
            AccountingEntry(
                date=date.today(),
                description="Same accounts",
                debit_account="512",
                credit_account="512",
                amount=Decimal("100.00")
            )
    
    def test_entry_creation_empty_accounts(self):
        """Test de création avec comptes vides."""
        with pytest.raises(ValueError, match="Les comptes débit et crédit sont obligatoires"):
            AccountingEntry(
                date=date.today(),
                description="Empty accounts",
                debit_account="",
                credit_account="701",
                amount=Decimal("100.00")
            )


class TestLedger:
    """Tests de la classe Ledger."""
    
    def test_ledger_initialization(self):
        """Test de l'initialisation du grand livre."""
        ledger = Ledger()
        
        # Vérification de la présence des comptes principaux
        assert "512" in ledger.accounts  # Banque
        assert "701" in ledger.accounts  # Ventes
        assert "601" in ledger.accounts  # Achats
        assert "44566" in ledger.accounts  # TVA déductible
        assert "44571" in ledger.accounts  # TVA collectée
        
        # Vérification des soldes initiaux
        for account in ledger.accounts.values():
            assert account.balance == Decimal("0")
    
    def test_add_entry_valid(self):
        """Test d'ajout d'une écriture valide."""
        ledger = Ledger()
        
        entry = AccountingEntry(
            date=date.today(),
            description="Test sale",
            debit_account="512",  # Banque
            credit_account="701",  # Ventes
            amount=Decimal("1000.00")
        )
        
        ledger.add_entry(entry)
        
        # Vérification de l'enregistrement
        assert len(ledger.entries) == 1
        assert ledger.entries[0] == entry
        
        # Vérification des soldes
        assert ledger.get_balance("512") == Decimal("1000.00")
        assert ledger.get_balance("701") == Decimal("1000.00")
    
    def test_add_entry_invalid_account(self):
        """Test d'ajout avec compte inexistant."""
        ledger = Ledger()
        
        entry = AccountingEntry(
            date=date.today(),
            description="Invalid account",
            debit_account="999",  # Compte inexistant
            credit_account="701",
            amount=Decimal("100.00")
        )
        
        with pytest.raises(ValueError, match="Compte débit inexistant"):
            ledger.add_entry(entry)
    
    def test_record_sale_basic(self):
        """Test d'enregistrement d'une vente de base."""
        ledger = Ledger()
        
        amount_ttc = Decimal("110.00")
        vat_rate = Decimal("0.10")
        sale_date = date.today()
        
        ledger.record_sale(amount_ttc, vat_rate, sale_date, "Vente restaurant")
        
        # Vérification des écritures
        assert len(ledger.entries) == 2  # Une pour le HT, une pour la TVA
        
        # Vérification des soldes
        expected_ht = Decimal("100.00")
        expected_vat = Decimal("10.00")
        
        assert abs(ledger.get_balance("411") - amount_ttc) < Decimal("0.01")  # Clients
        assert abs(ledger.get_balance("706") - expected_ht) < Decimal("0.01")  # Prestations
        assert abs(ledger.get_balance("44571") - expected_vat) < Decimal("0.01")  # TVA collectée
    
    def test_record_sale_no_vat(self):
        """Test d'enregistrement d'une vente sans TVA."""
        ledger = Ledger()
        
        amount_ttc = Decimal("100.00")
        vat_rate = Decimal("0.00")
        sale_date = date.today()
        
        ledger.record_sale(amount_ttc, vat_rate, sale_date, "Vente sans TVA")
        
        # Vérification qu'il n'y a qu'une écriture (pas de TVA)
        assert len(ledger.entries) == 1
        
        # Vérification des soldes
        assert ledger.get_balance("411") == Decimal("100.00")
        assert ledger.get_balance("706") == Decimal("100.00")
        assert ledger.get_balance("44571") == Decimal("0.00")
    
    def test_record_purchase_basic(self):
        """Test d'enregistrement d'un achat de base."""
        ledger = Ledger()
        
        amount_ht = Decimal("100.00")
        vat_rate = Decimal("0.055")  # 5.5%
        purchase_date = date.today()
        
        ledger.record_purchase(amount_ht, vat_rate, purchase_date, "Achat ingrédients")
        
        # Vérification des écritures
        assert len(ledger.entries) == 2
        
        # Vérification des soldes
        expected_vat = Decimal("5.50")
        expected_ttc = amount_ht + expected_vat
        
        assert ledger.get_balance("601") == amount_ht  # Achats
        assert abs(ledger.get_balance("44566") - expected_vat) < Decimal("0.01")  # TVA déductible
        assert abs(ledger.get_balance("401") - expected_ttc) < Decimal("0.01")  # Fournisseurs
    
    def test_record_payroll(self):
        """Test d'enregistrement d'une paie."""
        ledger = Ledger()
        
        gross_salary = Decimal("2500.00")
        social_charges = Decimal("1050.00")
        payroll_date = date.today()
        
        ledger.record_payroll(gross_salary, social_charges, payroll_date, "Paie janvier")
        
        # Vérification des écritures
        assert len(ledger.entries) == 2
        
        # Vérification des soldes
        assert ledger.get_balance("641") == gross_salary  # Rémunérations
        assert ledger.get_balance("645") == social_charges  # Charges sociales
        assert ledger.get_balance("421") == gross_salary  # Personnel - dettes
        assert ledger.get_balance("431") == social_charges  # Sécurité sociale
    
    def test_record_cash_payment(self):
        """Test d'enregistrement d'un paiement en espèces."""
        ledger = Ledger()
        
        # Initialisation de la caisse
        ledger.accounts["530"].balance = Decimal("1000.00")
        
        amount = Decimal("150.00")
        payment_date = date.today()
        
        ledger.record_cash_payment(amount, "613", payment_date, "Paiement loyer")
        
        # Vérification de l'écriture
        assert len(ledger.entries) == 1
        
        # Vérification des soldes
        assert ledger.get_balance("613") == amount  # Loyers
        assert ledger.get_balance("530") == Decimal("850.00")  # Caisse diminuée
    
    def test_get_trial_balance(self):
        """Test de génération de la balance comptable."""
        ledger = Ledger()
        
        # Quelques écritures
        ledger.record_sale(Decimal("110.00"), Decimal("0.10"), date.today(), "Vente 1")
        ledger.record_purchase(Decimal("50.00"), Decimal("0.055"), date.today(), "Achat 1")
        
        balance = ledger.get_trial_balance()
        
        # Vérification de la structure
        assert isinstance(balance, dict)
        
        # Vérification que les comptes avec solde sont présents
        assert "411" in balance  # Clients
        assert "706" in balance  # Prestations
        assert "44571" in balance  # TVA collectée
        assert "601" in balance  # Achats
        assert "44566" in balance  # TVA déductible
        assert "401" in balance  # Fournisseurs
        
        # Vérification de la structure des données
        for account_num, account_data in balance.items():
            assert 'name' in account_data
            assert 'debit' in account_data
            assert 'credit' in account_data
            assert account_data['debit'] >= Decimal("0")
            assert account_data['credit'] >= Decimal("0")
    
    def test_get_profit_loss(self):
        """Test de génération du compte de résultat."""
        ledger = Ledger()
        
        # Enregistrement de ventes et d'achats
        ledger.record_sale(Decimal("1100.00"), Decimal("0.10"), date.today(), "Ventes")
        ledger.record_purchase(Decimal("400.00"), Decimal("0.055"), date.today(), "Achats")
        ledger.record_payroll(Decimal("2000.00"), Decimal("840.00"), date.today(), "Paie")
        
        pnl = ledger.get_profit_loss()
        
        # Vérification de la structure
        assert 'revenues' in pnl
        assert 'expenses' in pnl
        assert 'profit' in pnl
        
        # Vérification des montants
        assert pnl['revenues'] == Decimal("1000.00")  # Ventes HT
        expected_expenses = Decimal("400.00") + Decimal("2000.00") + Decimal("840.00")  # Achats + salaires + charges
        assert pnl['expenses'] == expected_expenses
        assert pnl['profit'] == pnl['revenues'] - pnl['expenses']
    
    def test_multiple_operations_consistency(self):
        """Test de cohérence avec plusieurs opérations."""
        ledger = Ledger()
        
        # Série d'opérations
        operations = [
            ("sale", Decimal("220.00"), Decimal("0.10")),
            ("purchase", Decimal("80.00"), Decimal("0.055")),
            ("sale", Decimal("165.00"), Decimal("0.10")),
            ("payroll", Decimal("1500.00"), Decimal("630.00")),
            ("purchase", Decimal("120.00"), Decimal("0.055"))
        ]
        
        for op_type, amount1, amount2 in operations:
            if op_type == "sale":
                ledger.record_sale(amount1, amount2, date.today())
            elif op_type == "purchase":
                ledger.record_purchase(amount1, amount2, date.today())
            elif op_type == "payroll":
                ledger.record_payroll(amount1, amount2, date.today())
        
        # Vérification de l'équilibre comptable
        balance = ledger.get_trial_balance()
        
        total_debit = sum(account['debit'] for account in balance.values())
        total_credit = sum(account['credit'] for account in balance.values())
        
        # L'équilibre comptable doit être respecté
        assert abs(total_debit - total_credit) < Decimal("0.01")
    
    def test_vat_balance_calculation(self):
        """Test du calcul de la balance TVA."""
        ledger = Ledger()
        
        # Ventes avec TVA collectée
        ledger.record_sale(Decimal("1100.00"), Decimal("0.10"), date.today())
        ledger.record_sale(Decimal("550.00"), Decimal("0.10"), date.today())
        
        # Achats avec TVA déductible
        ledger.record_purchase(Decimal("200.00"), Decimal("0.055"), date.today())
        ledger.record_purchase(Decimal("300.00"), Decimal("0.20"), date.today())
        
        # Calcul de la balance TVA
        vat_collected = ledger.get_balance("44571")
        vat_deductible = ledger.get_balance("44566")
        vat_balance = vat_collected - vat_deductible
        
        # Vérifications
        expected_collected = Decimal("100.00") + Decimal("50.00")  # 150€
        expected_deductible = Decimal("11.00") + Decimal("60.00")  # 71€
        expected_balance = expected_collected - expected_deductible  # 79€
        
        assert abs(vat_collected - expected_collected) < Decimal("0.01")
        assert abs(vat_deductible - expected_deductible) < Decimal("0.01")
        assert abs(vat_balance - expected_balance) < Decimal("0.01")
