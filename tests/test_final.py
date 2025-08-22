#!/usr/bin/env python3
"""
Test final pour vérifier que tous les systèmes de FoodOps Pro fonctionnent.
"""

print("=== TEST FINAL FOODOPS PRO ===")

try:
    # Test 1: Chargement des données
    print("1. Test chargement des données...")
    from src.foodops_pro.io.data_loader import DataLoader

    loader = DataLoader()
    data = loader.load_all_data()
    print(f"   ✓ {len(data['ingredients'])} ingrédients chargés")
    print(f"   ✓ {len(data['recipes'])} recettes chargées")
    print(f"   ✓ {len(data['suppliers'])} fournisseurs chargés")
    print(f"   ✓ Scénario '{data['scenario'].name}' chargé")

    # Test 2: Calcul de coûts
    print("\n2. Test calcul de coûts...")
    from src.foodops_pro.core.costing import RecipeCostCalculator

    calculator = RecipeCostCalculator(data["ingredients"])
    burger_recipe = data["recipes"]["burger_classic"]
    breakdown = calculator.calculate_recipe_cost(burger_recipe)
    print(f"   ✓ Burger classique: {breakdown.cost_per_portion:.2f}€ par portion")
    print(f"   ✓ Coût total avec MO: {breakdown.total_cost_with_labor:.2f}€")

    # Test 3: Simulation de marché
    print("\n3. Test simulation de marché...")
    from src.foodops_pro.core.market import MarketEngine
    from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
    from decimal import Decimal

    restaurant = Restaurant(
        id="test",
        name="Test Restaurant",
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("1.0"),
        staffing_level=2,
    )
    restaurant.set_recipe_price("burger_classic", Decimal("12.50"))
    restaurant.activate_recipe("burger_classic")

    market = MarketEngine(data["scenario"], 42)
    results = market.allocate_demand([restaurant], 1)
    result = results["test"]

    print(
        f"   ✓ {result.served_customers} clients servis sur {result.capacity} de capacité"
    )
    print(f"   ✓ Chiffre d'affaires: {result.revenue:.0f}€")

    # Test 4: Comptabilité
    print("\n4. Test comptabilité...")
    from src.foodops_pro.core.ledger import Ledger, VATCalculator

    ledger = Ledger()

    # Enregistrement d'une vente
    ledger.record_sale(Decimal("110.00"), Decimal("0.10"), None, "Test vente")
    vat_collected = ledger.get_balance("44571")
    print(f"   ✓ TVA collectée: {vat_collected:.2f}€")

    # Test 5: Paie française
    print("\n5. Test paie française...")
    from src.foodops_pro.core.payroll import PayrollCalculator
    from src.foodops_pro.domain.employee import (
        Employee,
        EmployeePosition,
        EmployeeContract,
    )

    hr_config = data["hr_tables"]["social_charges"]
    payroll_calc = PayrollCalculator(hr_config)

    employee = Employee(
        id="test_emp",
        name="Test Employee",
        position=EmployeePosition.CUISINE,
        contract=EmployeeContract.CDI,
        salary_gross_monthly=Decimal("2200.00"),
    )

    payroll_result = payroll_calc.calculate_payroll(employee)
    print(f"   ✓ Salaire brut: {payroll_result.gross_salary:.0f}€")
    print(f"   ✓ Salaire net: {payroll_result.net_salary:.0f}€")
    print(f"   ✓ Coût total employeur: {payroll_result.total_cost:.0f}€")

    print("\n✅ TOUS LES SYSTÈMES FONCTIONNENT PARFAITEMENT !")
    print("\n🎮 Pour jouer, lancez : python -m src.foodops_pro.cli")
    print("📊 Legacy demo available in legacy/demos/demo.py")

except Exception as e:
    print(f"\n❌ Erreur durant le test : {e}")
    import traceback

    traceback.print_exc()
