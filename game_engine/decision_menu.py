"""
Menu de décisions enrichi
"""

from decimal import Decimal

# from game_engine.financial_reports import FinancialReports
from game_engine.console_ui import (
    ask_float,
    ask_int,
    clear_screen,
    confirm,
    get_input,
    pause,
    print_box,
    show_error,
    show_info,
    show_menu,
    show_success,
)
from game_engine.domain.finance.ledger import Ledger
from game_engine.domain.market.random_events import RandomEventManager
from game_engine.domain.stock.procurement import POLine, ProcurementPlanner
from game_engine.domain.menu.recipe_costing import RecipeCostCalculator
from game_engine.domain.restaurant import Restaurant
from game_engine.domain.staff.employee import EmployeeContract, EmployeePosition
from game_engine.domain.stock import StockManager
from game_engine.financial_reports import FinancialReports
from game_engine.utils import MenuHandler


class DecisionMenu:
    """Menu de décisions stratégiques pour les joueurs."""

    def __init__(self, cost_calculator: RecipeCostCalculator):
        self.cost_calculator = cost_calculator
        self.financial_reports = FinancialReports()
        # Catalogues et paramètres (injectés depuis le jeu/CLI)
        self._suppliers_catalog: dict[str, list[dict]] = {}
        self._available_recipes_cache: dict[str, any] = {}
        self._admin_settings = None

    def set_suppliers_catalog(self, suppliers_catalog: dict[str, list[dict]]):
        """Injection de la mercuriale (offres par ingrédient)."""
        self._suppliers_catalog = suppliers_catalog or {}

    def set_admin_settings(self, settings):
        """Injection des paramètres admin (auto_* et confirmations)."""
        self._admin_settings = settings

    def cache_available_recipes(self, recipes: dict[str, any]) -> None:
        self._available_recipes_cache = recipes or {}

    def show_decision_menu(
        self, restaurant: Restaurant, turn: int, available_recipes: dict
    ) -> dict[str, any]:
        """
        Affiche le menu de décisions principal et retourne les choix du joueur.

        Returns:
            Dict contenant toutes les décisions prises
        """
        decisions = {}

        while True:
            clear_screen()
            self._show_restaurant_status(restaurant, turn)

            menu = MenuHandler(f"DÉCISIONS - TOUR {turn} - {restaurant.name}")
            menu.add_option(
                "📋 Menu & Pricing",
                lambda: self._menu_pricing_decisions(
                    restaurant, available_recipes, decisions
                ),
            ).add_option(
                "👥 Ressources Humaines",
                lambda: self._hr_decisions(restaurant, decisions),
            ).add_option(
                "🛒 Achats & Stocks",
                lambda: self._purchasing_decisions(restaurant),
            ).add_option(
                "📈 Marketing & Commercial",
                lambda: self._marketing_decisions(restaurant, decisions),
            ).add_option(
                "📊 Rapports & Analyses", lambda: self._show_reports(restaurant)
            ).add_option(
                "✅ Valider et passer au tour suivant",
                lambda: "validate_and_exit"
                if self._validate_decisions(restaurant, decisions)
                else None,
            )
            # .add_option(
            #     "🏗️ Investissements",
            #     lambda: self._investment_decisions(restaurant, decisions),
            # )
            # .add_option(
            #     "💰 Finance & Comptabilité",
            #     lambda: self._financial_decisions(restaurant, decisions),
            # )
            result = menu.show()
            if result == "validate_and_exit":
                break

        return decisions

    def _can_validate_decisions(self, restaurant: Restaurant, decisions: dict) -> bool:
        """Check if decisions can be validated (add any validation logic here)."""
        # For now, always allow validation, but this can be extended with business rules
        return True

    def _show_restaurant_status(self, restaurant: Restaurant, turn: int) -> None:
        """Affiche le statut actuel du restaurant."""
        status = [
            f"🏪 {restaurant.name} ({restaurant.type.value.title()})",
            f"💰 Trésorerie: {restaurant.cash:,.0f}€",
            f"👥 Employés: {len(restaurant.employees)}",
            f"🍽️ Capacité: {restaurant.capacity_current} couverts",
            f"📊 Niveau staffing: {restaurant.staffing_level}/3",
            f"🍴 Recettes actives: {len(restaurant.get_active_menu())}",
        ]

        # Couleur selon la santé financière
        if restaurant.cash > 20000:
            style = "success"
        elif restaurant.cash > 5000:
            style = "warning"
        else:
            style = "error"

        print_box(status, f"STATUT - TOUR {turn}", style)

    # Usage:
    def _menu_pricing_decisions(
        self, restaurant: Restaurant, available_recipes: dict, decisions: dict
    ) -> None:
        """Gestion du menu et des prix."""

        menu = MenuHandler("MENU & PRICING")
        menu.add_option(
            "💰 Modifier les prix", lambda: self._modify_prices(restaurant, decisions)
        ).add_option(
            "➕ Ajouter des plats au menu",
            lambda: self._add_recipes(restaurant, available_recipes, decisions),
        ).add_option(
            "➖ Retirer des plats du menu",
            lambda: self._remove_recipes(restaurant, decisions),
        ).add_option(
            "📊 Analyser la rentabilité par plat",
            lambda: self._analyze_recipe_profitability(restaurant, available_recipes),
        ).add_option(
            "🍽️ Créer un menu du jour",
            lambda: self._create_daily_menu(restaurant, decisions),
        ).add_option(
            "📈 Voir l'historique des ventes",
            lambda: self._show_sales_history(restaurant),
        )

        menu.show()

    def _modify_prices(self, restaurant: Restaurant, decisions: dict) -> None:
        """Modification des prix de vente."""
        active_menu = restaurant.get_active_menu()

        if not active_menu:
            show_error("Aucune recette active dans le menu.")
            pause()
            return

        clear_screen()

        # Affichage du menu actuel avec analyse
        menu_analysis = ["MENU ACTUEL ET RENTABILITÉ:"]

        for recipe_id, current_price in active_menu.items():
            if recipe_id in self.cost_calculator.ingredients:  # Vérification simplifiée
                # Calcul du coût (simplifié pour la démo)
                estimated_cost = current_price * Decimal(
                    "0.35"
                )  # 35% de food cost estimé
                margin = current_price - estimated_cost
                margin_pct = (margin / current_price * 100) if current_price > 0 else 0

                menu_analysis.append(
                    f"• {recipe_id}: {current_price:.2f}€ "
                    f"(coût ~{estimated_cost:.2f}€, marge {margin_pct:.1f}%)"
                )

        print_box(menu_analysis, style="info")

        # Sélection de la recette à modifier
        recipe_list = list(active_menu.keys())
        recipe_choice = show_menu(
            "Quelle recette modifier ?",
            [
                f"{recipe_id} - {active_menu[recipe_id]:.2f}€"
                for recipe_id in recipe_list
            ],
        )

        if recipe_choice == 0:
            return

        selected_recipe = recipe_list[recipe_choice - 1]
        current_price = active_menu[selected_recipe]

        # Saisie du nouveau prix
        new_price = get_input(
            f"Nouveau prix pour {selected_recipe}",
            Decimal,
            min_val=Decimal("1.0"),
            max_val=Decimal("100.0"),
            default=current_price,
        )

        if new_price and new_price != current_price:
            if "price_changes" not in decisions:
                decisions["price_changes"] = {}
            decisions["price_changes"][selected_recipe] = new_price

            # Calcul de l'impact
            change_pct = (new_price - current_price) / current_price * 100
            impact_msg = f"Prix modifié: {current_price:.2f}€ → {new_price:.2f}€ ({change_pct:+.1f}%)"

            if abs(change_pct) > 10:
                impact_msg += (
                    "\n⚠️ Changement important - Impact sur la clientèle attendu"
                )

            show_success(impact_msg)
            pause()

    def _hr_decisions(self, restaurant: Restaurant, decisions: dict) -> None:
        """Gestion des ressources humaines."""
        while True:
            clear_screen()

            restaurant.display_team_info()

            menu = (
                MenuHandler("RESSOURCES HUMAINES")
                .add_option(
                    "👤 Recruter un employé",
                    lambda: self._recruit_employee(restaurant, decisions),
                )
                .add_option(
                    "❌ Licencier un employé",
                    lambda: self._fire_employee(restaurant, decisions),
                )
                .add_option(
                    "📚 Former le personnel",
                    lambda: self._train_employees(restaurant, decisions),
                )
                .add_option(
                    "⏰ Ajuster les horaires",
                    lambda: self._adjust_schedules(restaurant, decisions),
                )
                .add_option(
                    "💰 Négocier les salaires",
                    lambda: self._negotiate_salaries(restaurant, decisions),
                )
                .add_option(
                    "📊 Analyser la productivité",
                    lambda: self._analyze_productivity(restaurant),
                )
            )

            menu.show()
            break

    def _recruit_employee(self, restaurant: Restaurant, decisions: dict) -> None:
        """Recrutement d'un nouvel employé."""
        if len(restaurant.employees) >= 10:  # Limite arbitraire
            show_error("Équipe complète (maximum 10 employés).")
            pause()
            return

        # Choix du poste
        positions = [pos.value for pos in EmployeePosition]
        position_choice = show_menu("Quel poste recruter ?", positions)

        if position_choice == 0:
            return

        selected_position = list(EmployeePosition)[position_choice - 1]

        # Choix du contrat
        contracts = [cont.value for cont in EmployeeContract]
        contract_choice = show_menu("Type de contrat ?", contracts)

        if contract_choice == 0:
            return

        selected_contract = list(EmployeeContract)[contract_choice - 1]

        # Salaire proposé
        salary_ranges = {
            EmployeePosition.CUISINE: (1800, 3000),
            EmployeePosition.SALLE: (1700, 2500),
            EmployeePosition.MANAGER: (2500, 4000),
            EmployeePosition.PLONGE: (1650, 1900),
            EmployeePosition.CAISSE: (1650, 2200),
        }

        min_salary, max_salary = salary_ranges.get(selected_position, (1650, 3000))

        salary = get_input(
            f"Salaire brut mensuel ({min_salary}-{max_salary}€)",
            Decimal,
            min_val=Decimal(str(min_salary)),
            max_val=Decimal(str(max_salary)),
            default=Decimal(str((min_salary + max_salary) // 2)),
        )

        if salary:
            # Calcul du coût total
            total_cost = salary * Decimal("1.42")  # Avec charges

            if restaurant.cash < total_cost * 3:  # Vérification de solvabilité
                if not confirm(
                    f"⚠️ Coût: {total_cost:.0f}€/mois. "
                    f"Votre trésorerie ne couvre que {restaurant.cash / total_cost:.1f} mois. "
                    f"Confirmer le recrutement ?"
                ):
                    return

            # Enregistrement de la décision
            if "recruitments" not in decisions:
                decisions["recruitments"] = []

            decisions["recruitments"].append(
                {
                    "position": selected_position,
                    "contract": selected_contract,
                    "salary": salary,
                }
            )

            show_success(
                f"Recrutement programmé: {selected_position.value} "
                f"en {selected_contract.value} à {salary:.0f}€/mois"
            )
            pause()

    def _purchasing_decisions(self, restaurant: Restaurant) -> None:
        """Gestion des achats et stocks avancée."""
        # État minimal requis pour le module Achats & Stocks
        menu = MenuHandler("ACHATS & STOCKS")
        menu.add_option(
            "📋 Prévision & Besoins",
            lambda: self._forecast_and_requirements(restaurant),
        ).add_option(
            "🛒 Composer ma commande (manuel)",
            lambda: self._compose_manual_order(restaurant),
        ).add_option(
            "🤖 Proposer une commande (auto, revue ligne)",
            lambda: self._review_auto_order(restaurant),
        ).add_option(
            "📥 Réception de commandes", lambda: self._receiving_interface(restaurant)
        ).add_option(
            "📦 État des stocks & alertes",
            lambda: self._stock_management_interface(restaurant),
        ).add_option("🔙 Retour", lambda: "exit")

        menu.show()

        # --- Achats & Stocks: Prévision, besoins, PO, réception ---
        # Pour simplifier, on stocke ces éléments sur l'objet restaurant s'ils n'existent pas

        # Structures d'état minimales attendues sur restaurant
        if not hasattr(restaurant, "stock_manager"):
            restaurant.stock_manager = StockManager()
        if not hasattr(restaurant, "sales_forecast"):
            restaurant.sales_forecast = {}  # recipe_id -> qty next turn
        if not hasattr(restaurant, "pending_po_lines"):
            restaurant.pending_po_lines = []  # List[POLine]

    def _forecast_and_requirements(self, restaurant: Restaurant) -> None:
        """Saisie de prévision par recette active et calcul des besoins net."""
        clear_screen()
        active = restaurant.get_active_menu()
        if not active:
            show_info("Aucune recette active pour établir une prévision.")
            pause()
            return

        print("📋 PRÉVISION DES VENTES (prochain tour):")
        auto = getattr(self._admin_settings, "auto_forecast_enabled", False)
        for rid in active.keys():
            cur = int(restaurant.sales_forecast.get(rid, 0))
            default_qty = cur if cur else (20 if auto else 0)
            qty = ask_int(
                f"  Portions prévues pour {rid} (actuel {cur}): ",
                min_val=0,
                max_val=1000,
                default=default_qty,
            )
            restaurant.sales_forecast[rid] = qty

        # Calcul besoins avec ProcurementPlanner
        planner = ProcurementPlanner()
        active_recipes = [
            self._available_recipes_cache[rid]
            for rid in restaurant.active_recipes
            if hasattr(self, "_available_recipes_cache")
            and rid in self._available_recipes_cache
        ]
        requirements = planner.compute_requirements(
            active_recipes,
            getattr(restaurant, "sales_forecast", {}),
            restaurant.stock_manager,
        )

        # Affichage synthétique des besoins
        lines = ["📦 BESOINS NETS:", ""]
        if not requirements:
            lines.append("Aucun besoin (stock suffisant ou prévision 0)")
        else:
            for ing_id, qty in requirements.items():
                lines.append(f"• {ing_id}: {qty}")
        print_box(lines, "BESOINS", "info")
        pause()

    def _compose_manual_order(self, restaurant: Restaurant) -> None:
        """Mode MANUEL: composer une commande multi-lignes à partir des besoins."""
        planner = ProcurementPlanner()
        active_recipes = [
            self._available_recipes_cache[rid]
            for rid in restaurant.active_recipes
            if hasattr(self, "_available_recipes_cache")
            and rid in self._available_recipes_cache
        ]
        requirements = planner.compute_requirements(
            active_recipes,
            getattr(restaurant, "sales_forecast", {}),
            restaurant.stock_manager,
        )

        if not requirements:
            show_info("Aucun besoin net détecté.")
            pause()
            return

        pending: list[POLine] = []
        for ing_id, need in requirements.items():
            print_box(
                [f"Ingrédient: {ing_id}", f"Besoin net estimé: {need}"],
                "COMPOSER COMMANDE",
                "info",
            )
            # Catalogue simple: issu du cost_calculator (fallback) + suppliers_catalog du jeu si dispo
            offers = []
            if (
                hasattr(self, "_suppliers_catalog")
                and ing_id in self._suppliers_catalog
            ):
                offers = self._suppliers_catalog[ing_id]
            else:
                if ing_id in self.cost_calculator.ingredients:
                    ing = self.cost_calculator.ingredients[ing_id]
                    offers = [
                        {
                            "supplier_id": "metro_pro",
                            "quality_level": 2,
                            "pack_size": Decimal("1"),
                            "unit_price_ht": ing.cost_ht,
                            "vat_rate": ing.vat_rate,
                            "moq_qty": Decimal("0"),
                            "moq_value": Decimal("0"),
                        }
                    ]

            if not offers:
                continue

            added_any = False
            while True:
                # Liste des offres (fournisseur + gamme) avec infos complètes
                options = [
                    f"{o['supplier_id']} | gamme {o['quality_level']} | pack {o['pack_size']} {o.get('pack_unit', '')} | "
                    f"{o['unit_price_ht']:.2f}€ HT | TVA {o['vat_rate']:.1%} | LT {o.get('lead_time_days', '?')}j | F {o.get('reliability', '?')}"
                    for o in offers
                ]
                choice = show_menu(f"Choisir une offre pour {ing_id}", options)
                if choice == 0:
                    break
                offer = offers[choice - 1]

                qty_wanted = get_input(
                    f"Quantité souhaitée (peut être > besoin {need})",
                    Decimal,
                    min_val=Decimal("0"),
                    default=need,
                )
                if qty_wanted is None:
                    break

                # Arrondi pack vers le haut
                packs = (qty_wanted / offer["pack_size"]).to_integral_value(
                    rounding="ROUND_CEILING"
                )
                qty_final = packs * offer["pack_size"]

                # MOQ quantité & valeur
                if (
                    offer.get("moq_qty", Decimal("0")) > 0
                    and qty_final < offer["moq_qty"]
                ):
                    show_info(f"MOQ quantité {offer['moq_qty']} appliqué → ajustement")
                    qty_final = offer["moq_qty"]
                order_value = qty_final * offer["unit_price_ht"]
                if (
                    offer.get("moq_value", Decimal("0")) > 0
                    and order_value < offer["moq_value"]
                ):
                    deficit_value = offer["moq_value"] - order_value
                    extra_units = (
                        deficit_value / offer["unit_price_ht"]
                    ).to_integral_value(rounding="ROUND_CEILING")
                    qty_final += extra_units
                    order_value = qty_final * offer["unit_price_ht"]

                line = POLine(
                    ingredient_id=ing_id,
                    quantity=qty_final,
                    unit_price_ht=offer["unit_price_ht"],
                    vat_rate=offer["vat_rate"],
                    supplier_id=offer["supplier_id"],
                    pack_size=offer["pack_size"],
                    pack_unit=offer.get("pack_unit"),
                    quality_level=offer.get("quality_level"),
                    eta_days=offer.get("lead_time_days"),
                    qty_rounded_pack=qty_final,
                    moq_ok=True,
                    amount_ttc_estimated=(qty_final * offer["unit_price_ht"])
                    * (Decimal("1") + offer["vat_rate"]),
                )
                pending.append(line)
                added_any = True

                # Infos coût TTC & ETA
                cost_ttc = order_value * (Decimal("1") + offer["vat_rate"])
                eta_days = offer.get("lead_time_days", None)
                moq_msg = []
                if offer.get("moq_qty", Decimal("0")) > 0:
                    moq_msg.append(f"MOQ qty {offer['moq_qty']}")
                if offer.get("moq_value", Decimal("0")) > 0:
                    moq_msg.append(f"MOQ valeur {offer['moq_value']:.2f}€")
                moq_str = f" ({', '.join(moq_msg)})" if moq_msg else ""
                show_info(
                    f"Ligne ajoutée: {qty_final} @ {offer['unit_price_ht']:.2f}€ (HT={order_value:.2f}€, TTC={cost_ttc:.2f}€){moq_str} | ETA {eta_days}j"
                )

                if not confirm(
                    "Ajouter une autre ligne (autre offre) pour cet ingrédient ?"
                ):
                    break

            if added_any and not confirm("Passer à l'ingrédient suivant ?"):
                break

        if pending:
            restaurant.pending_po_lines = pending
            show_success(
                f"{len(pending)} lignes de commande enregistrées (à réceptionner)"
            )
        else:
            show_info("Aucune ligne créée.")
        pause()

    def _review_auto_order(self, restaurant: Restaurant) -> None:
        """Mode AUTO: propose un PO mais oblige revue par ligne (fournisseur/gamme/quantité)."""
        planner = ProcurementPlanner()
        active_recipes = [
            self._available_recipes_cache[rid]
            for rid in restaurant.active_recipes
            if hasattr(self, "_available_recipes_cache")
            and rid in self._available_recipes_cache
        ]
        requirements = planner.compute_requirements(
            active_recipes,
            getattr(restaurant, "sales_forecast", {}),
            restaurant.stock_manager,
        )

        # Appliquer requirement de confirmation par ligne
        if getattr(self._admin_settings, "require_line_confirmation", True):
            reviewed: list[POLine] = []
            for i, l in enumerate(pending, 1):
                print_box(
                    [
                        f"{i}. {l.ingredient_id}: {l.quantity} @ {l.unit_price_ht:.2f}€ (pack {l.pack_size}) chez {l.supplier_id}"
                    ],
                    "REVUE LIGNE",
                    "warning",
                )
                # Permettre un override quantité (sur-stock autorisé)
                new_qty = get_input(
                    "Quantité souhaitée (arrondi pack ensuite)",
                    Decimal,
                    min_val=Decimal("0"),
                    default=l.quantity,
                )
                if new_qty is not None:
                    packs = (new_qty / l.pack_size).to_integral_value(
                        rounding="ROUND_CEILING"
                    )
                    l = POLine(
                        ingredient_id=l.ingredient_id,
                        quantity=packs * l.pack_size,
                        unit_price_ht=l.unit_price_ht,
                        vat_rate=l.vat_rate,
                        supplier_id=l.supplier_id,
                        pack_size=l.pack_size,
                    )
                reviewed.append(l)

        # Construire catalogue à partir du cache
        suppliers_catalog = {}
        if hasattr(self, "_suppliers_catalog"):
            # Transformer la liste d'offres en dict supplier->offer struct pour planner
            for ing_id, offers in self._suppliers_catalog.items():
                suppliers_catalog[ing_id] = {}
                for o in offers:
                    suppliers_catalog[ing_id][o["supplier_id"]] = {
                        "price_ht": o["unit_price_ht"],
                        "vat": o["vat_rate"],
                        "pack": o["pack_size"],
                        "moq_value": o.get("moq_value", Decimal("0")),
                    }

        auto_lines = planner.propose_purchase_orders(requirements, suppliers_catalog)
        if not auto_lines:
            show_info("Aucune proposition automatique disponible.")
            pause()
            return

        reviewed: list[POLine] = []
        for i, l in enumerate(auto_lines, 1):
            need = requirements.get(l.ingredient_id, Decimal("0"))
            order_value = l.quantity * l.unit_price_ht
            print_box(
                [
                    f"{i}. {l.ingredient_id} → besoin {need}",
                    f"Proposition: {l.quantity} @ {l.unit_price_ht:.2f}€ HT (pack {l.pack_size}) chez {l.supplier_id} | HT={order_value:.2f}€",
                ],
                "REVUE LIGNE",
                "warning",
            )

            # Choix fournisseur+gamme parmi offres
            offers = (
                self._suppliers_catalog.get(l.ingredient_id, [])
                if hasattr(self, "_suppliers_catalog")
                else []
            )
            if offers:
                options = [
                    f"{o['supplier_id']} | gamme {o['quality_level']} | pack {o['pack_size']} {o.get('pack_unit', '')} | {o['unit_price_ht']:.2f}€ HT | TVA {o['vat_rate']:.1%} | LT {o.get('lead_time_days', '?')}j | F {o.get('reliability', '?')}"
                    for o in offers
                ]
                ch = show_menu(
                    "Choisir fournisseur/gamme (ou retour pour garder)", options
                )
                if ch > 0:
                    o = offers[ch - 1]
                    l = POLine(
                        ingredient_id=l.ingredient_id,
                        quantity=l.quantity,
                        unit_price_ht=o["unit_price_ht"],
                        vat_rate=o["vat_rate"],
                        supplier_id=o["supplier_id"],
                        pack_size=o["pack_size"],
                    )

            # Modifier quantité (sur-stock autorisé) + arrondi pack
            new_qty = get_input(
                "Quantité souhaitée (arrondi pack ensuite)",
                Decimal,
                min_val=Decimal("0"),
                default=l.quantity,
            )
            if new_qty is not None:
                packs = (new_qty / l.pack_size).to_integral_value(
                    rounding="ROUND_CEILING"
                )
                l = POLine(
                    ingredient_id=l.ingredient_id,
                    quantity=packs * l.pack_size,
                    unit_price_ht=l.unit_price_ht,
                    vat_rate=l.vat_rate,
                    supplier_id=l.supplier_id,
                    pack_size=l.pack_size,
                )

            reviewed.append(l)

        restaurant.pending_po_lines = reviewed
        show_success("Commande automatique revue et enregistrée (à réceptionner)")
        pause()

        # Note: les recettes doivent être en cache pour calculs précis
        if not hasattr(self, "_available_recipes_cache"):
            show_info(
                "Note: pour le calcul précis des besoins, les recettes doivent être connues. Cette version affichera le stock uniquement si non disponible."
            )
            pause()
            return

    def cache_available_recipes(self, recipes: dict[str, any]) -> None:
        """Optionnel: l'appelant peut fournir un cache des recettes pour achats."""
        self._available_recipes_cache = recipes

    def _propose_purchase_order(self, restaurant: Restaurant, decisions: dict) -> None:
        """Propose un PO en fonction des besoins et permet édition simple."""
        clear_screen()
        if not hasattr(self, "_available_recipes_cache"):
            show_error(
                "Recettes non disponibles pour proposer une commande. Activez des recettes et revenez."
            )
            pause()
            return

        active_recipes = [
            self._available_recipes_cache[rid]
            for rid in restaurant.active_recipes
            if rid in self._available_recipes_cache
        ]
        planner = ProcurementPlanner()
        requirements = planner.compute_requirements(
            active_recipes, restaurant.sales_forecast, restaurant.stock_manager
        )

        if not requirements:
            show_info("Aucun besoin net détecté (stock suffisant ou prévision nulle).")
            pause()
            return

        # Construire un petit catalogue fournisseur factice basé sur l’ingrédient (utilise cost catalog)
        suppliers_catalog = {}
        # On estime prix à partir des ingrédients connus par le cost_calculator
        for ing_id, need in requirements.items():
            if ing_id in self.cost_calculator.ingredients:
                ing = self.cost_calculator.ingredients[ing_id]
                suppliers_catalog[ing_id] = {
                    "metro_pro": {
                        "price_ht": ing.cost_ht,
                        "vat": ing.vat_rate,
                        "pack": Decimal("1"),
                        "moq_value": Decimal("0"),
                    }
                }

        lines = planner.propose_purchase_orders(requirements, suppliers_catalog)
        if not lines:
            show_info("Aucune proposition de commande possible (catalogue incomplet).")
            pause()
            return

        # Affichage et édition simple
        view = ["🛒 PROPOSITION DE COMMANDE:", ""]
        total_value = Decimal("0")
        for i, line in enumerate(lines, 1):
            line_value = line.quantity * line.unit_price_ht
            total_value += line_value
            view.append(
                f"{i}. {line.ingredient_id} — {line.quantity} @ {line.unit_price_ht:.2f}€ (HT) = {line_value:.2f}€ — {line.supplier_id}"
            )

        view.append("")
        view.append(f"Total HT estimé: {total_value:.2f}€")
        print_box(view, "COMMANDE FOURNISSEURS", "info")

        if confirm("Valider cette commande ?"):
            # Enregistrer comme en attente
            restaurant.pending_po_lines = lines
            decisions.setdefault("purchase_orders", []).append(
                {
                    "lines": [
                        {
                            "ingredient_id": l.ingredient_id,
                            "qty": str(l.quantity),
                            "price_ht": str(l.unit_price_ht),
                            "supplier": l.supplier_id,
                        }
                        for l in lines
                    ],
                    "total_ht": str(total_value),
                }
            )
            show_success("Commande enregistrée (à réceptionner)")
        else:
            show_info("Commande annulée")
        pause()

    def _receiving_interface(self, restaurant: Restaurant) -> None:
        """Réceptionne les lignes en attente et crée des lots FEFO."""
        clear_screen()
        from decimal import Decimal

        lines: list[POLine] = getattr(restaurant, "pending_po_lines", [])
        if not lines:
            show_info("Aucune commande en attente.")
            pause()
            return

        view = ["📥 RÉCEPTION DE COMMANDES:", ""]
        for i, l in enumerate(lines, 1):
            view.append(
                f"{i}. {l.ingredient_id} — Cmd: {l.quantity} | Acc: {l.accepted_qty} | Statut: {l.status}"
            )
        print_box(view, "BON DE COMMANDE EN ATTENTE", "info")

        # Saisie réception par ligne: accepter/refuser et split lots
        from datetime import date

        from game_engine.domain.stock.procurement import (
            DeliveryLine,
            GoodsReceipt,
            GoodsReceiptLine,
            ReceivingService,
        )

        gr_lines: list[GoodsReceiptLine] = []
        remaining_lines: list[POLine] = []
        all_lots: list = []

        for l in lines:
            # Choix action
            action = show_menu(
                f"Ligne {l.ingredient_id} (Cmd {l.quantity}, Acc {l.accepted_qty})",
                ["Accepter (total/partiel)", "Refuser"],
            )
            if action == 0:
                remaining_lines.append(l)
                continue

            if action == 2:
                # Refus: on garde la ligne en attente, aucun lot
                gr_lines.append(
                    GoodsReceiptLine(
                        ingredient_id=l.ingredient_id,
                        qty_ordered=l.quantity,
                        qty_delivered=Decimal("0"),
                        qty_accepted=Decimal("0"),
                        unit_price_ht=l.unit_price_ht,
                        vat_rate=l.vat_rate,
                        supplier_id=l.supplier_id,
                        pack_size=l.pack_size,
                        lots=[],
                        comment="Refusé",
                    )
                )
                remaining_lines.append(l)  # reste en attente
                continue

            # Accepter (total/partiel)
            # Proposer une quantité livrée (par défaut = quantité commandée restante)
            to_receive_default = l.quantity - l.accepted_qty
            if to_receive_default < 0:
                to_receive_default = Decimal("0")
            qty_delivered = get_input(
                f"Quantité livrée pour {l.ingredient_id} (reste {to_receive_default} à recevoir): ",
                Decimal,
                min_val=Decimal("0"),
                default=to_receive_default,
            ) or Decimal("0")

            # Option de split lots
            deliveries: list[DeliveryLine] = []
            if qty_delivered > 0:
                nb_lots = ask_int(
                    f"Nombre de lots pour {l.ingredient_id} (1 par défaut)",
                    min_val=1,
                    max_val=10,
                    default=1,
                )
                if nb_lots <= 1:
                    deliveries.append(
                        DeliveryLine(
                            ingredient_id=l.ingredient_id,
                            quantity_received=qty_delivered,
                            unit_price_ht=l.unit_price_ht,
                            vat_rate=l.vat_rate,
                            supplier_id=l.supplier_id,
                            pack_size=l.pack_size,
                            lot_number=None,
                            quality_level=l.quality_level or 2,
                        )
                    )
                else:
                    qty_remaining = qty_delivered
                    for i in range(nb_lots):
                        if i == nb_lots - 1:
                            q = qty_remaining
                        else:
                            q = get_input(
                                f"  Quantité lot {i + 1} (reste {qty_remaining})",
                                Decimal,
                                min_val=Decimal("0.001"),
                                max_val=qty_remaining,
                                default=(qty_remaining / Decimal(str(nb_lots - i))),
                            )
                        qty_remaining -= q
                        deliveries.append(
                            DeliveryLine(
                                ingredient_id=l.ingredient_id,
                                quantity_received=q,
                                unit_price_ht=l.unit_price_ht,
                                vat_rate=l.vat_rate,
                                supplier_id=l.supplier_id,
                                pack_size=l.pack_size,
                                lot_number=get_input(
                                    f"  Numéro lot {i + 1} (optionnel)",
                                    str,
                                    default=f"{l.ingredient_id}-{i + 1}",
                                ),
                                quality_level=l.quality_level or 2,
                            )
                        )

            # Calcul lots et ajout en stock
            receiver = ReceivingService(shelf_life_rules={1: -2, 3: 0, 5: 2})
            lots = (
                receiver.receive(deliveries, date.today(), default_shelf_life_days=5)
                if deliveries
                else []
            )
            for lot in lots:
                restaurant.stock_manager.add_lot(lot)
            all_lots.extend(lots)

            qty_accepted = sum([lt.quantity for lt in lots], Decimal("0"))
            l.accepted_qty += qty_accepted
            # Statut de ligne
            if l.accepted_qty <= 0:
                l.status = "OPEN"
            elif l.accepted_qty < l.quantity:
                l.status = "PARTIAL"
            else:
                l.status = "CLOSED"

            gr_lines.append(
                GoodsReceiptLine(
                    ingredient_id=l.ingredient_id,
                    qty_ordered=l.quantity,
                    qty_delivered=qty_delivered,
                    qty_accepted=qty_accepted,
                    unit_price_ht=l.unit_price_ht,
                    vat_rate=l.vat_rate,
                    supplier_id=l.supplier_id,
                    pack_size=l.pack_size,
                    lots=lots,
                    comment=None,
                )
            )

            if l.status != "CLOSED":
                remaining_lines.append(l)

        # Mettre à jour pending_po_lines en gardant seulement les lignes non CLOSED
        restaurant.pending_po_lines = remaining_lines

        total_ht = sum(
            [(ln.qty_accepted * ln.unit_price_ht) for ln in gr_lines], Decimal("0")
        )
        total_ttc = sum(
            [
                (ln.qty_accepted * ln.unit_price_ht) * (Decimal("1") + ln.vat_rate)
                for ln in gr_lines
            ],
            Decimal("0"),
        )
        po_status = (
            "CLOSED"
            if not remaining_lines
            else (
                "PARTIAL"
                if any(l.accepted_qty > 0 for l in remaining_lines)
                else "OPEN"
            )
        )
        gr = GoodsReceipt(
            date=date.today(),
            lines=gr_lines,
            total_ht=total_ht,
            total_ttc=total_ttc,
            status=po_status,
        )
        restaurant._last_goods_receipt = gr

        # Récap et alertes DLC
        view = [
            f"GR du {gr.date} — Statut PO: {gr.status}",
            f"Total accepté HT: {gr.total_ht:.2f}€ | TTC: {gr.total_ttc:.2f}€",
            "Détail par ligne:",
        ]
        for ln in gr.lines:
            view.append(
                f"• {ln.ingredient_id}: Cmd {ln.qty_ordered} | Livr {ln.qty_delivered} | Acc {ln.qty_accepted}"
            )
        print_box(view, "BON DE RÉCEPTION", "success")

        expiring = restaurant.stock_manager.get_expiring_lots(days=3)
        if expiring:
            msg = ["⚠️ LOTS PROCHE DLC:"] + [
                f"• {lt.ingredient_id} ({lt.quantity}) — DLC {lt.dlc}"
                for lt in expiring
            ]
            print_box(msg, "ALERTES DLC", "warning")

        pause()

    def _place_order_interface(self, restaurant: Restaurant, decisions: dict) -> None:
        """Interface de commande avec choix de qualité."""
        clear_screen()
        show_info("🛒 CHOIX QUALITÉ DES INGRÉDIENTS")

        # Affichage de l'état actuel
        current_quality = restaurant.get_overall_quality_score()
        print(
            f"\n📊 QUALITÉ ACTUELLE: {restaurant.get_quality_description()} ({current_quality:.1f}/5)"
        )
        print(f"💰 Impact coût: {restaurant.calculate_quality_cost_impact():.0%}")
        print(f"⭐ Réputation: {restaurant.reputation:.1f}/10")

        # Choix des ingrédients principaux
        ingredients_to_configure = [
            ("beef_ground", "🥩 Viande (bœuf haché)"),
            ("tomato", "🍅 Légumes (tomates)"),
            ("cheese_mozzarella", "🧀 Fromage (mozzarella)"),
            ("flour", "🌾 Féculents (farine)"),
        ]

        print("\n🎯 NIVEAUX DE QUALITÉ DISPONIBLES:")
        print("   1⭐ Économique (-30% coût, -20% satisfaction)")
        print("   2⭐ Standard (prix de référence)")
        print("   3⭐ Supérieur (+25% coût, +15% satisfaction)")
        print("   4⭐ Premium (+50% coût, +30% satisfaction)")
        print("   5⭐ Luxe (+100% coût, +50% satisfaction)")

        changes_made = False

        for ingredient_id, ingredient_name in ingredients_to_configure:
            current_level = restaurant.ingredient_choices.get(ingredient_id, 2)
            print(f"\n{ingredient_name} (actuel: {current_level}⭐)")

            new_level = ask_int(
                f"   Nouveau niveau (1-5) [actuel: {current_level}]: ",
                min_val=1,
                max_val=5,
                default=current_level,
            )

            if new_level != current_level:
                restaurant.set_ingredient_quality(ingredient_id, new_level)
                changes_made = True
                print(
                    f"   ✅ {ingredient_name} mis à jour: {current_level}⭐ → {new_level}⭐"
                )

        if changes_made:
            # Recalcul des métriques
            new_quality = restaurant.get_overall_quality_score()
            new_cost_impact = restaurant.calculate_quality_cost_impact()

            print("\n📈 IMPACT DES CHANGEMENTS:")
            print(f"   Qualité: {current_quality:.1f}/5 → {new_quality:.1f}/5")
            print(f"   Coût matières: {restaurant.calculate_quality_cost_impact():.0%}")
            print(f"   Description: {restaurant.get_quality_description()}")

            # Sauvegarde dans les décisions
            decisions["ingredient_quality_changes"] = {
                "previous_score": float(current_quality),
                "new_score": float(new_quality),
                "cost_impact": float(new_cost_impact),
                "ingredients": dict(restaurant.ingredient_choices),
            }

            show_success("✅ Choix de qualité enregistrés !")
        else:
            show_info("ℹ️ Aucun changement effectué")

        pause()

    def _stock_management_interface(self, restaurant: Restaurant) -> None:
        """Interface de gestion des stocks."""
        show_info("📦 GESTION DES STOCKS")

        # Simuler l'affichage des stocks
        stock_info = [
            "📊 ÉTAT DES STOCKS:",
            "🥩 Steak haché:",
            "   Lot A: 15kg (expire dans 2 jours) ⚠️",
            "   Lot B: 8kg (expire dans 5 jours) ✅",
            "🍅 Tomates:",
            "   Lot C: 5kg (expire demain) 🚨 PROMOTION -50%",
            "   Lot D: 12kg (expire dans 4 jours) ✅",
            "💡 Actions recommandées:",
            "• Utiliser le Lot A en priorité (FEFO)",
            "• Promouvoir les tomates du Lot C",
            "• Commander du steak haché (stock bas)",
        ]

        print_box(stock_info, "STOCKS ACTUELS")
        pause()

    def _supplier_analysis_interface(self, restaurant: Restaurant) -> None:
        """Interface d'analyse des fournisseurs."""
        show_info("🏪 ANALYSE DES FOURNISSEURS")

        suppliers_data = [
            "📊 COMPARATIF FOURNISSEURS:",
            "🥩 METRO PRO:",
            "   Fiabilité: 95% | Délai: 1j | Prix: Standard",
            "   Spécialité: Gamme complète 1★-3★",
            "🌱 BIO FRANCE:",
            "   Fiabilité: 88% | Délai: 3j | Prix: +20%",
            "   Spécialité: Bio et premium 3★-5★",
            "🚚 RUNGIS DIRECT:",
            "   Fiabilité: 92% | Délai: 2j | Prix: Variable",
            "   Spécialité: Frais quotidien 2★-4★",
            "💡 Recommandation: Diversifiez vos sources",
            "   selon votre positionnement qualité",
        ]

        print_box(suppliers_data, "FOURNISSEURS")
        pause()

    def _quality_price_report(self, restaurant: Restaurant) -> None:
        """Rapport qualité/prix détaillé."""
        clear_screen()
        show_info("📊 RAPPORT QUALITÉ/PRIX DÉTAILLÉ")

        # Métriques actuelles
        quality_score = restaurant.get_overall_quality_score()
        cost_impact = restaurant.calculate_quality_cost_impact()
        avg_satisfaction = restaurant.get_average_satisfaction()
        avg_ticket = restaurant.get_average_ticket()

        # Facteurs d'attractivité par segment
        segments = ["students", "families", "foodies"]
        attractiveness_factors = {}
        for segment in segments:
            factor = restaurant.get_quality_attractiveness_factor(segment)
            attractiveness_factors[segment] = factor

        report_data = [
            "📈 MÉTRIQUES QUALITÉ ACTUELLES:",
            f"Score qualité global: {restaurant.get_quality_description()} ({quality_score:.1f}/5)",
            f"Impact sur coûts: {cost_impact:.0%}",
            f"Satisfaction client: {avg_satisfaction:.1f}/5",
            f"Réputation: {restaurant.reputation:.1f}/10",
            f"Ticket moyen: {avg_ticket:.2f}€",
            "🎯 ATTRACTIVITÉ PAR SEGMENT:",
            f"• Étudiants: {attractiveness_factors['students']:.0%} (sensibilité faible)",
            f"• Familles: {attractiveness_factors['families']:.0%} (sensibilité normale)",
            f"• Foodies: {attractiveness_factors['foodies']:.0%} (sensibilité élevée)",
            "💰 ANALYSE COÛT/BÉNÉFICE:",
        ]

        # Simulation d'amélioration qualité
        if quality_score < 4.0:
            min(5.0, quality_score + 1.0)
            cost_increase = 25  # Estimation +25% pour +1 niveau
            satisfaction_increase = 15  # Estimation +15% satisfaction

            report_data.extend(
                [
                    "📈 SIMULATION AMÉLIORATION (+1 niveau qualité):",
                    f"• Coût supplémentaire estimé: +{cost_increase}%",
                    f"• Satisfaction supplémentaire: +{satisfaction_increase}%",
                    f"• Nouvelle attractivité foodies: +{satisfaction_increase * 1.5:.0f}%",
                ]
            )

        # Recommandations personnalisées
        recommendations = []

        if quality_score < 2.5:
            recommendations.append("🔴 PRIORITÉ: Améliorer la qualité de base")
            recommendations.append("• Passer au moins 2 ingrédients en niveau 3⭐")
        elif quality_score < 3.5:
            recommendations.append("🟡 OPPORTUNITÉ: Différenciation qualité")
            recommendations.append("• Cibler les foodies avec du premium (4⭐)")
        else:
            recommendations.append("🟢 EXCELLENCE: Maintenir la qualité")
            recommendations.append("• Optimiser les coûts sans perdre en qualité")

        if restaurant.reputation < 6.0:
            recommendations.append("• Améliorer la satisfaction pour la réputation")

        if avg_ticket > 0 and quality_score > 0:
            price_quality_ratio = float(avg_ticket / quality_score)
            if price_quality_ratio > 4.0:
                recommendations.append(
                    "• Prix élevé vs qualité: risque de perte clients"
                )
            elif price_quality_ratio < 2.5:
                recommendations.append(
                    "• Excellent rapport qualité/prix: potentiel hausse prix"
                )

        report_data.extend(["🎯 RECOMMANDATIONS PERSONNALISÉES:", ""])
        report_data.extend(recommendations)

        # Détail des ingrédients
        if restaurant.ingredient_choices:
            report_data.extend(["", "🥘 DÉTAIL INGRÉDIENTS:", ""])
            for ingredient_id, level in restaurant.ingredient_choices.items():
                ingredient_name = {
                    "beef_ground": "Viande",
                    "tomato": "Légumes",
                    "cheese_mozzarella": "Fromage",
                    "flour": "Féculents",
                }.get(ingredient_id, ingredient_id)

                stars = "⭐" * level
                report_data.append(f"• {ingredient_name}: {stars} (niveau {level})")

        print_box(report_data, "RAPPORT QUALITÉ/PRIX")
        pause()

    def _alerts_promotions_interface(self, restaurant: Restaurant) -> None:
        """Interface des alertes et promotions."""
        show_info("⚠️ ALERTES ET PROMOTIONS")

        alerts_data = [
            "🚨 ALERTES URGENTES:",
            "• 5kg de tomates expirent demain",
            "  → Promotion -50% recommandée",
            "• Stock de steak haché bas (8kg restants)",
            "  → Commande urgente suggérée",
            "🎯 OPPORTUNITÉS SAISONNIÈRES:",
            "• Tomates d'été: -30% ce mois",
            "  → Qualité +1★ pour même prix",
            "• Champignons d'automne disponibles",
            "  → Nouveau plat saisonnier possible",
        ]

        print_box(alerts_data, "ALERTES")
        pause()

    def _marketing_interface(self, restaurant: Restaurant, decisions: dict) -> None:
        """Interface marketing et communication."""
        clear_screen()
        show_info("📈 MARKETING & COMMUNICATION")

        # Simuler l'état marketing actuel
        print("\n📊 ÉTAT MARKETING ACTUEL:")
        print("   Réputation en ligne: 4.2/5 ⭐ (127 avis)")
        print("   Budget marketing mensuel: 850€")
        print("   Campagnes actives: 2")
        print("   ROI marketing: 3.2x")

        # Options de campagnes
        print("\n🎯 CAMPAGNES DISPONIBLES:")
        campaigns = [
            {
                "name": "Réseaux sociaux",
                "cost": "50€/jour",
                "reach": "1000 personnes",
                "conversion": "2.5%",
            },
            {
                "name": "Publicité locale",
                "cost": "80€/jour",
                "reach": "750 personnes",
                "conversion": "3.5%",
            },
            {
                "name": "Programme fidélité",
                "cost": "30€/jour",
                "reach": "150 clients",
                "conversion": "15%",
            },
            {
                "name": "Événement spécial",
                "cost": "200€/jour",
                "reach": "400 personnes",
                "conversion": "8%",
            },
        ]

        for i, campaign in enumerate(campaigns, 1):
            print(
                f"   {i}. {campaign['name']}: {campaign['cost']} - {campaign['reach']} - {campaign['conversion']}"
            )

        print("\n💡 RECOMMANDATIONS:")
        print("   • Augmenter présence réseaux sociaux (+20% clients jeunes)")
        print("   • Lancer programme fidélité (rétention +30%)")
        print("   • Répondre aux avis négatifs (réputation +0.3)")

        # Choix de campagne
        choice = ask_int(
            "Lancer une campagne (1-4) ou 0 pour passer: ",
            min_val=0,
            max_val=4,
            default=0,
        )
        if choice > 0:
            campaign = campaigns[choice - 1]
            duration = ask_int(
                f"Durée en jours pour '{campaign['name']}': ",
                min_val=1,
                max_val=30,
                default=7,
            )

            decisions["marketing_campaign"] = {
                "type": campaign["name"],
                "cost_per_day": campaign["cost"],
                "duration": duration,
                "expected_reach": campaign["reach"],
                "expected_conversion": campaign["conversion"],
            }

            show_success(
                f"✅ Campagne '{campaign['name']}' programmée pour {duration} jours"
            )
        else:
            show_info("ℹ️ Aucune campagne lancée")

        pause()

    def _finance_interface(self, restaurant: Restaurant, decisions: dict) -> None:
        """Interface finance avancée."""
        clear_screen()
        show_info("💰 FINANCE AVANCÉE")

        # Simuler les données financières
        print("\n📊 TABLEAU DE BORD FINANCIER:")
        print("   Trésorerie: 12,450€")
        print("   CA mensuel: 28,750€")
        print("   Marge brute: 65.2%")
        print("   Résultat net: 4,320€ (15.0%)")

        print("\n📈 RATIOS FINANCIERS:")
        print("   Liquidité: 2.1 (Bon)")
        print("   Endettement: 35% (Acceptable)")
        print("   ROE: 18.5% (Excellent)")
        print("   Rotation stocks: 12x/an (Optimal)")

        print("\n🍽️ RENTABILITÉ PAR PLAT:")
        dishes = [
            {
                "name": "Burger Classic",
                "price": "12.50€",
                "cost": "4.20€",
                "margin": "66.4%",
                "volume": 145,
            },
            {
                "name": "Salade César",
                "price": "9.80€",
                "cost": "3.10€",
                "margin": "68.4%",
                "volume": 89,
            },
            {
                "name": "Pizza Margherita",
                "price": "11.00€",
                "cost": "3.80€",
                "margin": "65.5%",
                "volume": 112,
            },
            {
                "name": "Pâtes Carbonara",
                "price": "10.50€",
                "cost": "2.90€",
                "margin": "72.4%",
                "volume": 78,
            },
        ]

        for dish in dishes:
            print(
                f"   • {dish['name']}: {dish['price']} (coût: {dish['cost']}, marge: {dish['margin']}, vol: {dish['volume']})"
            )

        print("\n💡 RECOMMANDATIONS FINANCIÈRES:")
        print("   • Augmenter prix Burger Classic (+0.50€ = +290€/mois)")
        print("   • Promouvoir Pâtes Carbonara (marge la plus élevée)")
        print("   • Optimiser coûts Pizza Margherita (-0.20€ coût)")
        print("   • Négocier délais fournisseurs (trésorerie +15%)")

        # Options financières
        print("\n🎯 ACTIONS DISPONIBLES:")
        print("   1. Demander un prêt bancaire")
        print("   2. Investir dans du matériel")
        print("   3. Optimiser la trésorerie")
        print("   4. Analyser un investissement")

        choice = ask_int(
            "Choisir une action (1-4) ou 0 pour passer: ",
            min_val=0,
            max_val=4,
            default=0,
        )

        if choice == 1:
            amount = ask_float(
                "Montant du prêt souhaité (€): ",
                min_val=1000,
                max_val=50000,
                default=10000,
            )
            decisions["loan_request"] = {
                "amount": amount,
                "purpose": "expansion",
                "estimated_rate": "4.5%",
            }
            show_success(f"✅ Demande de prêt de {amount:,.0f}€ enregistrée")

        elif choice == 2:
            equipment_options = [
                {
                    "name": "Four professionnel",
                    "cost": 8500,
                    "benefit": "+20% capacité",
                },
                {
                    "name": "Système de caisse",
                    "cost": 2200,
                    "benefit": "+15% efficacité",
                },
                {
                    "name": "Frigo supplémentaire",
                    "cost": 3800,
                    "benefit": "+30% stocks",
                },
            ]

            print("\n🔧 ÉQUIPEMENTS DISPONIBLES:")
            for i, eq in enumerate(equipment_options, 1):
                print(f"   {i}. {eq['name']}: {eq['cost']}€ ({eq['benefit']})")

            eq_choice = ask_int(
                "Choisir équipement (1-3): ", min_val=1, max_val=3, default=1
            )
            equipment = equipment_options[eq_choice - 1]

            decisions["equipment_purchase"] = {
                "name": equipment["name"],
                "cost": equipment["cost"],
                "benefit": equipment["benefit"],
            }
            show_success(f"✅ Achat {equipment['name']} programmé")

        elif choice == 3:
            print("\n💰 OPTIMISATION TRÉSORERIE:")
            print("   • Négocier délais paiement fournisseurs: +2,100€")
            print("   • Accélérer encaissements clients: +850€")
            print("   • Optimiser niveau stocks: +1,200€")

            decisions["cash_optimization"] = True
            show_success("✅ Plan d'optimisation trésorerie activé")

        elif choice == 4:
            investment_amount = ask_float(
                "Montant investissement (€): ",
                min_val=1000,
                max_val=30000,
                default=5000,
            )
            expected_return = investment_amount * 0.15  # 15% de retour estimé
            payback_months = investment_amount / (expected_return / 12)

            print("\n📊 ANALYSE INVESTISSEMENT:")
            print(f"   Investissement: {investment_amount:,.0f}€")
            print(f"   Retour annuel estimé: {expected_return:,.0f}€")
            print("   Retour sur investissement: 15%")
            print(f"   Période de retour: {payback_months:.1f} mois")

            decisions["investment_analysis"] = {
                "amount": investment_amount,
                "expected_return": expected_return,
                "roi": 0.15,
                "payback_months": payback_months,
            }

        else:
            show_info("ℹ️ Aucune action financière")

        pause()

    def _marketing_decisions(self, restaurant: Restaurant, decisions: dict) -> None:
        """Décisions marketing et commerciales."""
        menu = MenuHandler("MARKETING & COMMERCIAL")
        menu.add_option(
            "📢 Lancer une campagne publicitaire",
            lambda: self._advertising_campaign(restaurant, decisions),
        ).add_option(
            "🎁 Programme de fidélité",
            lambda: self._loyalty_program(restaurant, decisions),
        ).add_option(
            "🎉 Organiser un événement spécial",
            lambda: self._special_event(restaurant, decisions),
        ).add_option(
            "🤝 Partenariats locaux",
            lambda: (show_info("Option - En développement"), pause()),
        ).add_option(
            "📱 Présence digitale",
            lambda: (show_info("Option - En développement"), pause()),
        ).add_option(
            "💳 Moyens de paiement",
            lambda: (show_info("Option - En développement"), pause()),
        ).add_option("🔙 Retour", lambda: "exit")

        menu.show()

    def _advertising_campaign(self, restaurant: Restaurant, decisions: dict) -> None:
        """Campagne publicitaire."""
        campaign_types = [
            (
                "Flyers quartier",
                200,
                "Faible",
                "Distribution de flyers dans le quartier",
            ),
            ("Radio locale", 800, "Moyen", "Spot radio aux heures de pointe"),
            ("Réseaux sociaux", 300, "Moyen", "Campagne Facebook/Instagram ciblée"),
            (
                "Journal local",
                500,
                "Faible",
                "Encart publicitaire dans la presse locale",
            ),
            ("Influenceurs", 1200, "Fort", "Collaboration avec des influenceurs food"),
        ]

        clear_screen()

        campaign_options = [
            f"{name} - {cost}€ (Impact: {impact})"
            for name, cost, impact, desc in campaign_types
        ]

        choice = show_menu("CAMPAGNES PUBLICITAIRES", campaign_options)

        if choice == 0:
            return

        selected_campaign = campaign_types[choice - 1]
        name, cost, impact, description = selected_campaign

        # Affichage des détails
        details = [
            f"CAMPAGNE: {name}",
            f"Coût: {cost}€",
            f"Impact attendu: {impact}",
            f"Description: {description}",
            f"Trésorerie actuelle: {restaurant.cash:.0f}€",
            f"Trésorerie après campagne: {restaurant.cash - cost:.0f}€",
        ]

        print_box(details, style="info")

        if restaurant.cash < cost:
            show_error("Trésorerie insuffisante pour cette campagne.")
            pause()
            return

        if confirm(f"Lancer la campagne {name} pour {cost}€ ?"):
            if "marketing_campaigns" not in decisions:
                decisions["marketing_campaigns"] = []

            decisions["marketing_campaigns"].append(
                {"type": name, "cost": cost, "impact": impact}
            )

            show_success(f"Campagne {name} programmée !")
            pause()

    # def _financial_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
    #     """Décisions financières."""
    #     menu = MenuHandler("FINANCE")
    #     menu.add_option(
    #         "💳 Demander un prêt bancaire",
    #         lambda: self._request_loan(restaurant, decisions),
    #     ).add_option(
    #         "💰 Rembourser un emprunt",
    #         lambda: self._repay_loan(restaurant, decisions),
    #     ).add_option(
    #         "📈 Placer des excédents",
    #         lambda: self._invest_surplus(restaurant, decisions),
    #     ).add_option(
    #         "📊 Analyser la rentabilité",
    #         lambda: self._analyze_profitability(restaurant),
    #     ).add_option(
    #         "💸 Gérer la trésorerie",
    #         lambda: self._manage_cash_flow(restaurant, decisions),
    #     )

    #     menu.show()

    def _show_reports(self, restaurant: Restaurant) -> None:
        """Affichage des rapports financiers."""
        menu = MenuHandler("RAPPORTS & ANALYSES")
        menu.add_option(
            "📊 Compte de résultat",
            lambda: self._show_profit_loss_statement(restaurant),
        ).add_option(
            "💰 Tableau de flux de trésorerie",
            lambda: self._show_cash_flow_statement(restaurant),
        ).add_option(
            "📋 Bilan comptable",
            lambda: self._show_balance_sheet(restaurant),
        ).add_option(
            "📈 Analyse des KPIs",
            lambda: self._show_kpi_analysis(restaurant),
        ).add_option(
            "📉 Évolution des performances",
            lambda: self._show_performance_evolution(restaurant),
        )

        menu.show()

    def _show_profit_loss_statement(self, restaurant: Restaurant) -> None:
        """Affiche le compte de résultat."""

        ledger = Ledger()
        self.financial_reports.show_profit_loss_statement(restaurant, ledger)
        pause()

    def _show_cash_flow_statement(self, restaurant: Restaurant) -> None:
        """Affiche le tableau de flux de trésorerie."""
        from game_engine.domain.finance.ledger import Ledger

        ledger = Ledger()
        self.financial_reports.show_cash_flow_statement(restaurant, ledger)
        pause()

    def _show_balance_sheet(self, restaurant: Restaurant) -> None:
        """Affiche le bilan comptable."""
        from game_engine.domain.finance.ledger import Ledger

        ledger = Ledger()
        self.financial_reports.show_balance_sheet(restaurant, ledger)
        pause()

    def _show_kpi_analysis(self, restaurant: Restaurant) -> None:
        """Affiche l'analyse des KPIs."""
        show_info("Analyse des KPIs - En développement")
        pause()

    def _show_performance_evolution(self, restaurant: Restaurant) -> None:
        """Affiche l'évolution des performances."""
        show_info("Évolution des performances - En développement")
        pause()

    def _validate_decisions(self, restaurant: Restaurant, decisions: dict) -> bool:
        """Validation finale des décisions."""
        if not decisions:
            return confirm("Aucune décision prise. Passer au tour suivant ?")

        # Résumé des décisions
        summary = ["RÉSUMÉ DES DÉCISIONS:"]

        if "price_changes" in decisions:
            summary.append("💰 Modifications de prix:")
            for recipe, price in decisions["price_changes"].items():
                summary.append(f"  • {recipe}: {price:.2f}€")

        if "recruitments" in decisions:
            summary.append("👤 Recrutements:")
            for recruit in decisions["recruitments"]:
                summary.append(
                    f"  • {recruit['position'].value} - {recruit['salary']:.0f}€/mois"
                )

        if "marketing_campaigns" in decisions:
            summary.append("📢 Campagnes marketing:")
            for campaign in decisions["marketing_campaigns"]:
                summary.append(f"  • {campaign['type']} - {campaign['cost']}€")

        print_box(summary, "VALIDATION", "warning")

        return confirm("Valider ces décisions et passer au tour suivant ?")

    # Méthodes utilitaires (implémentation complète)
    def _add_recipes(
        self, restaurant: Restaurant, available_recipes: dict, decisions: dict
    ) -> None:
        """Ajoute des recettes disponibles au menu actif avec prix TTC."""
        clear_screen()

        # Recettes non actives
        inactive = [
            r
            for r in available_recipes.values()
            if r.id not in restaurant.active_recipes
        ]
        if not inactive:
            show_info("Toutes les recettes sont déjà actives.")
            pause()
            return

        # Choix multiple simple (itératif)
        while True:
            options = [f"{r.name} ({r.id})" for r in inactive]
            choice = show_menu("Ajouter un plat", options)
            if choice == 0:
                break

            recipe = inactive[choice - 1]

            # Proposer prix par défaut selon coût + cible marge
            breakdown = self.cost_calculator.calculate_recipe_cost(recipe)
            cost_per_portion = breakdown.total_cost_with_labor / recipe.portions

            target_margin_pct = {
                "fast": Decimal("0.70"),
                "classic": Decimal("0.75"),
                "brasserie": Decimal("0.72"),
                "gastronomique": Decimal("0.80"),
            }.get(restaurant.type.value, Decimal("0.70"))

            # TVA simplifiée 10%
            vat = Decimal("0.10")
            default_price_ht = cost_per_portion / (Decimal("1.0") - target_margin_pct)
            default_price_ttc = (default_price_ht * (Decimal("1.0") + vat)).quantize(
                Decimal("0.10")
            )

            price_ttc = get_input(
                f"Prix TTC pour {recipe.name} (coût/portion ~{cost_per_portion:.2f}€)",
                Decimal,
                min_val=Decimal("1.0"),
                max_val=Decimal("100.0"),
                default=default_price_ttc,
            )
            if not price_ttc:
                continue

            restaurant.set_recipe_price(recipe.id, price_ttc)
            restaurant.activate_recipe(recipe.id)

            # Enregistrer décision
            decisions.setdefault("added_recipes", []).append(
                {
                    "recipe_id": recipe.id,
                    "price_ttc": price_ttc,
                }
            )

            # Retirer de la liste inactive
            inactive = [r for r in inactive if r.id != recipe.id]
            if not inactive or not confirm("Ajouter un autre plat ?"):
                break

    def _remove_recipes(self, restaurant: Restaurant, decisions: dict) -> None:
        """Retire des recettes du menu actif."""
        active = restaurant.get_active_menu()
        if not active:
            show_info("Aucune recette active.")
            pause()
            return

        options = [f"{rid} - {price:.2f}€" for rid, price in active.items()]
        choice = show_menu("Retirer un plat", options)
        if choice == 0:
            return

        selected_id = list(active.keys())[choice - 1]
        restaurant.deactivate_recipe(selected_id)
        decisions.setdefault("removed_recipes", []).append(selected_id)
        show_success(f"Recette {selected_id} désactivée")
        pause()

    def _analyze_recipe_profitability(
        self, restaurant: Restaurant, available_recipes: dict
    ) -> None:
        """Analyse marge et recommandations par recette active."""
        active = restaurant.get_active_menu()
        if not active:
            show_info("Aucune recette active.")
            pause()
            return

        lines = ["📊 RENTABILITÉ PAR PLAT:", ""]
        for rid, price_ttc in active.items():
            if rid not in available_recipes:
                continue
            recipe = available_recipes[rid]
            # TODO: passer les lots de stock réels si disponibles
            analysis = self.cost_calculator.calculate_margin_analysis(
                recipe, price_ttc, vat_rate=Decimal("0.10")
            )
            margin_pct = analysis["margin_percentage"] * 100
            lines.append(
                f"• {recipe.name}: prix {price_ttc:.2f}€, marge {margin_pct:.1f}% (coût/portion {analysis['cost_per_portion']:.2f}€)"
            )

            # Cibles par type
            targets = {"fast": 70, "classic": 75, "brasserie": 72, "gastronomique": 80}
            target = targets.get(restaurant.type.value, 70)
            if margin_pct < target:
                # Proposer nouvelle tarification HT -> TTC
                new_price_ht = analysis["cost_per_portion"] / (
                    Decimal("1.0") - Decimal(str(target / 100))
                )
                new_price_ttc = new_price_ht * Decimal("1.10")
                lines.append(
                    f"   ↳ Suggestion: augmenter à ~{new_price_ttc:.2f}€ pour atteindre {target}%"
                )

        print_box(lines, "ANALYSE RENTABILITÉ", "info")
        pause()

    def _create_daily_menu(self, restaurant: Restaurant, decisions: dict) -> None:
        """Crée un menu du jour (sous-ensemble des recettes actives) avec prix spéciaux."""
        active = restaurant.get_active_menu()
        if not active:
            show_info("Aucune recette active.")
            pause()
            return

        options = [f"{rid} - {price:.2f}€" for rid, price in active.items()]
        selection: list[str] = []

        while True:
            choice = show_menu("Ajouter au menu du jour", options)
            if choice == 0:
                break
            rid = list(active.keys())[choice - 1]
            if rid not in selection:
                selection.append(rid)
            if not confirm("Ajouter un autre plat au menu du jour ?"):
                break

        if not selection:
            show_info("Aucune sélection pour le menu du jour.")
            pause()
            return

        # Prix spéciaux (remise % simple)
        discount = get_input(
            "Remise % (ex: 20 pour -20%)",
            Decimal,
            min_val=Decimal("0"),
            max_val=Decimal("90"),
            default=Decimal("20"),
        )
        specials = {}
        for rid in selection:
            base = active[rid]
            specials[rid] = (
                base * (Decimal("1.0") - discount / Decimal("100"))
            ).quantize(Decimal("0.10"))

        decisions["daily_menu"] = specials
        show_success("Menu du jour créé pour 1 tour")
        pause()

    def _show_sales_history(self, restaurant: Restaurant) -> None:
        """Affiche l'historique des ventes par recette (si disponible)."""
        history = getattr(restaurant, "sales_history", None)
        if not history:
            show_info("Aucun historique de ventes disponible.")
            pause()
            return

        lines = ["📈 HISTORIQUE DES VENTES:", ""]
        for rid, records in history.items():  # records: List[Tuple[turn, qty]]
            total = sum(q for _, q in records)
            lines.append(f"• {rid}: total {total} portions")
        print_box(lines, "VENTES", "info")
        pause()

    def _fire_employee(self, restaurant: Restaurant, decisions: dict) -> None:
        show_info("Licenciement - En développement")
        pause()

    def _train_employees(self, restaurant: Restaurant, decisions: dict) -> None:
        show_info("Formation - En développement")
        pause()

    def _adjust_schedules(self, restaurant: Restaurant, decisions: dict) -> None:
        show_info("Horaires - En développement")
        pause()

    def _negotiate_salaries(self, restaurant: Restaurant, decisions: dict) -> None:
        show_info("Négociation salaires - En développement")
        pause()

    def _analyze_productivity(self, restaurant: Restaurant) -> None:
        show_info("Analyse productivité - En développement")
        pause()

    def _loyalty_program(self, restaurant: Restaurant, decisions: dict) -> None:
        show_info("Programme fidélité - En développement")
        pause()

    def _special_event(self, restaurant: Restaurant, decisions: dict) -> None:
        show_info("Événement spécial - En développement")
        pause()

    # def _investment_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
    #     show_info("Investissements - En développement")
    #     pause()

    def show_random_events(self, event_manager: RandomEventManager) -> None:
        """Affiche les événements aléatoires actifs."""
        events_summary = event_manager.get_events_summary()

        if not events_summary["active_events"]:
            show_info("📅 Aucun événement spécial en cours")
            return

        clear_screen()
        show_info("🎲 ÉVÉNEMENTS EN COURS")

        for event in events_summary["active_events"]:
            print(f"\n{event['title']}")
            print(f"   📝 {event['description']}")
            print(f"   📊 Catégorie: {event['category']}")
            print(f"   ⏱️ Reste: {event['remaining_turns']} tour(s)")

        # Afficher les effets cumulés
        effects = event_manager.get_current_effects()

        print("\n📈 EFFETS CUMULÉS:")
        if effects["demand_multiplier"] != 1.0:
            change = (effects["demand_multiplier"] - 1) * 100
            print(f"   Demande globale: {change:+.0f}%")

        if effects["price_sensitivity"] != 1.0:
            change = (effects["price_sensitivity"] - 1) * 100
            print(f"   Sensibilité aux prix: {change:+.0f}%")

        if effects["quality_importance"] != 1.0:
            change = (effects["quality_importance"] - 1) * 100
            print(f"   Importance de la qualité: {change:+.0f}%")

        if effects["segment_effects"]:
            print("   Effets par segment:")
            for segment, multiplier in effects["segment_effects"].items():
                change = (multiplier - 1) * 100
                print(f"     • {segment}: {change:+.0f}%")

        pause()
