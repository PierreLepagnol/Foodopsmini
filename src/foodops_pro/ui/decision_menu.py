"""Menu de décisions enrichi pour FoodOps Pro."""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from decimal import Decimal

from ..domain.restaurant import Restaurant
from ..domain.employee import Employee, EmployeePosition, EmployeeContract
from ..domain.random_events import RandomEventManager
from ..domain.stock import StockManager
from ..domain.supplier import Supplier
from ..core.costing import RecipeCostCalculator
from ..core.procurement import ProcurementPlanner, ReceivingService, POLine
from .console_ui import ConsoleUI
from .financial_reports import FinancialReports


class PlayerRole(str, Enum):
    """Rôles possibles pour les participants."""

    GENERAL_MANAGER = "Direction générale"
    PRODUCTION = "Responsable production"
    HR = "Responsable RH"
    PURCHASING = "Responsable achats"
    MARKETING = "Responsable marketing"
    FINANCE = "Directeur financier"
    ANALYST = "Analyste"


ROLE_MENU_OPTIONS = {
    PlayerRole.GENERAL_MANAGER: {1, 2, 3, 4, 5, 6, 7, 8, 9},
    PlayerRole.PRODUCTION: {2, 9},
    PlayerRole.HR: {3, 9},
    PlayerRole.PURCHASING: {4, 9},
    PlayerRole.MARKETING: {5, 9},
    PlayerRole.FINANCE: {7, 9},
    PlayerRole.ANALYST: {8, 9},
}


class DecisionMenu:
    """Menu de décisions stratégiques pour les joueurs."""

    def __init__(self, ui: ConsoleUI, cost_calculator: RecipeCostCalculator):
        self.ui = ui
        self.cost_calculator = cost_calculator
        self.financial_reports = FinancialReports(ui)
        # Catalogues et paramètres (injectés depuis le jeu/CLI)
        self._suppliers_catalog: Dict[str, List[Dict]] = {}
        self._suppliers_map: Dict[str, Supplier] = {}
        self._available_recipes_cache: Dict[str, any] = {}
        self._admin_settings = None
        self._prefill_purchase: Optional[Dict] = None

    def set_suppliers_catalog(self, suppliers_catalog: Dict[str, List[Dict]]):
        """Injection de la mercuriale (offres par ingrédient)."""
        self._suppliers_catalog = suppliers_catalog or {}

    def set_suppliers_map(self, suppliers: Dict[str, Supplier]):
        """Injection de la table fournisseurs (id->Supplier)."""
        self._suppliers_map = suppliers or {}

    def set_admin_settings(self, settings):
        """Injection des paramètres admin (auto_* et confirmations)."""
        self._admin_settings = settings

    def cache_available_recipes(self, recipes: Dict[str, any]) -> None:
        self._available_recipes_cache = recipes or {}

    def _select_role(self) -> PlayerRole:
        """Permet au participant de choisir son rôle."""
        options = [role.value for role in PlayerRole]
        choice = self.ui.show_menu("Sélectionnez votre rôle", options, allow_back=False)
        return list(PlayerRole)[choice - 1]

    def show_decision_menu(
        self,
        restaurant: Restaurant,
        turn: int,
        available_recipes: Dict,
        available_employees: List = None,
        role: Optional[PlayerRole] = None,
    ) -> Dict[str, any]:
        """Affiche le menu de décisions principal et retourne les choix du joueur."""

        role = role or self._select_role()
        allowed_options = ROLE_MENU_OPTIONS.get(role, {9})

        decisions: Dict[str, any] = {}

        while True:
            self.ui.clear_screen()
            self._show_restaurant_status(restaurant, turn)

            all_options = [
                "📋 Menu & Pricing",
                "👨‍🍳 Production & Mise en place",
                "👥 Ressources Humaines",
                "🛒 Achats & Stocks",
                "📈 Marketing & Commercial",
                "🏗️ Investissements",
                "💰 Finance & Comptabilité",
                "📊 Rapports & Analyses",
                "✅ Valider et passer au tour suivant",
            ]

            display_options: List[str] = []
            option_map: List[int] = []
            for idx, opt in enumerate(all_options, 1):
                if idx in allowed_options:
                    display_options.append(opt)
                    option_map.append(idx)

            choice = self.ui.show_menu(
                f"DÉCISIONS - TOUR {turn} - {restaurant.name}",
                display_options,
                allow_back=False,
            )

            selected = option_map[choice - 1]

            if selected == 1:
                self._menu_pricing_decisions(restaurant, available_recipes, decisions)
            elif selected == 2:
                self._production_decisions(restaurant)
            elif selected == 3:
                self._hr_decisions(restaurant, available_employees, decisions)
            elif selected == 4:
                self._purchasing_decisions(restaurant, decisions)
            elif selected == 5:
                self._marketing_decisions(restaurant, decisions)
            elif selected == 6:
                self._investment_decisions(restaurant, decisions)
            elif selected == 7:
                self._finance_decisions(restaurant, decisions)
            elif selected == 8:
                self._reports_decisions(restaurant, decisions)
            elif selected == 9:
                if self._validate_decisions(restaurant, decisions):
                    break
            else:
                continue
        return decisions
    def _production_decisions(self, restaurant,):
        """Saisie du plan de production manuel par recettes (taille, quantité, qualité)."""
        self.ui.clear_screen()
        self.ui.print_box([
            "Préparez votre mise en place.",
            "- La taille L consomme 1.5x d'ingrédients",
            "- La qualité influencera la satisfaction client",
            "- Durée: non prise en compte pour l'instant (prochaine étape: personnel)",
            "- Les unités produites sont valables 1 tour (sinon perdues)",
        ], title="👨‍🍳 PRODUCTION & MISE EN PLACE", style="info")
        # Afficher carte active
        menu = getattr(restaurant, "menu", {})
        active = [rid for rid, price in menu.items() if price is not None]
        if not active:
            self.ui.show_error("Aucune recette active. Allez dans Menu & Pricing pour activer des recettes.")
            self.ui.pause()
            return
        draft = dict(getattr(restaurant, "production_plan_draft", {}) or {})
        while True:
            options = [f"{i+1}. {rid} — plan actuel: {draft.get(rid, {}).get('qty', 0)} portions ({draft.get(rid, {}).get('size', 'S')}, Q={draft.get(rid, {}).get('quality', '1.0')})" for i, rid in enumerate(active)]
            options.append("Valider")
            choice = self.ui.show_menu("Sélectionnez une recette à planifier", options)
            if choice == 0:
                return
            if choice == len(options):
                restaurant.production_plan_draft = draft
                self.ui.show_success("Plan de production enregistré pour ce tour.")
                self.ui.pause()
                return
            rid = active[choice-1]
            size = self.ui.show_menu("Choisir taille de portion", ["S (standard)", "L (1.5x ingrédients)"])
            size_val = "S" if size == 1 else "L"
            qty = self.ui.ask_int("Quantité de portions à produire", min_val=0, default=int(draft.get(rid, {}).get("qty", 0) or 0))
            quality = self.ui.get_input("Qualité (0.5 à 1.5)", float, min_val=0.5, max_val=1.5, default=float(draft.get(rid, {}).get("quality", 1.0)))
            draft[rid] = {"size": size_val, "qty": qty, "quality": quality}

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

        self.ui.print_box(status, f"STATUT - TOUR {turn}", style)

    def _menu_pricing_decisions(
        self, restaurant: Restaurant, available_recipes: Dict, decisions: Dict
    ) -> None:
        """Gestion du menu et des prix."""
        while True:
            self.ui.clear_screen()

            submenu_options = [
                "💰 Modifier les prix",
                "➕ Ajouter des plats au menu",
                "➖ Retirer des plats du menu",
                "📊 Analyser la rentabilité par plat",
                "🍽️ Créer un menu du jour",
                "📈 Voir l'historique des ventes",
            ]

            choice = self.ui.show_menu("MENU & PRICING", submenu_options)

            if choice == 0:
                break
            elif choice == 1:
                self._modify_prices(restaurant, decisions)
            elif choice == 2:
                self._add_recipes(restaurant, available_recipes, decisions)
            elif choice == 3:
                self._remove_recipes(restaurant, decisions)
            elif choice == 4:
                self._analyze_recipe_profitability(restaurant, available_recipes)
            elif choice == 5:
                self._create_daily_menu(restaurant, decisions)
            elif choice == 6:
                self._show_sales_history(restaurant)

    def _modify_prices(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Modification des prix de vente."""
        active_menu = restaurant.get_active_menu()

        if not active_menu:
            self.ui.show_error("Aucune recette active dans le menu.")
            self.ui.pause()
            return

        self.ui.clear_screen()

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

        self.ui.print_box(menu_analysis, style="info")

        # Sélection de la recette à modifier
        recipe_list = list(active_menu.keys())
        recipe_choice = self.ui.show_menu(
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
        new_price = self.ui.get_input(
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

            self.ui.show_success(impact_msg)
            self.ui.pause()

    def _hr_decisions(
        self, restaurant: Restaurant, available_employees: List, decisions: Dict
    ) -> None:
        """Gestion des ressources humaines."""
        while True:
            self.ui.clear_screen()

            # Affichage de l'équipe actuelle
            team_info = [f"ÉQUIPE ACTUELLE ({len(restaurant.employees)} employés):"]

            total_cost = Decimal("0")
            for emp in restaurant.employees:
                monthly_cost = emp.salary_gross_monthly * Decimal(
                    "1.42"
                )  # Avec charges
                total_cost += monthly_cost
                team_info.append(
                    f"• {emp.name} ({emp.position.value}) - "
                    f"{emp.contract.value} - {monthly_cost:.0f}€/mois"
                )

            team_info.append(f"")
            team_info.append(f"Coût total équipe: {total_cost:.0f}€/mois")

            self.ui.print_box(team_info, style="info")

            submenu_options = [
                "👤 Recruter un employé",
                "❌ Licencier un employé",
                "📚 Former le personnel",
                "⏰ Ajuster les horaires",
                "💰 Négocier les salaires",
                "📊 Analyser la productivité",
            ]

            choice = self.ui.show_menu("RESSOURCES HUMAINES", submenu_options)

            if choice == 0:
                break
            elif choice == 1:
                self._recruit_employee(restaurant, decisions)
            elif choice == 2:
                self._fire_employee(restaurant, decisions)
            elif choice == 3:
                self._train_employees(restaurant, decisions)
            elif choice == 4:
                self._adjust_schedules(restaurant, decisions)
            elif choice == 5:
                self._negotiate_salaries(restaurant, decisions)
            elif choice == 6:
                self._analyze_productivity(restaurant)

    def _recruit_employee(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Recrutement d'un nouvel employé."""
        if len(restaurant.employees) >= 10:  # Limite arbitraire
            self.ui.show_error("Équipe complète (maximum 10 employés).")
            self.ui.pause()
            return

        # Choix du poste
        positions = [pos.value for pos in EmployeePosition]
        position_choice = self.ui.show_menu("Quel poste recruter ?", positions)

        if position_choice == 0:
            return

        selected_position = list(EmployeePosition)[position_choice - 1]

        # Choix du contrat
        contracts = [cont.value for cont in EmployeeContract]
        contract_choice = self.ui.show_menu("Type de contrat ?", contracts)

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

        salary = self.ui.get_input(
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
                if not self.ui.confirm(
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

            self.ui.show_success(
                f"Recrutement programmé: {selected_position.value} "
                f"en {selected_contract.value} à {salary:.0f}€/mois"
            )
            self.ui.pause()

    def _purchasing_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Gestion des achats et stocks avancée."""
        # État minimal requis pour le module Achats & Stocks
        if not hasattr(restaurant, "stock_manager"):
            restaurant.stock_manager = StockManager()
        if not hasattr(restaurant, "sales_forecast"):
            restaurant.sales_forecast = {}
        if not hasattr(restaurant, "pending_po_lines"):
            restaurant.pending_po_lines = []

        while True:
            self.ui.clear_screen()

            submenu_options = [
                "📋 Prévision & Besoins",
                "🛒 Composer ma commande (manuel)",
                "📚 Catalogues fournisseurs",
                "🤖 Proposer une commande (auto, revue ligne)",
                "🏷️ Commander par gamme (fast/bistro/gastro)",
                "📥 Réception de commandes",
                "📦 État des stocks & alertes",
                "🔙 Retour",
            ]

            choice = self.ui.show_menu("ACHATS & STOCKS", submenu_options)

            if choice == 1:
                self._forecast_and_requirements(restaurant)
            elif choice == 2:
                self._compose_manual_order(restaurant)
            elif choice == 3:
                self._supplier_catalog_interface(restaurant)
            elif choice == 4:
                self._review_auto_order(restaurant)
            elif choice == 5:
                self._auto_order_by_gamme(restaurant)
            elif choice == 6:
                self._receiving_interface(restaurant)
            elif choice == 7:
                self._stock_management_interface(restaurant)
            elif choice == 8:
                break

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
        self.ui.clear_screen()
        active = restaurant.get_active_menu()
        if not active:
            self.ui.show_info("Aucune recette active pour établir une prévision.")
            self.ui.pause()
            return

        print("📋 PRÉVISION DES VENTES (prochain tour):")
        auto = getattr(self._admin_settings, "auto_forecast_enabled", False)
        for rid in active.keys():
            cur = int(restaurant.sales_forecast.get(rid, 0))
            default_qty = cur if cur else (20 if auto else 0)
            try:
                qty = self.ui.ask_int(
                    f"  Portions prévues pour {rid} (actuel {cur}): ",
                    min_val=0,
                    max_val=1000,
                    default=default_qty,
                )
                restaurant.sales_forecast[rid] = qty
            except Exception:
                continue

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
        self.ui.print_box(lines, "BESOINS", "info")
        self.ui.pause()

    def _compose_manual_order(self, restaurant: Restaurant) -> None:
        """Mode MANUEL en 3 étapes: ingrédient → fournisseur → gamme & quantité."""
        planner = ProcurementPlanner()
        active_recipes = [self._available_recipes_cache[rid] for rid in getattr(restaurant, "active_recipes", []) if hasattr(self, "_available_recipes_cache") and rid in self._available_recipes_cache]
        requirements = planner.compute_requirements(active_recipes, getattr(restaurant, "sales_forecast", {}), restaurant.stock_manager)

        if not requirements:
            self.ui.show_info("Aucun besoin net détecté. Vous pouvez tout de même commander manuellement via le catalogue.")
            cat_keys = sorted(self._suppliers_catalog.keys()) if hasattr(self, "_suppliers_catalog") and self._suppliers_catalog else []
            if cat_keys:
                requirements = {ing: Decimal('0') for ing in cat_keys}
            else:
                self.ui.show_error("Aucun catalogue fournisseur disponible. Impossible de composer une commande.")
                self.ui.pause()
                return

        pending: List[POLine] = getattr(restaurant, "pending_po_lines", []).copy()

        # Si un pré-remplissage existe depuis le catalogue, traiter d’abord
        if getattr(self, "_prefill_purchase", None):
            pre = self._prefill_purchase
            self._prefill_purchase = None
            ing_id = pre.get('ingredient_id')
            supplier_id = pre.get('supplier_id')
            ql = pre.get('quality_level')
            need = requirements.get(ing_id, Decimal('0'))
            created = self._select_gamme_and_quantity(restaurant, ing_id, supplier_id, need, preselected_quality_level=ql)
            if created is not None:
                pending.append(created)

        while True:
            # Étape 1 — Choisir l’ingrédient
            ing_id = self._select_ingredient_from_requirements(restaurant, requirements)
            if ing_id is None:
                break
            need = requirements.get(ing_id, Decimal('0'))

            # Étape 2 & 3 — Boucle pour permettre split multi-fournisseurs/gammes
            while True:
                supplier_id = self._select_supplier_for_ingredient(ing_id)
                if supplier_id is None:
                    break

                created = self._select_gamme_and_quantity(restaurant, ing_id, supplier_id, need)
                if created is not None:
                    pending.append(created)

                # Ajouter une autre ligne pour CE MÊME ingrédient ?
                if not self.ui.confirm("Ajouter une autre ligne pour ce même ingrédient ?"):

                    break

            # Passer à un autre ingrédient ?
            if not self.ui.confirm("Passer à un autre ingrédient ?"):
                break

        if pending:
            restaurant.pending_po_lines = pending
            self.ui.show_success(f"✅ {len(pending)} lignes de commande enregistrées (à réceptionner).")
        else:
            self.ui.show_info("Aucune ligne créée.")
        self.ui.pause()

    def _select_ingredient_from_requirements(self, restaurant: Restaurant, requirements: Dict[str, Decimal]) -> Optional[str]:
        """Affiche la liste des ingrédients avec besoin net, stock dispo et alerte DLC."""
        # Construire options triées par besoin décroissant
        items = sorted(requirements.items(), key=lambda kv: kv[1], reverse=True)
        options = []
        index_to_ing: List[str] = []
        expiring = restaurant.stock_manager.get_expiring_lots(days=3)
        expiring_set = {lt.ingredient_id for lt in expiring}
        for ing_id, need in items:
            stock = restaurant.stock_manager.get_available_quantity(ing_id)
            unit = getattr(self.cost_calculator.ingredients.get(ing_id, None), 'unit', '') if hasattr(self.cost_calculator, 'ingredients') else ''
            alert = " 🚨 DLC" if ing_id in expiring_set else ""
            options.append(f"{ing_id} — Besoin net: {need} | Stock: {stock} {unit}{alert}")
            index_to_ing.append(ing_id)
        choice = self.ui.show_menu("Étape 1 — Choisir l’ingrédient", options)
        if choice == 0:
            return None
        return index_to_ing[choice - 1]

    def _select_supplier_for_ingredient(self, ing_id: str) -> Optional[str]:
        """Affiche les fournisseurs qui proposent cet ingrédient (résumé clair)."""
        while True:
            offers = list(self._suppliers_catalog.get(ing_id, [])) if hasattr(self, "_suppliers_catalog") else []
            if not offers:
                # Fallback minimal
                if ing_id in getattr(self.cost_calculator, 'ingredients', {}):
                    ing = self.cost_calculator.ingredients[ing_id]
                    offers = [{
                        'supplier_id': 'metro_pro', 'quality_level': 2,
                        'pack_size': Decimal('1'), 'pack_unit': getattr(ing, 'unit', ''),
                        'unit_price_ht': ing.cost_ht, 'vat_rate': ing.vat_rate,
                        'moq_qty': Decimal('0'), 'moq_value': Decimal('0'),
                        'lead_time_days': 1, 'reliability': Decimal('0.95')
                    }]
                    self.ui.show_info("Une seule offre trouvée (catalogue minimal). Ajoutez supplier_prices.csv pour plus d’options.")
                else:
                    self.ui.show_error(f"Aucune offre disponible pour {ing_id}.")
                    return None

            # Regrouper par fournisseur
            by_supplier: Dict[str, List[Dict]] = {}
            for o in offers:
                by_supplier.setdefault(o['supplier_id'], []).append(o)
            supplier_ids = sorted(by_supplier.keys())

            options = ["📚 Voir le catalogue pour cet ingrédient"]
            for sid in supplier_ids:
                sup = getattr(self, "_suppliers_map", {}).get(sid)
                name = getattr(sup, 'name', sid)
                lead = getattr(sup, 'lead_time_days', None)
                if lead is None:
                    # fallback depuis offre
                    lead_vals = [oo.get('lead_time_days') for oo in by_supplier[sid] if oo.get('lead_time_days') is not None]
                    lead = min(lead_vals) if lead_vals else None
                rel = getattr(sup, 'reliability', None)
                if rel is None:
                    rel_vals = [oo.get('reliability') for oo in by_supplier[sid] if oo.get('reliability') is not None]
                    rel = max(rel_vals) if rel_vals else None
                moq_values = [oo.get('moq_value', Decimal('0')) for oo in by_supplier[sid]]
                min_moq = None
                if moq_values:
                    try:
                        filtered = [mv for mv in moq_values if mv is not None]
                        min_moq = min(filtered) if filtered else None
                    except Exception:
                        min_moq = None
                moq_str = f"MOQ valeur: {min_moq:.2f}€" if (min_moq is not None and min_moq > 0) else "MOQ: Aucun"
                lead_str = f"Délai (jours): {lead}" if lead is not None else "Délai (jours): ?"
                rel_str = f"Fiabilité: {rel}" if rel is not None else "Fiabilité: ?"
                options.append(f"{name} | {lead_str} | {rel_str} | {moq_str}")

            ch = self.ui.show_menu(f"Étape 2 — Choisir le fournisseur pour {ing_id}", options)
            if ch == 0:
                return None
            if ch == 1:
                # Ouvrir le catalogue filtré puis reboucler
                self._catalog_by_ingredient(ing_id)
                continue
            return supplier_ids[ch - 2]

    def _select_gamme_and_quantity(self, restaurant: Restaurant, ing_id: str, supplier_id: str, need: Decimal, preselected_quality_level: Optional[int] = None) -> Optional[POLine]:
        """Affiche les gammes disponibles pour le fournisseur et saisit la quantité."""
        from datetime import date, timedelta

        all_offers = list(self._suppliers_catalog.get(ing_id, [])) if hasattr(self, "_suppliers_catalog") else []
        offers = [o for o in all_offers if o.get('supplier_id') == supplier_id]
        if not offers:
            offers = all_offers  # fallback
        if not offers:
            self.ui.show_error("Aucune offre pour cet ingrédient.")
            return None
        if len(offers) == 1:
            self.ui.show_info("Note: une seule offre disponible pour cet ingrédient chez ce fournisseur.")

        # Si préselection gamme, filtrer
        if preselected_quality_level is not None:
            filtered = [o for o in offers if o.get('quality_level') == preselected_quality_level]
            if len(filtered) == 1:
                selected_offer = filtered[0]
            else:
                selected_offer = None
        else:
            selected_offer = None

        # Libellés complets
        def fmt_offer(o: Dict) -> str:
            parts = [
                f"Gamme {o.get('quality_level', '?')}",
                f"Pack: {o.get('pack_size')} {o.get('pack_unit','')}",
                f"Prix HT: {o.get('unit_price_ht'):.2f}€",
                f"TVA: {o.get('vat_rate'):.1%}"
            ]
            if o.get('lead_time_days') is not None:
                parts.append(f"Délai (jours): {o.get('lead_time_days')}")
            if o.get('reliability') is not None:
                parts.append(f"Fiabilité: {o.get('reliability')}")
            if o.get('typical_shelf_life_days') is not None:
                parts.append(f"DLC typique: {o.get('typical_shelf_life_days')}j")
            moq_bits = []
            if o.get('moq_qty'):
                moq_bits.append(f"Qté {o['moq_qty']}")
            if o.get('moq_value'):
                moq_bits.append(f"Valeur {o['moq_value']:.2f}€")
            if moq_bits:
                parts.append(f"MOQ: {' / '.join(moq_bits)}")
            return " | ".join(parts)

        if selected_offer is None:
            options = [fmt_offer(o) for o in offers]
            ch = self.ui.show_menu(f"Étape 3 — Choisir la gamme & quantité ({ing_id})", options)
            if ch == 0:
                return None
            o = offers[ch - 1]
        else:
            o = selected_offer

        # Rappels de règles
        self.ui.show_info("Aide: Arrondi au pack (vers le haut). Sur-stock autorisé. Les MOQ peuvent ajuster la quantité/valeur.")
        qty_wanted = self.ui.get_input(
            f"Quantité souhaitée (besoin net ≈ {need})",
            Decimal, min_val=Decimal('0'), default=need
        )
        if qty_wanted is None:
            return None

        # Arrondi pack vers le haut
        packs = (qty_wanted / o['pack_size']).to_integral_value(rounding='ROUND_CEILING')
        qty_final = packs * o['pack_size']

        # MOQ quantité & valeur
        if o.get('moq_qty', Decimal('0')) > 0 and qty_final < o['moq_qty']:
            self.ui.show_info(f"MOQ quantité {o['moq_qty']} appliqué → ajustement")
            qty_final = o['moq_qty']
        order_value = qty_final * o['unit_price_ht']
        if o.get('moq_value', Decimal('0')) > 0 and order_value < o['moq_value']:
            deficit_value = o['moq_value'] - order_value
            extra_units = (deficit_value / o['unit_price_ht']).to_integral_value(rounding='ROUND_CEILING')
            qty_final += extra_units
            order_value = qty_final * o['unit_price_ht']

        # Coût TTC & ETA
        cost_ttc = order_value * (Decimal('1') + o['vat_rate'])
        eta_days = o.get('lead_time_days', None)
        eta_str = f"Date estimée d’arrivée: {(date.today() + timedelta(days=eta_days))}" if eta_days is not None else "Date estimée d’arrivée: inconnue"
        if need and qty_final > need:
            self.ui.show_info("Note: sur-stock autorisé — vous commandez au-delà du besoin net.")

        self.ui.show_info(f"Synthèse: {qty_final} @ {o['unit_price_ht']:.2f}€ HT → HT={order_value:.2f}€, TTC={cost_ttc:.2f}€. {eta_str}")

        line = POLine(
            ingredient_id=ing_id,
            quantity=qty_final,
            unit_price_ht=o['unit_price_ht'],
            vat_rate=o['vat_rate'],
            supplier_id=o['supplier_id'],
            pack_size=o['pack_size'],
            pack_unit=o.get('pack_unit'),
            quality_level=o.get('quality_level'),
            eta_days=o.get('lead_time_days'),
        )
        line.compute_amounts()
        self.ui.show_success("Ligne ajoutée à la commande en attente.")
        return line
    def _supplier_catalog_interface(self, restaurant: Restaurant) -> None:
        """Catalogue fournisseurs: Par ingrédient ou Par fournisseur (consultation)."""
        if not hasattr(self, "_suppliers_catalog") or not self._suppliers_catalog:
            self.ui.show_info("Aucun catalogue fournisseur chargé. Ajoutez supplier_prices.csv pour plus d’options.")
            self.ui.pause()
            return
        while True:
            ch = self.ui.show_menu("📚 Catalogues fournisseurs", [
                "Par ingrédient",
                "Par fournisseur",
                "Retour"
            ])
            if ch == 0 or ch == 3:
                break
            if ch == 1:
                self._catalog_by_ingredient()
            elif ch == 2:
                self._catalog_by_supplier()

    def _catalog_by_ingredient(self, preselected_ing: Optional[str] = None) -> None:
        # Choisir un ingrédient
        if preselected_ing is None:
            ingredients = sorted(self._suppliers_catalog.keys())
            ch = self.ui.show_menu("Choisir un ingrédient", ingredients)
            if ch == 0:
                return
            ing_id = ingredients[ch - 1]
        else:
            ing_id = preselected_ing
        offers = self._suppliers_catalog.get(ing_id, [])
        # Filtre rapide: prix, délai, fiabilité, gamme
        filters = ["Prix (asc)", "Délai (asc)", "Fiabilité (desc)", "Gamme (asc)", "Aucun filtre"]
        fh = self.ui.show_menu("Filtrer/ordonner les offres", filters)
        if fh == 1:
            offers = sorted(offers, key=lambda o: o.get('unit_price_ht', Decimal('inf')))
        elif fh == 2:
            offers = sorted(offers, key=lambda o: o.get('lead_time_days', 9999) or 9999)
        elif fh == 3:
            offers = sorted(offers, key=lambda o: o.get('reliability', Decimal('0')), reverse=True)
        elif fh == 4:
            offers = sorted(offers, key=lambda o: o.get('quality_level', 0) or 0)

        lines = ["Fournisseur | Gamme | Pack | Prix HT | TVA | Délai (jours) | Fiabilité | DLC typique | MOQ", ""]
        for o in offers:
            pack = f"{o.get('pack_size')} {o.get('pack_unit','')}"
            delay = o.get('lead_time_days') if o.get('lead_time_days') is not None else "?"
            rel = o.get('reliability') if o.get('reliability') is not None else "?"
            dlc = f"{o.get('typical_shelf_life_days')}j" if o.get('typical_shelf_life_days') is not None else ""
            moq_bits = []
            if o.get('moq_qty'):
                moq_bits.append(f"Qté {o['moq_qty']}")
            if o.get('moq_value'):
                moq_bits.append(f"Valeur {o['moq_value']:.2f}€")
            moq = " / ".join(moq_bits)
            lines.append(f"{o.get('supplier_id')} | {o.get('quality_level')} | {pack} | {o.get('unit_price_ht'):.2f}€ | {o.get('vat_rate'):.1%} | {delay} | {rel} | {dlc} | {moq}")
        self.ui.print_box(lines, f"Catalogue — {ing_id}", "info")

        if self.ui.confirm("Pré-remplir une ligne dans ‘Composer ma commande’ ?"):
            # Laisser l’utilisateur choisir l’offre pour pré-remplissage
            opts = [f"{o.get('supplier_id')} | Gamme {o.get('quality_level')} | {o.get('unit_price_ht'):.2f}€" for o in offers]
            ch2 = self.ui.show_menu("Choisir une offre à envoyer", opts)
            if ch2 > 0:
                sel = offers[ch2 - 1]
                # Pré-remplissage stocké puis retour
                self._prefill_purchase = {
                    'ingredient_id': ing_id,
                    'supplier_id': sel.get('supplier_id'),
                    'quality_level': sel.get('quality_level'),
                }
                self.ui.show_success("Pré-remplissage enregistré. Ouvrez ‘Composer ma commande’.")
        self.ui.pause()

    def _catalog_by_supplier(self) -> None:
        supplier_ids = sorted({o['supplier_id'] for lst in self._suppliers_catalog.values() for o in lst})
        names = [getattr(self._suppliers_map.get(sid, None), 'name', sid) for sid in supplier_ids]
        opts = [f"{names[i]} ({supplier_ids[i]})" for i in range(len(supplier_ids))]
        ch = self.ui.show_menu("Choisir un fournisseur", opts)
        if ch == 0:
            return
        sid = supplier_ids[ch - 1]
        sup = self._suppliers_map.get(sid)
        strengths = []
        weaknesses = []
        if sup:
            # heuristiques simples
            if sup.reliability >= Decimal('0.95'):
                strengths.append("Fiabilité élevée")
            elif sup.reliability <= Decimal('0.85'):
                weaknesses.append("Fiabilité moyenne/faible")
            if sup.lead_time_days <= 2:
                strengths.append("Délais courts")
            elif sup.lead_time_days >= 5:
                weaknesses.append("Délais longs")
            if sup.min_order_value > 0:
                weaknesses.append(f"MOQ valeur élevé: {sup.min_order_value:.2f}€")
        header = ["FICHE FOURNISSEUR:"]
        if strengths:
            header.append("Forces: " + ", ".join(strengths))
        if weaknesses:
            header.append("Faiblesses: " + ", ".join(weaknesses))
        if sup:
            header.append(f"Délai (jours): {sup.lead_time_days} | Fiabilité: {sup.reliability}")
        self.ui.print_box(header, f"{getattr(sup, 'name', sid)}", "header")

        offers = []
        for ing_id, lst in self._suppliers_catalog.items():
            for o in lst:
                if o.get('supplier_id') == sid:
                    offers.append((ing_id, o))
        lines = ["Ingrédient | Gamme | Pack | Prix HT | TVA | Délai (jours) | Fiabilité | DLC typique | MOQ", ""]
        for ing_id, o in offers:
            pack = f"{o.get('pack_size')} {o.get('pack_unit','')}"
            delay = o.get('lead_time_days') if o.get('lead_time_days') is not None else "?"
            rel = o.get('reliability') if o.get('reliability') is not None else "?"
            dlc = f"{o.get('typical_shelf_life_days')}j" if o.get('typical_shelf_life_days') is not None else ""
            moq_bits = []
            if o.get('moq_qty'):
                moq_bits.append(f"Qté {o['moq_qty']}")
            if o.get('moq_value'):
                moq_bits.append(f"Valeur {o['moq_value']:.2f}€")
            moq = " / ".join(moq_bits)
            lines.append(f"{ing_id} | {o.get('quality_level')} | {pack} | {o.get('unit_price_ht'):.2f}€ | {o.get('vat_rate'):.1%} | {delay} | {rel} | {dlc} | {moq}")
        self.ui.print_box(lines, f"Catalogue — {getattr(sup, 'name', sid)}", "info")

        if self.ui.confirm("Pré-remplir une ligne dans ‘Composer ma commande’ ?"):
            if not offers:
                self.ui.pause()
                return
            opts = [f"{ing} | {o.get('supplier_id')} | Gamme {o.get('quality_level')} | {o.get('unit_price_ht'):.2f}€" for ing, o in offers]
            ch2 = self.ui.show_menu("Choisir une offre à envoyer", opts)
            if ch2 > 0:
                ing2, sel = offers[ch2 - 1]
                self._prefill_purchase = {
                    'ingredient_id': ing2,
                    'supplier_id': sel.get('supplier_id'),
                    'quality_level': sel.get('quality_level'),
                }
                self.ui.show_success("Pré-remplissage enregistré. Ouvrez ‘Composer ma commande’.")
        self.ui.pause()


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
            reviewed: List[POLine] = []
            for i, l in enumerate(pending, 1):
                self.ui.print_box(
                    [
                        f"{i}. {l.ingredient_id}: {l.quantity} @ {l.unit_price_ht:.2f}€ (pack {l.pack_size}) chez {l.supplier_id}"
                    ],
                    "REVUE LIGNE",
                    "warning",
                )
                # Permettre un override quantité (sur-stock autorisé)
                new_qty = self.ui.get_input(
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
            pending = reviewed

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
            self.ui.show_info("Aucune proposition automatique disponible.")
            self.ui.pause()
            return

        reviewed: List[POLine] = []
        for i, l in enumerate(auto_lines, 1):
            need = requirements.get(l.ingredient_id, Decimal("0"))
            order_value = l.quantity * l.unit_price_ht
            self.ui.print_box(
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
                    f"{o['supplier_id']} | Gamme {o.get('quality_level','?')} | Pack: {o.get('pack_size')} {o.get('pack_unit','')} | Prix HT: {o.get('unit_price_ht'):.2f}€ | TVA: {o.get('vat_rate'):.1%} | Délai (jours): {o.get('lead_time_days','?')} | Fiabilité: {o.get('reliability','?')}"
                    for o in offers
                ]
                ch = self.ui.show_menu(
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
            new_qty = self.ui.get_input(
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
        self.ui.show_success(
            "Commande automatique revue et enregistrée (à réceptionner)"
        )
        self.ui.pause()

        # Note: les recettes doivent être en cache pour calculs précis
        if not hasattr(self, "_available_recipes_cache"):
            self.ui.show_info(
                "Note: pour le calcul précis des besoins, les recettes doivent être connues. Cette version affichera le stock uniquement si non disponible."
            )
            self.ui.pause()
            return

    def cache_available_recipes(self, recipes: Dict[str, any]) -> None:
        """Optionnel: l'appelant peut fournir un cache des recettes pour achats."""
        self._available_recipes_cache = recipes

    def _propose_purchase_order(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Propose un PO en fonction des besoins et permet édition simple."""
        self.ui.clear_screen()
        if not hasattr(self, "_available_recipes_cache"):
            self.ui.show_error(
                "Recettes non disponibles pour proposer une commande. Activez des recettes et revenez."
            )
            self.ui.pause()
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
            self.ui.show_info(
                "Aucun besoin net détecté (stock suffisant ou prévision nulle)."
            )
            self.ui.pause()
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
            self.ui.show_info(
                "Aucune proposition de commande possible (catalogue incomplet)."
            )
            self.ui.pause()
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
        self.ui.print_box(view, "COMMANDE FOURNISSEURS", "info")

        if self.ui.confirm("Valider cette commande ?"):
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
            self.ui.show_success("Commande enregistrée (à réceptionner)")
        else:
            self.ui.show_info("Commande annulée")
        self.ui.pause()

    def _receiving_interface(self, restaurant: Restaurant) -> None:
        """Réceptionne les lignes en attente et crée des lots FEFO."""
        self.ui.clear_screen()
        from decimal import Decimal

        lines: list[POLine] = getattr(restaurant, "pending_po_lines", [])
        if not lines:
            self.ui.show_info("Aucune commande en attente.")
            self.ui.pause()
            return

        view = ["📥 RÉCEPTION DE COMMANDES:", ""]
        for i, l in enumerate(lines, 1):
            view.append(
                f"{i}. {l.ingredient_id} — Cmd: {l.quantity} | Acc: {l.accepted_qty} | Statut: {l.status}"
            )
        self.ui.print_box(view, "BON DE COMMANDE EN ATTENTE", "info")

        # Option: tout accepter automatiquement (gagne-temps)
        if self.ui.confirm("Tout accepter automatiquement (quantité restante par défaut) ?"):
            from ..core.procurement import DeliveryLine, ReceivingService, GoodsReceipt, GoodsReceiptLine
            from datetime import date
            gr_lines: list[GoodsReceiptLine] = []
            remaining_lines: list[POLine] = []
            for l in lines:
                to_receive_default = l.quantity - l.accepted_qty
                if to_receive_default <= 0:
                    continue
                deliveries = [
                    DeliveryLine(
                        ingredient_id=l.ingredient_id,
                        quantity_received=to_receive_default,
                        unit_price_ht=l.unit_price_ht,
                        vat_rate=l.vat_rate,
                        supplier_id=l.supplier_id,
                        pack_size=l.pack_size,
                        lot_number=None,
                        quality_level=l.quality_level or 2,
                    )
                ]
                receiver = ReceivingService(shelf_life_rules={1: -2, 3: 0, 5: 2})
                lots = receiver.receive(deliveries, date.today(), default_shelf_life_days=5)
                for lot in lots:
                    restaurant.stock_manager.add_lot(lot)
                qty_accepted = sum([lt.quantity for lt in lots], Decimal("0"))
                l.accepted_qty += qty_accepted
                l.status = "CLOSED" if l.accepted_qty >= l.quantity else ("PARTIAL" if l.accepted_qty > 0 else "OPEN")
                gr_lines.append(GoodsReceiptLine(
                    ingredient_id=l.ingredient_id,
                    qty_ordered=l.quantity,
                    qty_delivered=to_receive_default,
                    qty_accepted=qty_accepted,
                    unit_price_ht=l.unit_price_ht,
                    vat_rate=l.vat_rate,
                    supplier_id=l.supplier_id,
                    pack_size=l.pack_size,
                    lots=lots,
                    comment="auto-accept",
                ))
                if l.status != "CLOSED":
                    remaining_lines.append(l)
            total_ht = sum([(ln.qty_accepted * ln.unit_price_ht) for ln in gr_lines], Decimal("0"))
            total_ttc = sum([(ln.qty_accepted * ln.unit_price_ht) * (Decimal("1") + ln.vat_rate) for ln in gr_lines], Decimal("0"))
            po_status = "CLOSED" if not remaining_lines else ("PARTIAL" if any(l.accepted_qty > 0 for l in remaining_lines) else "OPEN")
            gr = GoodsReceipt(date=date.today(), lines=gr_lines, total_ht=total_ht, total_ttc=total_ttc, status=po_status)
            restaurant._last_goods_receipt = gr
            restaurant.pending_po_lines = remaining_lines
            view = [
                f"GR du {gr.date} — Statut PO: {gr.status}",
                f"Total accepté HT: {gr.total_ht:.2f}€ | TTC: {gr.total_ttc:.2f}€",
                "",
                "Détail par ligne:",
            ]
            for ln in gr.lines:
                view.append(f"• {ln.ingredient_id}: Cmd {ln.qty_ordered} | Livr {ln.qty_delivered} | Acc {ln.qty_accepted}")
            self.ui.print_box(view, "BON DE RÉCEPTION", "success")
            self.ui.pause()
            return

        # Saisie réception par ligne: accepter/refuser et split lots
        from ..core.procurement import (
            DeliveryLine,
            ReceivingService,
            GoodsReceipt,
            GoodsReceiptLine,
        )
        from datetime import date

        gr_lines: list[GoodsReceiptLine] = []
    def _auto_order_by_gamme(self, restaurant: Restaurant) -> None:
        """Commande auto selon la gamme de l’établissement (fast/bistro/gastro)."""
        self.ui.clear_screen()
        ch = self.ui.show_menu("Choisir la gamme de l’établissement", [
            "Fast-food (QL≈2)", "Bistro (QL≈3)", "Gastro (QL≈4/5)"])
        if ch == 0:
            return
        target_ql = 2 if ch == 1 else 3 if ch == 2 else 4
        # Calculer besoins nets
        planner = ProcurementPlanner()
        active_recipes = [self._available_recipes_cache[rid] for rid in restaurant.active_recipes if rid in getattr(self, '_available_recipes_cache', {})]
        forecast = getattr(restaurant, 'sales_forecast', {}) or {}
        requirements = planner.compute_requirements(active_recipes, forecast, restaurant.stock_manager)
        if not requirements:
            self.ui.show_info("Aucun besoin net détecté.")
            self.ui.pause()
            return
        # Construire un mini-catalogue orienté gamme
        suppliers_catalog = {}
        for ing_id, need in requirements.items():
            offers = list(self._suppliers_catalog.get(ing_id, [])) if hasattr(self, '_suppliers_catalog') else []
            if not offers:
                continue
            # choisir l’offre dont la QL est la plus proche de target_ql, avec fallback
            offers_sorted = sorted(offers, key=lambda o: (abs((o.get('quality_level') or 0) - target_ql), o.get('unit_price_ht', Decimal('inf'))))
            best = offers_sorted[0]
            suppliers_catalog.setdefault(ing_id, {})[best['supplier_id']] = {
                'price_ht': best['unit_price_ht'],
                'vat': best['vat_rate'],
                'pack': best['pack_size'],
                'moq_value': best.get('moq_value', Decimal('0')),
                'lead_time_days': best.get('lead_time_days'),
                'reliability': best.get('reliability'),
            }
        if not suppliers_catalog:
            self.ui.show_info("Catalogue insuffisant pour construire une commande.")
            self.ui.pause()
            return
        # Proposer lignes
        lines = planner.propose_purchase_orders(requirements, suppliers_catalog)
        if not lines:
            self.ui.show_info("Aucune proposition auto possible.")
            self.ui.pause()
            return
        # Ajouter à la commande en attente
        if not hasattr(restaurant, 'pending_po_lines'):
            restaurant.pending_po_lines = []
        restaurant.pending_po_lines.extend(lines)
        self.ui.show_success(f"{len(lines)} lignes ajoutées à la commande (gamme).")
        self.ui.pause()

        remaining_lines: list[POLine] = []
        all_lots: list = []

        for l in lines:
            # Choix simple : accepter ou refuser la ligne
            action = self.ui.show_menu(
                f"Ligne {l.ingredient_id} (Cmd {l.quantity})",
                ["Accepter la commande", "Refuser la commande"],
            )
            if action == 2:
                # Refus : on garde la ligne en attente, aucun lot créé
                remaining_lines.append(l)
                continue

            # Accepter (total/partiel)
            # Proposer une quantité livrée (par défaut = quantité commandée restante)
            to_receive_default = l.quantity - l.accepted_qty
            if to_receive_default < 0:
                to_receive_default = Decimal("0")
            qty_delivered = self.ui.get_input(
                f"Quantité livrée pour {l.ingredient_id} (reste {to_receive_default} à recevoir): ",
                Decimal,
                min_val=Decimal("0"),
                default=to_receive_default,
            ) or Decimal("0")

            # Option de split lots
            deliveries: list[DeliveryLine] = []
            if qty_delivered > 0:
                nb_lots = self.ui.ask_int(
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
                            q = self.ui.get_input(
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
                                lot_number=self.ui.get_input(
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
            "",
            "Détail par ligne:",
        ]
        for ln in gr.lines:
            view.append(
                f"• {ln.ingredient_id}: Cmd {ln.qty_ordered} | Livr {ln.qty_delivered} | Acc {ln.qty_accepted}"
            )
        self.ui.print_box(view, "BON DE RÉCEPTION", "success")

        expiring = restaurant.stock_manager.get_expiring_lots(days=3)
        if expiring:
            msg = ["⚠️ LOTS PROCHE DLC:"] + [
                f"• {lt.ingredient_id} ({lt.quantity}) — DLC {lt.dlc}"
                for lt in expiring
            ]
            self.ui.print_box(msg, "ALERTES DLC", "warning")

        self.ui.pause()

    def _place_order_interface(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Interface de commande avec choix de qualité."""
        self.ui.clear_screen()
        self.ui.show_info("🛒 CHOIX QUALITÉ DES INGRÉDIENTS")

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

        print(f"\n🎯 NIVEAUX DE QUALITÉ DISPONIBLES:")
        print(f"   1⭐ Économique (-30% coût, -20% satisfaction)")
        print(f"   2⭐ Standard (prix de référence)")
        print(f"   3⭐ Supérieur (+25% coût, +15% satisfaction)")
        print(f"   4⭐ Premium (+50% coût, +30% satisfaction)")
        print(f"   5⭐ Luxe (+100% coût, +50% satisfaction)")

        changes_made = False

        for ingredient_id, ingredient_name in ingredients_to_configure:
            current_level = restaurant.ingredient_choices.get(ingredient_id, 2)
            print(f"\n{ingredient_name} (actuel: {current_level}⭐)")

            try:
                new_level = self.ui.ask_int(
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

            except (ValueError, KeyboardInterrupt):
                print(f"   ⏭️ {ingredient_name} inchangé")
                continue

        if changes_made:
            # Recalcul des métriques
            new_quality = restaurant.get_overall_quality_score()
            new_cost_impact = restaurant.calculate_quality_cost_impact()

            print(f"\n📈 IMPACT DES CHANGEMENTS:")
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

            self.ui.show_success("✅ Choix de qualité enregistrés !")
        else:
            self.ui.show_info("ℹ️ Aucun changement effectué")

        self.ui.pause()

    def _stock_management_interface(self, restaurant: Restaurant) -> None:
        """Interface de gestion des stocks (réel, via StockManager)."""
        self.ui.show_info("📦 GESTION DES STOCKS")

        if not hasattr(restaurant, "stock_manager"):
            self.ui.show_info("Aucun stock pour l'instant.")
            self.ui.pause()
            return

        # Affichage réel des lots par ingrédient (FEFO)
        lots = getattr(restaurant.stock_manager, "lots", [])
        if not lots:
            self.ui.show_info("Aucun lot en stock.")
            self.ui.pause()
            return

        by_ing: Dict[str, List] = {}
        for lot in lots:
            by_ing.setdefault(lot.ingredient_id, []).append(lot)
        view = ["STOCKS ACTUELS", ""]
        for ing, ing_lots in by_ing.items():
            view.append(f"🍽️ {ing}:")
            ing_lots.sort(key=lambda x: x.dlc)
            for lt in ing_lots:
                emoji = "🚨" if lt.is_near_expiry(1) else ("⚠️" if lt.is_near_expiry(3) else "✅")
                view.append(
                    f"  Lot {lt.lot_number or '-'}: {lt.quantity} (DLC {lt.dlc}) {emoji} | Prix {lt.unit_cost_ht} HT, TVA {lt.vat_rate}, Fournisseur {lt.supplier_id}"
                )
        total_value = restaurant.stock_manager.get_stock_value()
        view.append("")
        view.append(f"Valeur stock HT: {total_value:.2f}€")
        self.ui.print_box(view, "ÉTAT DES STOCKS", "info")
        self.ui.pause()

        # Alertes DLC (rappel)
        expiring = restaurant.stock_manager.get_expiring_lots(days=3)
        if expiring:
            msg = ["⚠️ LOTS PROCHE DLC:"] + [f"• {lt.ingredient_id} ({lt.quantity}) — DLC {lt.dlc}" for lt in expiring]
            self.ui.print_box(msg, "ALERTES DLC", "warning")
            self.ui.pause()

        # Option: purge des périmés
        if self.ui.confirm("Supprimer les lots périmés ?"):
            removed = restaurant.stock_manager.remove_expired_lots()
            self.ui.show_info(f"{len(removed)} lots périmés supprimés.")
            self.ui.pause()
    # Suppression de l'affichage statique pour éviter les doublons et confusion

    def _supplier_analysis_interface(self, restaurant: Restaurant) -> None:
        """Interface d'analyse des fournisseurs."""
        self.ui.show_info("🏪 ANALYSE DES FOURNISSEURS")

        suppliers_data = [
            "📊 COMPARATIF FOURNISSEURS:",
            "",
            "🥩 METRO PRO:",
            "   Fiabilité: 95% | Délai: 1j | Prix: Standard",
            "   Spécialité: Gamme complète 1★-3★",
            "",
            "🌱 BIO FRANCE:",
            "   Fiabilité: 88% | Délai: 3j | Prix: +20%",
            "   Spécialité: Bio et premium 3★-5★",
            "",
            "🚚 RUNGIS DIRECT:",
            "   Fiabilité: 92% | Délai: 2j | Prix: Variable",
            "   Spécialité: Frais quotidien 2★-4★",
            "",
            "💡 Recommandation: Diversifiez vos sources",
            "   selon votre positionnement qualité",
        ]

        self.ui.print_box(suppliers_data, "FOURNISSEURS")
        self.ui.pause()

    def _quality_price_report(self, restaurant: Restaurant) -> None:
        """Rapport qualité/prix détaillé."""
        self.ui.clear_screen()
        self.ui.show_info("📊 RAPPORT QUALITÉ/PRIX DÉTAILLÉ")

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
            "",
            f"Score qualité global: {restaurant.get_quality_description()} ({quality_score:.1f}/5)",
            f"Impact sur coûts: {cost_impact:.0%}",
            f"Satisfaction client: {avg_satisfaction:.1f}/5",
            f"Réputation: {restaurant.reputation:.1f}/10",
            f"Ticket moyen: {avg_ticket:.2f}€",
            "",
            "🎯 ATTRACTIVITÉ PAR SEGMENT:",
            "",
            f"• Étudiants: {attractiveness_factors['students']:.0%} (sensibilité faible)",
            f"• Familles: {attractiveness_factors['families']:.0%} (sensibilité normale)",
            f"• Foodies: {attractiveness_factors['foodies']:.0%} (sensibilité élevée)",
            "",
            "💰 ANALYSE COÛT/BÉNÉFICE:",
            "",
        ]

        # Simulation d'amélioration qualité
        if quality_score < 4.0:
            target_quality = min(5.0, quality_score + 1.0)
            cost_increase = 25  # Estimation +25% pour +1 niveau
            satisfaction_increase = 15  # Estimation +15% satisfaction

            report_data.extend(
                [
                    f"📈 SIMULATION AMÉLIORATION (+1 niveau qualité):",
                    f"• Coût supplémentaire estimé: +{cost_increase}%",
                    f"• Satisfaction supplémentaire: +{satisfaction_increase}%",
                    f"• Nouvelle attractivité foodies: +{satisfaction_increase * 1.5:.0f}%",
                    "",
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

        self.ui.print_box(report_data, "RAPPORT QUALITÉ/PRIX")
        self.ui.pause()

    def _alerts_promotions_interface(self, restaurant: Restaurant) -> None:
        """Interface des alertes et promotions."""
        self.ui.show_info("⚠️ ALERTES ET PROMOTIONS")

        alerts_data = [
            "🚨 ALERTES URGENTES:",
            "",
            "• 5kg de tomates expirent demain",
            "  → Promotion -50% recommandée",
            "",
            "• Stock de steak haché bas (8kg restants)",
            "  → Commande urgente suggérée",
            "",
            "🎯 OPPORTUNITÉS SAISONNIÈRES:",
            "",
            "• Tomates d'été: -30% ce mois",
            "  → Qualité +1★ pour même prix",
            "",
            "• Champignons d'automne disponibles",
            "  → Nouveau plat saisonnier possible",
        ]

        self.ui.print_box(alerts_data, "ALERTES")
        self.ui.pause()

    def _marketing_interface(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Interface marketing et communication."""
        self.ui.clear_screen()
        self.ui.show_info("📈 MARKETING & COMMUNICATION")

        # Simuler l'état marketing actuel
        print(f"\n📊 ÉTAT MARKETING ACTUEL:")
        print(f"   Réputation en ligne: 4.2/5 ⭐ (127 avis)")
        print(f"   Budget marketing mensuel: 850€")
        print(f"   Campagnes actives: 2")
        print(f"   ROI marketing: 3.2x")

        # Options de campagnes
        print(f"\n🎯 CAMPAGNES DISPONIBLES:")
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

        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   • Augmenter présence réseaux sociaux (+20% clients jeunes)")
        print(f"   • Lancer programme fidélité (rétention +30%)")
        print(f"   • Répondre aux avis négatifs (réputation +0.3)")

        # Choix de campagne
        try:
            choice = self.ui.ask_int(
                "Lancer une campagne (1-4) ou 0 pour passer: ",
                min_val=0,
                max_val=4,
                default=0,
            )
            if choice > 0:
                campaign = campaigns[choice - 1]
                duration = self.ui.ask_int(
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

                self.ui.show_success(
                    f"✅ Campagne '{campaign['name']}' programmée pour {duration} jours"
                )
            else:
                self.ui.show_info("ℹ️ Aucune campagne lancée")

        except (ValueError, KeyboardInterrupt):
            self.ui.show_info("ℹ️ Aucune campagne lancée")

        self.ui.pause()

    def _finance_interface(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Interface finance avancée."""
        self.ui.clear_screen()
        self.ui.show_info("💰 FINANCE AVANCÉE")

        # Simuler les données financières
        print(f"\n📊 TABLEAU DE BORD FINANCIER:")
        print(f"   Trésorerie: 12,450€")
        print(f"   CA mensuel: 28,750€")
        print(f"   Marge brute: 65.2%")
        print(f"   Résultat net: 4,320€ (15.0%)")

        print(f"\n📈 RATIOS FINANCIERS:")
        print(f"   Liquidité: 2.1 (Bon)")
        print(f"   Endettement: 35% (Acceptable)")
        print(f"   ROE: 18.5% (Excellent)")
        print(f"   Rotation stocks: 12x/an (Optimal)")

        print(f"\n🍽️ RENTABILITÉ PAR PLAT:")
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

        print(f"\n💡 RECOMMANDATIONS FINANCIÈRES:")
        print(f"   • Augmenter prix Burger Classic (+0.50€ = +290€/mois)")
        print(f"   • Promouvoir Pâtes Carbonara (marge la plus élevée)")
        print(f"   • Optimiser coûts Pizza Margherita (-0.20€ coût)")
        print(f"   • Négocier délais fournisseurs (trésorerie +15%)")

        # Options financières
        print(f"\n🎯 ACTIONS DISPONIBLES:")
        print(f"   1. Demander un prêt bancaire")
        print(f"   2. Investir dans du matériel")
        print(f"   3. Optimiser la trésorerie")
        print(f"   4. Analyser un investissement")

        try:
            choice = self.ui.ask_int(
                "Choisir une action (1-4) ou 0 pour passer: ",
                min_val=0,
                max_val=4,
                default=0,
            )

            if choice == 1:
                amount = self.ui.ask_float(
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
                self.ui.show_success(
                    f"✅ Demande de prêt de {amount:,.0f}€ enregistrée"
                )

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

                print(f"\n🔧 ÉQUIPEMENTS DISPONIBLES:")
                for i, eq in enumerate(equipment_options, 1):
                    print(f"   {i}. {eq['name']}: {eq['cost']}€ ({eq['benefit']})")

                eq_choice = self.ui.ask_int(
                    "Choisir équipement (1-3): ", min_val=1, max_val=3, default=1
                )
                equipment = equipment_options[eq_choice - 1]

                decisions["equipment_purchase"] = {
                    "name": equipment["name"],
                    "cost": equipment["cost"],
                    "benefit": equipment["benefit"],
                }
                self.ui.show_success(f"✅ Achat {equipment['name']} programmé")

            elif choice == 3:
                print(f"\n💰 OPTIMISATION TRÉSORERIE:")
                print(f"   • Négocier délais paiement fournisseurs: +2,100€")
                print(f"   • Accélérer encaissements clients: +850€")
                print(f"   • Optimiser niveau stocks: +1,200€")

                decisions["cash_optimization"] = True
                self.ui.show_success("✅ Plan d'optimisation trésorerie activé")

            elif choice == 4:
                investment_amount = self.ui.ask_float(
                    "Montant investissement (€): ",
                    min_val=1000,
                    max_val=30000,
                    default=5000,
                )
                expected_return = investment_amount * 0.15  # 15% de retour estimé
                payback_months = investment_amount / (expected_return / 12)

                print(f"\n📊 ANALYSE INVESTISSEMENT:")
                print(f"   Investissement: {investment_amount:,.0f}€")
                print(f"   Retour annuel estimé: {expected_return:,.0f}€")
                print(f"   Retour sur investissement: 15%")
                print(f"   Période de retour: {payback_months:.1f} mois")

                decisions["investment_analysis"] = {
                    "amount": investment_amount,
                    "expected_return": expected_return,
                    "roi": 0.15,
                    "payback_months": payback_months,
                }

            else:
                self.ui.show_info("ℹ️ Aucune action financière")

        except (ValueError, KeyboardInterrupt):
            self.ui.show_info("ℹ️ Aucune action financière")

        self.ui.pause()

    def _marketing_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Décisions marketing et commerciales."""
        while True:
            self.ui.clear_screen()

            submenu_options = [
                "📢 Lancer une campagne publicitaire",
                "🎁 Programme de fidélité",
                "🎉 Organiser un événement spécial",
                "🤝 Partenariats locaux",
                "📱 Présence digitale",
                "💳 Moyens de paiement",
            ]

            choice = self.ui.show_menu("MARKETING & COMMERCIAL", submenu_options)

            if choice == 0:
                break
            elif choice == 1:
                self._advertising_campaign(restaurant, decisions)
            elif choice == 2:
                self._loyalty_program(restaurant, decisions)
            elif choice == 3:
                self._special_event(restaurant, decisions)
            else:
                self.ui.show_info(f"Option {choice} - En développement")
                self.ui.pause()

    def _advertising_campaign(self, restaurant: Restaurant, decisions: Dict) -> None:
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

        self.ui.clear_screen()

        campaign_options = [
            f"{name} - {cost}€ (Impact: {impact})"
            for name, cost, impact, desc in campaign_types
        ]

        choice = self.ui.show_menu("CAMPAGNES PUBLICITAIRES", campaign_options)

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
            "",
            f"Trésorerie actuelle: {restaurant.cash:.0f}€",
            f"Trésorerie après campagne: {restaurant.cash - cost:.0f}€",
        ]

        self.ui.print_box(details, style="info")

        if restaurant.cash < cost:
            self.ui.show_error("Trésorerie insuffisante pour cette campagne.")
            self.ui.pause()
            return

        if self.ui.confirm(f"Lancer la campagne {name} pour {cost}€ ?"):
            if "marketing_campaigns" not in decisions:
                decisions["marketing_campaigns"] = []

            decisions["marketing_campaigns"].append(
                {"type": name, "cost": cost, "impact": impact}
            )

            self.ui.show_success(f"Campagne {name} programmée !")
            self.ui.pause()

    def _financial_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Décisions financières."""
        while True:
            self.ui.clear_screen()

            submenu_options = [
                "💳 Demander un prêt bancaire",
                "💰 Rembourser un emprunt",
                "📈 Placer des excédents",
                "📅 États par tour (P&L / Bilan)",

                "📊 Analyser la rentabilité",
                "💸 Gérer la trésorerie",
            ]

            choice = self.ui.show_menu("FINANCE & COMPTABILITÉ", submenu_options)

            if choice == 0:
                break
            elif choice == 4:
                self._financial_states_by_turn(restaurant)
            else:
                self.ui.show_info("Fonction à venir…")
                self.ui.pause()
                self.ui.show_info(f"Option financière {choice} - En développement")
                self.ui.pause()

    def _financial_states_by_turn(self, restaurant: Restaurant) -> None:
        """Affiche une navigation par tour: P&L et Bilan par tour + Cumulé."""
        from ..core.ledger import Ledger
        ledger = Ledger()
        while True:
            self.ui.clear_screen()
            # Tours disponibles basés sur l'historique des allocations/production
            turns = sorted((restaurant.production_stats_history or {}).keys())
            options = [f"Tour {t}" for t in turns]
            options.append("Cumulé (1 → courant)")
            choice = self.ui.show_menu("États par tour", options)
            if choice == 0:
                return
            if choice == len(options):
                period = "Cumulé"
                # Appel des rapports existants (à terme: agréger les données réelles)
                self.financial_reports.show_profit_loss_statement(restaurant, ledger, period)
                self.ui.pause()
                # Bilan (placeholder basé sur ledger)
                self.financial_reports.show_balance_sheet(restaurant, ledger)
                self.ui.pause()
            else:
                tsel = turns[choice - 1]
                period = f"Tour {tsel}"
                self.financial_reports.show_profit_loss_statement(restaurant, ledger, period)
                self.ui.pause()
                self.financial_reports.show_balance_sheet(restaurant, ledger)
                self.ui.pause()

    def _show_reports(self, restaurant: Restaurant) -> None:
        """Affichage des rapports financiers."""
        while True:
            self.ui.clear_screen()

            report_options = [
                "📊 Compte de résultat",
                "💰 Tableau de flux de trésorerie",
                "📋 Bilan comptable",
                "📈 Analyse des KPIs",
                "📉 Évolution des performances",
                "🍽️ Production (coûts & volumes)",
            ]

            choice = self.ui.show_menu("RAPPORTS & ANALYSES", report_options)

            if choice == 0:
                break
            elif choice == 1:
                from ..core.ledger import Ledger
                ledger = Ledger()
                self.financial_reports.show_profit_loss_statement(restaurant, ledger)
                self.ui.pause()
            elif choice == 2:
                from ..core.ledger import Ledger
                ledger = Ledger()
                self.financial_reports.show_cash_flow_statement(restaurant, ledger)
                self.ui.pause()
            elif choice == 3:
                from ..core.ledger import Ledger
                ledger = Ledger()
                self.financial_reports.show_balance_sheet(restaurant, ledger)
                self.ui.pause()
            elif choice == 4:
                self.financial_reports.show_kpi_analysis(restaurant)
                self.ui.pause()
            elif choice == 5:
                self._production_reports(restaurant)
                self.ui.pause()

    def _production_reports(self, restaurant: Restaurant) -> None:
        self.ui.clear_screen()
        turn = getattr(self, 'current_turn', None)
        # Essayer d'utiliser le dernier tour si non fourni via menu
        stats = getattr(restaurant, 'production_stats_history', {})
        if not stats:
            self.ui.show_info("Aucune production enregistrée pour ce restaurant.")
            return
        # Prendre le plus récent
        latest_turn = max(stats.keys())
        data = stats[latest_turn]
        lines = [f"🍽️ Production — Tour {latest_turn}", "", "Recette | Produites | Vendues | Perdues | Coût/portion (HT)", "-"]
        for rid, d in data.items():
            cost = d.get('cost_per_portion')
            cost_str = f"{cost:.2f}€" if cost is not None else "?"
            lines.append(f"{rid} | {d.get('produced',0)} | {d.get('sold',0)} | {d.get('lost',0)} | {cost_str}")
        self.ui.print_box(lines, style='info')
        self.ui.pause()

    def _validate_decisions(self, restaurant: Restaurant, decisions: Dict) -> bool:
        """Validation finale des décisions."""
        if not decisions:
            return self.ui.confirm("Aucune décision prise. Passer au tour suivant ?")

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

        self.ui.print_box(summary, "VALIDATION", "warning")

        return self.ui.confirm("Valider ces décisions et passer au tour suivant ?")

    # Méthodes utilitaires (implémentation complète)
    def _add_recipes(
        self, restaurant: Restaurant, available_recipes: Dict, decisions: Dict
    ) -> None:
        """Ajoute des recettes disponibles au menu actif avec prix TTC."""
        self.ui.clear_screen()

        # Recettes non actives
        inactive = [
            r
            for r in available_recipes.values()
            if r.id not in restaurant.active_recipes
        ]
        if not inactive:
            self.ui.show_info("Toutes les recettes sont déjà actives.")
            self.ui.pause()
            return

        # Choix multiple simple (itératif)
        while True:
            options = [f"{r.name} ({r.id})" for r in inactive]
            choice = self.ui.show_menu("Ajouter un plat", options)
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

            price_ttc = self.ui.get_input(
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
            if not inactive or not self.ui.confirm("Ajouter un autre plat ?"):
                break

    def _remove_recipes(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Retire des recettes du menu actif."""
        active = restaurant.get_active_menu()
        if not active:
            self.ui.show_info("Aucune recette active.")
            self.ui.pause()
            return

        options = [f"{rid} - {price:.2f}€" for rid, price in active.items()]
        choice = self.ui.show_menu("Retirer un plat", options)
        if choice == 0:
            return

        selected_id = list(active.keys())[choice - 1]
        restaurant.deactivate_recipe(selected_id)
        decisions.setdefault("removed_recipes", []).append(selected_id)
        self.ui.show_success(f"Recette {selected_id} désactivée")
        self.ui.pause()

    def _analyze_recipe_profitability(
        self, restaurant: Restaurant, available_recipes: Dict
    ) -> None:
        """Analyse marge et recommandations par recette active."""
        active = restaurant.get_active_menu()
        if not active:
            self.ui.show_info("Aucune recette active.")
            self.ui.pause()
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

        self.ui.print_box(lines, "ANALYSE RENTABILITÉ", "info")
        self.ui.pause()

    def _create_daily_menu(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Crée un menu du jour (sous-ensemble des recettes actives) avec prix spéciaux."""
        active = restaurant.get_active_menu()
        if not active:
            self.ui.show_info("Aucune recette active.")
            self.ui.pause()
            return

        options = [f"{rid} - {price:.2f}€" for rid, price in active.items()]
        selection: List[str] = []

        while True:
            choice = self.ui.show_menu("Ajouter au menu du jour", options)
            if choice == 0:
                break
            rid = list(active.keys())[choice - 1]
            if rid not in selection:
                selection.append(rid)
            if not self.ui.confirm("Ajouter un autre plat au menu du jour ?"):
                break

        if not selection:
            self.ui.show_info("Aucune sélection pour le menu du jour.")
            self.ui.pause()
            return

        # Prix spéciaux (remise % simple)
        discount = self.ui.get_input(
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
        self.ui.show_success("Menu du jour créé pour 1 tour")
        self.ui.pause()

    def _show_sales_history(self, restaurant: Restaurant) -> None:
        """Affiche l'historique des ventes par recette (si disponible)."""
        history = getattr(restaurant, "sales_history", None)
        if not history:
            self.ui.show_info("Aucun historique de ventes disponible.")
            self.ui.pause()
            return

        lines = ["📈 HISTORIQUE DES VENTES:", ""]
        for rid, records in history.items():  # records: List[Tuple[turn, qty]]
            total = sum(q for _, q in records)
            lines.append(f"• {rid}: total {total} portions")
        self.ui.print_box(lines, "VENTES", "info")
        self.ui.pause()

    def _fire_employee(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Licenciement - En développement")
        self.ui.pause()

    def _train_employees(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Formation - En développement")
        self.ui.pause()

    def _adjust_schedules(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Horaires - En développement")
        self.ui.pause()

    def _negotiate_salaries(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Négociation salaires - En développement")
        self.ui.pause()

    def _analyze_productivity(self, restaurant: Restaurant) -> None:
        self.ui.show_info("Analyse productivité - En développement")
        self.ui.pause()

    def _loyalty_program(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Programme fidélité - En développement")
        self.ui.pause()

    def _special_event(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Événement spécial - En développement")
        self.ui.pause()

    def _investment_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Investissements - En développement")
        self.ui.pause()

    def show_random_events(self, event_manager: RandomEventManager) -> None:
        """Affiche les événements aléatoires actifs."""
        events_summary = event_manager.get_events_summary()

        if not events_summary["active_events"]:
            self.ui.show_info("📅 Aucun événement spécial en cours")
            return

        self.ui.clear_screen()
        self.ui.show_info("🎲 ÉVÉNEMENTS EN COURS")

        for event in events_summary["active_events"]:
            print(f"\n{event['title']}")
            print(f"   📝 {event['description']}")
            print(f"   📊 Catégorie: {event['category']}")
            print(f"   ⏱️ Reste: {event['remaining_turns']} tour(s)")

        # Afficher les effets cumulés
        effects = event_manager.get_current_effects()

        print(f"\n📈 EFFETS CUMULÉS:")
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
            print(f"   Effets par segment:")
            for segment, multiplier in effects["segment_effects"].items():
                change = (multiplier - 1) * 100
                print(f"     • {segment}: {change:+.0f}%")

        self.ui.pause()
