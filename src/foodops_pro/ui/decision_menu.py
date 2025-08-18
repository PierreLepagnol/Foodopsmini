"""
Menu de décisions enrichi pour FoodOps Pro.
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from ..domain.restaurant import Restaurant
from ..domain.employee import Employee, EmployeePosition, EmployeeContract
from ..core.costing import RecipeCostCalculator
from .console_ui import ConsoleUI
from .financial_reports import FinancialReports


class DecisionMenu:
    """Menu de décisions stratégiques pour les joueurs."""
    
    def __init__(self, ui: ConsoleUI, cost_calculator: RecipeCostCalculator):
        self.ui = ui
        self.cost_calculator = cost_calculator
        self.financial_reports = FinancialReports(ui)
    
    def show_decision_menu(self, restaurant: Restaurant, turn: int, 
                          available_recipes: Dict, available_employees: List = None) -> Dict[str, any]:
        """
        Affiche le menu de décisions principal et retourne les choix du joueur.
        
        Returns:
            Dict contenant toutes les décisions prises
        """
        decisions = {}
        
        while True:
            self.ui.clear_screen()
            self._show_restaurant_status(restaurant, turn)
            
            menu_options = [
                "📋 Menu & Pricing",
                "👥 Ressources Humaines", 
                "🛒 Achats & Stocks",
                "📈 Marketing & Commercial",
                "🏗️ Investissements",
                "💰 Finance & Comptabilité",
                "📊 Rapports & Analyses",
                "✅ Valider et passer au tour suivant"
            ]
            
            choice = self.ui.show_menu(
                f"DÉCISIONS - TOUR {turn} - {restaurant.name}",
                menu_options,
                allow_back=False
            )
            
            if choice == 1:
                self._menu_pricing_decisions(restaurant, available_recipes, decisions)
            elif choice == 2:
                self._hr_decisions(restaurant, available_employees, decisions)
            elif choice == 3:
                self._purchasing_decisions(restaurant, decisions)
            elif choice == 4:
                self._marketing_decisions(restaurant, decisions)
            elif choice == 5:
                self._investment_decisions(restaurant, decisions)
            elif choice == 6:
                self._financial_decisions(restaurant, decisions)
            elif choice == 7:
                self._show_reports(restaurant)
            elif choice == 8:
                if self._validate_decisions(restaurant, decisions):
                    break
        
        return decisions
    
    def _show_restaurant_status(self, restaurant: Restaurant, turn: int) -> None:
        """Affiche le statut actuel du restaurant."""
        status = [
            f"🏪 {restaurant.name} ({restaurant.type.value.title()})",
            f"💰 Trésorerie: {restaurant.cash:,.0f}€",
            f"👥 Employés: {len(restaurant.employees)}",
            f"🍽️ Capacité: {restaurant.capacity_current} couverts",
            f"📊 Niveau staffing: {restaurant.staffing_level}/3",
            f"🍴 Recettes actives: {len(restaurant.get_active_menu())}"
        ]
        
        # Couleur selon la santé financière
        if restaurant.cash > 20000:
            style = "success"
        elif restaurant.cash > 5000:
            style = "warning"
        else:
            style = "error"
        
        self.ui.print_box(status, f"STATUT - TOUR {turn}", style)
    
    def _menu_pricing_decisions(self, restaurant: Restaurant, 
                               available_recipes: Dict, decisions: Dict) -> None:
        """Gestion du menu et des prix."""
        while True:
            self.ui.clear_screen()
            
            submenu_options = [
                "💰 Modifier les prix",
                "➕ Ajouter des plats au menu",
                "➖ Retirer des plats du menu",
                "📊 Analyser la rentabilité par plat",
                "🍽️ Créer un menu du jour",
                "📈 Voir l'historique des ventes"
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
                estimated_cost = current_price * Decimal("0.35")  # 35% de food cost estimé
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
            [f"{recipe_id} - {active_menu[recipe_id]:.2f}€" for recipe_id in recipe_list]
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
            default=current_price
        )
        
        if new_price and new_price != current_price:
            if 'price_changes' not in decisions:
                decisions['price_changes'] = {}
            decisions['price_changes'][selected_recipe] = new_price
            
            # Calcul de l'impact
            change_pct = ((new_price - current_price) / current_price * 100)
            impact_msg = f"Prix modifié: {current_price:.2f}€ → {new_price:.2f}€ ({change_pct:+.1f}%)"
            
            if abs(change_pct) > 10:
                impact_msg += "\n⚠️ Changement important - Impact sur la clientèle attendu"
            
            self.ui.show_success(impact_msg)
            self.ui.pause()
    
    def _hr_decisions(self, restaurant: Restaurant, 
                     available_employees: List, decisions: Dict) -> None:
        """Gestion des ressources humaines."""
        while True:
            self.ui.clear_screen()
            
            # Affichage de l'équipe actuelle
            team_info = [f"ÉQUIPE ACTUELLE ({len(restaurant.employees)} employés):"]
            
            total_cost = Decimal("0")
            for emp in restaurant.employees:
                monthly_cost = emp.salary_gross_monthly * Decimal("1.42")  # Avec charges
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
                "📊 Analyser la productivité"
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
            EmployeePosition.CAISSE: (1650, 2200)
        }
        
        min_salary, max_salary = salary_ranges.get(selected_position, (1650, 3000))
        
        salary = self.ui.get_input(
            f"Salaire brut mensuel ({min_salary}-{max_salary}€)",
            Decimal,
            min_val=Decimal(str(min_salary)),
            max_val=Decimal(str(max_salary)),
            default=Decimal(str((min_salary + max_salary) // 2))
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
            if 'recruitments' not in decisions:
                decisions['recruitments'] = []
            
            decisions['recruitments'].append({
                'position': selected_position,
                'contract': selected_contract,
                'salary': salary
            })
            
            self.ui.show_success(
                f"Recrutement programmé: {selected_position.value} "
                f"en {selected_contract.value} à {salary:.0f}€/mois"
            )
            self.ui.pause()
    
    def _purchasing_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Gestion des achats et stocks avancée."""
        while True:
            self.ui.clear_screen()

            submenu_options = [
                "🛒 Passer une commande",
                "📦 Gérer les stocks",
                "🏪 Analyser les fournisseurs",
                "📊 Rapport qualité/prix",
                "⚠️ Alertes et promotions",
                "🔙 Retour"
            ]

            choice = self.ui.show_menu("ACHATS & STOCKS", submenu_options)

            if choice == 1:
                self._place_order_interface(restaurant, decisions)
            elif choice == 2:
                self._stock_management_interface(restaurant)
            elif choice == 3:
                self._supplier_analysis_interface(restaurant)
            elif choice == 4:
                self._quality_price_report(restaurant)
            elif choice == 5:
                self._alerts_promotions_interface(restaurant)
            elif choice == 6:
                break

    def _place_order_interface(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Interface de commande avec choix de qualité."""
        self.ui.show_info("🛒 COMMANDE D'INGRÉDIENTS")

        # Simuler l'affichage des options de qualité
        example_ingredients = [
            {
                'name': 'Steak haché',
                'variants': [
                    {'quality': '⭐ Surgelé', 'price': '5.95€/kg', 'supplier': 'Davigel'},
                    {'quality': '⭐⭐ Frais standard', 'price': '8.50€/kg', 'supplier': 'Metro Pro'},
                    {'quality': '⭐⭐⭐⭐ Bio', 'price': '12.75€/kg', 'supplier': 'Bio France'},
                ]
            },
            {
                'name': 'Tomates',
                'variants': [
                    {'quality': '⭐ Conserve', 'price': '2.24€/kg', 'supplier': 'Metro Pro'},
                    {'quality': '⭐⭐ Frais import', 'price': '3.20€/kg', 'supplier': 'Rungis Direct'},
                    {'quality': '⭐⭐⭐⭐⭐ Terroir', 'price': '6.40€/kg', 'supplier': 'Ferme Locale'},
                ]
            }
        ]

        for ingredient in example_ingredients:
            self.ui.print_section(f"📋 {ingredient['name']}")
            for variant in ingredient['variants']:
                print(f"   {variant['quality']} - {variant['price']} ({variant['supplier']})")

        self.ui.show_info("💡 Choisissez vos ingrédients selon votre stratégie qualité/prix")
        self.ui.pause()

    def _stock_management_interface(self, restaurant: Restaurant) -> None:
        """Interface de gestion des stocks."""
        self.ui.show_info("📦 GESTION DES STOCKS")

        # Simuler l'affichage des stocks
        stock_info = [
            "📊 ÉTAT DES STOCKS:",
            "",
            "🥩 Steak haché:",
            "   Lot A: 15kg (expire dans 2 jours) ⚠️",
            "   Lot B: 8kg (expire dans 5 jours) ✅",
            "",
            "🍅 Tomates:",
            "   Lot C: 5kg (expire demain) 🚨 PROMOTION -50%",
            "   Lot D: 12kg (expire dans 4 jours) ✅",
            "",
            "💡 Actions recommandées:",
            "• Utiliser le Lot A en priorité (FEFO)",
            "• Promouvoir les tomates du Lot C",
            "• Commander du steak haché (stock bas)"
        ]

        self.ui.print_box(stock_info, "STOCKS ACTUELS")
        self.ui.pause()

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
            "   selon votre positionnement qualité"
        ]

        self.ui.print_box(suppliers_data, "FOURNISSEURS")
        self.ui.pause()

    def _quality_price_report(self, restaurant: Restaurant) -> None:
        """Rapport qualité/prix."""
        self.ui.show_info("📊 RAPPORT QUALITÉ/PRIX")

        report_data = [
            "📈 IMPACT QUALITÉ SUR VOS VENTES:",
            "",
            "Score qualité actuel: ⭐⭐⭐ (3.2/5)",
            "Impact sur attractivité: +15%",
            "",
            "💰 ANALYSE COÛT/BÉNÉFICE:",
            "• Passer en bio (+50% coût) = +30% satisfaction",
            "• ROI estimé: +12% de marge sur 6 mois",
            "",
            "🎯 RECOMMANDATIONS:",
            "• Privilégier le bio sur 2-3 ingrédients clés",
            "• Garder l'économique sur les accompagnements",
            "• Communiquer sur la qualité pour justifier les prix"
        ]

        self.ui.print_box(report_data, "QUALITÉ/PRIX")
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
            "  → Nouveau plat saisonnier possible"
        ]

        self.ui.print_box(alerts_data, "ALERTES")
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
                "💳 Moyens de paiement"
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
            ("Flyers quartier", 200, "Faible", "Distribution de flyers dans le quartier"),
            ("Radio locale", 800, "Moyen", "Spot radio aux heures de pointe"),
            ("Réseaux sociaux", 300, "Moyen", "Campagne Facebook/Instagram ciblée"),
            ("Journal local", 500, "Faible", "Encart publicitaire dans la presse locale"),
            ("Influenceurs", 1200, "Fort", "Collaboration avec des influenceurs food")
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
            f"Trésorerie après campagne: {restaurant.cash - cost:.0f}€"
        ]
        
        self.ui.print_box(details, style="info")
        
        if restaurant.cash < cost:
            self.ui.show_error("Trésorerie insuffisante pour cette campagne.")
            self.ui.pause()
            return
        
        if self.ui.confirm(f"Lancer la campagne {name} pour {cost}€ ?"):
            if 'marketing_campaigns' not in decisions:
                decisions['marketing_campaigns'] = []
            
            decisions['marketing_campaigns'].append({
                'type': name,
                'cost': cost,
                'impact': impact
            })
            
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
                "📊 Analyser la rentabilité",
                "💸 Gérer la trésorerie"
            ]
            
            choice = self.ui.show_menu("FINANCE", submenu_options)
            
            if choice == 0:
                break
            else:
                self.ui.show_info(f"Option financière {choice} - En développement")
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
                "📉 Évolution des performances"
            ]
            
            choice = self.ui.show_menu("RAPPORTS & ANALYSES", report_options)
            
            if choice == 0:
                break
            elif choice == 1:
                # Pour la démo, on crée un ledger vide
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
            else:
                self.ui.show_info(f"Rapport {choice} - En développement")
                self.ui.pause()
    
    def _validate_decisions(self, restaurant: Restaurant, decisions: Dict) -> bool:
        """Validation finale des décisions."""
        if not decisions:
            return self.ui.confirm("Aucune décision prise. Passer au tour suivant ?")
        
        # Résumé des décisions
        summary = ["RÉSUMÉ DES DÉCISIONS:"]
        
        if 'price_changes' in decisions:
            summary.append("💰 Modifications de prix:")
            for recipe, price in decisions['price_changes'].items():
                summary.append(f"  • {recipe}: {price:.2f}€")
        
        if 'recruitments' in decisions:
            summary.append("👤 Recrutements:")
            for recruit in decisions['recruitments']:
                summary.append(f"  • {recruit['position'].value} - {recruit['salary']:.0f}€/mois")
        
        if 'marketing_campaigns' in decisions:
            summary.append("📢 Campagnes marketing:")
            for campaign in decisions['marketing_campaigns']:
                summary.append(f"  • {campaign['type']} - {campaign['cost']}€")
        
        self.ui.print_box(summary, "VALIDATION", "warning")
        
        return self.ui.confirm("Valider ces décisions et passer au tour suivant ?")
    
    # Méthodes utilitaires (implémentation simplifiée)
    def _add_recipes(self, restaurant: Restaurant, available_recipes: Dict, decisions: Dict) -> None:
        self.ui.show_info("Ajout de recettes - En développement")
        self.ui.pause()
    
    def _remove_recipes(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Retrait de recettes - En développement")
        self.ui.pause()
    
    def _analyze_recipe_profitability(self, restaurant: Restaurant, available_recipes: Dict) -> None:
        self.ui.show_info("Analyse rentabilité - En développement")
        self.ui.pause()
    
    def _create_daily_menu(self, restaurant: Restaurant, decisions: Dict) -> None:
        self.ui.show_info("Menu du jour - En développement")
        self.ui.pause()
    
    def _show_sales_history(self, restaurant: Restaurant) -> None:
        self.ui.show_info("Historique des ventes - En développement")
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
