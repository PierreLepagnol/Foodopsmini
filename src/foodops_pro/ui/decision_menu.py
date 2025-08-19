"""
Menu de décisions enrichi pour FoodOps Pro.
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from ..domain.restaurant import Restaurant
from ..domain.employee import Employee, EmployeePosition, EmployeeContract
from ..domain.random_events import RandomEventManager
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
                "📈 Marketing & Communication",
                "💰 Finance avancée",
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
                self._marketing_interface(restaurant, decisions)
            elif choice == 7:
                self._finance_interface(restaurant, decisions)
            elif choice == 8:
                break

    def _place_order_interface(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Interface de commande avec choix de qualité."""
        self.ui.clear_screen()
        self.ui.show_info("🛒 CHOIX QUALITÉ DES INGRÉDIENTS")

        # Affichage de l'état actuel
        current_quality = restaurant.get_overall_quality_score()
        print(f"\n📊 QUALITÉ ACTUELLE: {restaurant.get_quality_description()} ({current_quality:.1f}/5)")
        print(f"💰 Impact coût: {restaurant.calculate_quality_cost_impact():.0%}")
        print(f"⭐ Réputation: {restaurant.reputation:.1f}/10")

        # Choix des ingrédients principaux
        ingredients_to_configure = [
            ("beef_ground", "🥩 Viande (bœuf haché)"),
            ("tomato", "🍅 Légumes (tomates)"),
            ("cheese_mozzarella", "🧀 Fromage (mozzarella)"),
            ("flour", "🌾 Féculents (farine)")
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
                    min_val=1, max_val=5, default=current_level
                )

                if new_level != current_level:
                    restaurant.set_ingredient_quality(ingredient_id, new_level)
                    changes_made = True
                    print(f"   ✅ {ingredient_name} mis à jour: {current_level}⭐ → {new_level}⭐")

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
            decisions['ingredient_quality_changes'] = {
                'previous_score': float(current_quality),
                'new_score': float(new_quality),
                'cost_impact': float(new_cost_impact),
                'ingredients': dict(restaurant.ingredient_choices)
            }

            self.ui.show_success("✅ Choix de qualité enregistrés !")
        else:
            self.ui.show_info("ℹ️ Aucun changement effectué")

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
            ""
        ]

        # Simulation d'amélioration qualité
        if quality_score < 4.0:
            target_quality = min(5.0, quality_score + 1.0)
            cost_increase = 25  # Estimation +25% pour +1 niveau
            satisfaction_increase = 15  # Estimation +15% satisfaction

            report_data.extend([
                f"📈 SIMULATION AMÉLIORATION (+1 niveau qualité):",
                f"• Coût supplémentaire estimé: +{cost_increase}%",
                f"• Satisfaction supplémentaire: +{satisfaction_increase}%",
                f"• Nouvelle attractivité foodies: +{satisfaction_increase * 1.5:.0f}%",
                ""
            ])

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
                recommendations.append("• Prix élevé vs qualité: risque de perte clients")
            elif price_quality_ratio < 2.5:
                recommendations.append("• Excellent rapport qualité/prix: potentiel hausse prix")

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
                    "flour": "Féculents"
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
            "  → Nouveau plat saisonnier possible"
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
            {"name": "Réseaux sociaux", "cost": "50€/jour", "reach": "1000 personnes", "conversion": "2.5%"},
            {"name": "Publicité locale", "cost": "80€/jour", "reach": "750 personnes", "conversion": "3.5%"},
            {"name": "Programme fidélité", "cost": "30€/jour", "reach": "150 clients", "conversion": "15%"},
            {"name": "Événement spécial", "cost": "200€/jour", "reach": "400 personnes", "conversion": "8%"},
        ]

        for i, campaign in enumerate(campaigns, 1):
            print(f"   {i}. {campaign['name']}: {campaign['cost']} - {campaign['reach']} - {campaign['conversion']}")

        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   • Augmenter présence réseaux sociaux (+20% clients jeunes)")
        print(f"   • Lancer programme fidélité (rétention +30%)")
        print(f"   • Répondre aux avis négatifs (réputation +0.3)")

        # Choix de campagne
        try:
            choice = self.ui.ask_int("Lancer une campagne (1-4) ou 0 pour passer: ", min_val=0, max_val=4, default=0)
            if choice > 0:
                campaign = campaigns[choice - 1]
                duration = self.ui.ask_int(f"Durée en jours pour '{campaign['name']}': ", min_val=1, max_val=30, default=7)

                decisions['marketing_campaign'] = {
                    'type': campaign['name'],
                    'cost_per_day': campaign['cost'],
                    'duration': duration,
                    'expected_reach': campaign['reach'],
                    'expected_conversion': campaign['conversion']
                }

                self.ui.show_success(f"✅ Campagne '{campaign['name']}' programmée pour {duration} jours")
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
            {"name": "Burger Classic", "price": "12.50€", "cost": "4.20€", "margin": "66.4%", "volume": 145},
            {"name": "Salade César", "price": "9.80€", "cost": "3.10€", "margin": "68.4%", "volume": 89},
            {"name": "Pizza Margherita", "price": "11.00€", "cost": "3.80€", "margin": "65.5%", "volume": 112},
            {"name": "Pâtes Carbonara", "price": "10.50€", "cost": "2.90€", "margin": "72.4%", "volume": 78}
        ]

        for dish in dishes:
            print(f"   • {dish['name']}: {dish['price']} (coût: {dish['cost']}, marge: {dish['margin']}, vol: {dish['volume']})")

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
            choice = self.ui.ask_int("Choisir une action (1-4) ou 0 pour passer: ", min_val=0, max_val=4, default=0)

            if choice == 1:
                amount = self.ui.ask_float("Montant du prêt souhaité (€): ", min_val=1000, max_val=50000, default=10000)
                decisions['loan_request'] = {
                    'amount': amount,
                    'purpose': 'expansion',
                    'estimated_rate': '4.5%'
                }
                self.ui.show_success(f"✅ Demande de prêt de {amount:,.0f}€ enregistrée")

            elif choice == 2:
                equipment_options = [
                    {"name": "Four professionnel", "cost": 8500, "benefit": "+20% capacité"},
                    {"name": "Système de caisse", "cost": 2200, "benefit": "+15% efficacité"},
                    {"name": "Frigo supplémentaire", "cost": 3800, "benefit": "+30% stocks"}
                ]

                print(f"\n🔧 ÉQUIPEMENTS DISPONIBLES:")
                for i, eq in enumerate(equipment_options, 1):
                    print(f"   {i}. {eq['name']}: {eq['cost']}€ ({eq['benefit']})")

                eq_choice = self.ui.ask_int("Choisir équipement (1-3): ", min_val=1, max_val=3, default=1)
                equipment = equipment_options[eq_choice - 1]

                decisions['equipment_purchase'] = {
                    'name': equipment['name'],
                    'cost': equipment['cost'],
                    'benefit': equipment['benefit']
                }
                self.ui.show_success(f"✅ Achat {equipment['name']} programmé")

            elif choice == 3:
                print(f"\n💰 OPTIMISATION TRÉSORERIE:")
                print(f"   • Négocier délais paiement fournisseurs: +2,100€")
                print(f"   • Accélérer encaissements clients: +850€")
                print(f"   • Optimiser niveau stocks: +1,200€")

                decisions['cash_optimization'] = True
                self.ui.show_success("✅ Plan d'optimisation trésorerie activé")

            elif choice == 4:
                investment_amount = self.ui.ask_float("Montant investissement (€): ", min_val=1000, max_val=30000, default=5000)
                expected_return = investment_amount * 0.15  # 15% de retour estimé
                payback_months = investment_amount / (expected_return / 12)

                print(f"\n📊 ANALYSE INVESTISSEMENT:")
                print(f"   Investissement: {investment_amount:,.0f}€")
                print(f"   Retour annuel estimé: {expected_return:,.0f}€")
                print(f"   Retour sur investissement: 15%")
                print(f"   Période de retour: {payback_months:.1f} mois")

                decisions['investment_analysis'] = {
                    'amount': investment_amount,
                    'expected_return': expected_return,
                    'roi': 0.15,
                    'payback_months': payback_months
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
