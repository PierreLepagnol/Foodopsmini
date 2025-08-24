"""
Rapports financiers professionnels pour FoodOps Pro.
"""

from datetime import datetime
from decimal import Decimal

from game_engine.core.ledger import Ledger
from game_engine.domain.restaurant import Restaurant
from game_engine.ui.console_ui import clear_screen, print_box


class FinancialReports:
    """Générateur de rapports financiers professionnels."""

    def show_profit_loss_statement(
        self, restaurant: Restaurant, ledger: Ledger, period: str = "Mois en cours"
    ) -> None:
        """Affiche le compte de résultat professionnel."""
        clear_screen()

        # Récupération des données comptables
        pnl_data = ledger.get_profit_loss()
        balance_data = ledger.get_trial_balance()

        # Calcul des métriques détaillées
        metrics = self._calculate_detailed_metrics(restaurant, pnl_data, balance_data)

        # En-tête du rapport
        header = [
            f"COMPTE DE RÉSULTAT - {restaurant.name.upper()}",
            f"Période: {period}",
            f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            "",
        ]

        # Structure du compte de résultat
        pnl_lines = []

        # PRODUITS D'EXPLOITATION
        pnl_lines.extend(
            [
                "PRODUITS D'EXPLOITATION",
                f"├─ Chiffre d'affaires HT              │ {metrics['ca_ht']:>15.2f} €",
                f"├─ Subventions d'exploitation          │ {metrics['subventions']:>15.2f} €",
                f"└─ TOTAL PRODUITS                      │ {metrics['total_produits']:>15.2f} €",
                "",
            ]
        )

        # CHARGES D'EXPLOITATION
        pnl_lines.extend(
            [
                "CHARGES D'EXPLOITATION",
                f"├─ Achats matières premières          │ {metrics['achats_mp']:>15.2f} €",
                "├─ Charges externes",
                f"│  ├─ Loyer                           │ {metrics['loyer']:>15.2f} €",
                f"│  ├─ Électricité/Gaz                 │ {metrics['energie']:>15.2f} €",
                f"│  ├─ Assurances                      │ {metrics['assurances']:>15.2f} €",
                f"│  ├─ Marketing                       │ {metrics['marketing']:>15.2f} €",
                f"│  └─ Autres charges externes         │ {metrics['autres_externes']:>15.2f} €",
                "├─ Charges de personnel",
                f"│  ├─ Salaires bruts                  │ {metrics['salaires_bruts']:>15.2f} €",
                f"│  └─ Charges sociales                │ {metrics['charges_sociales']:>15.2f} €",
                f"├─ Dotations aux amortissements        │ {metrics['amortissements']:>15.2f} €",
                f"├─ Autres charges d'exploitation       │ {metrics['autres_charges']:>15.2f} €",
                f"└─ TOTAL CHARGES                       │ {metrics['total_charges']:>15.2f} €",
                "",
            ]
        )

        # RÉSULTAT D'EXPLOITATION
        pnl_lines.extend(
            [
                f"RÉSULTAT D'EXPLOITATION                │ {metrics['resultat_exploitation']:>15.2f} €",
                "",
            ]
        )

        # CHARGES FINANCIÈRES
        pnl_lines.extend(
            [
                "CHARGES FINANCIÈRES",
                f"└─ Intérêts d'emprunts                 │ {metrics['interets']:>15.2f} €",
                "",
            ]
        )

        # RÉSULTAT FINAL
        pnl_lines.extend(
            [
                f"RÉSULTAT AVANT IMPÔTS                  │ {metrics['resultat_avant_impots']:>15.2f} €",
                f"└─ Impôts sur les bénéfices           │ {metrics['impots']:>15.2f} €",
                "",
                f"RÉSULTAT NET                           │ {metrics['resultat_net']:>15.2f} €",
            ]
        )

        # Affichage du compte de résultat
        all_lines = header + pnl_lines
        print_box(all_lines, style="info")

        # KPIs métier
        self._show_business_kpis(restaurant, metrics)

        # Analyse et recommandations
        self._show_financial_analysis(metrics)

    def _calculate_detailed_metrics(
        self, restaurant: Restaurant, pnl_data: dict, balance_data: dict
    ) -> dict[str, Decimal]:
        """Calcule les métriques détaillées du compte de résultat."""
        metrics = {}

        # Produits
        metrics["ca_ht"] = pnl_data.get("revenues", Decimal("0"))
        metrics["subventions"] = Decimal("0")  # À implémenter si nécessaire
        metrics["total_produits"] = metrics["ca_ht"] + metrics["subventions"]

        # Charges d'exploitation
        total_expenses = pnl_data.get("expenses", Decimal("0"))

        # Répartition estimée des charges (à améliorer avec plus de détails comptables)
        metrics["achats_mp"] = total_expenses * Decimal(
            "0.30"
        )  # 30% pour matières premières
        metrics["loyer"] = restaurant.rent_monthly
        metrics["energie"] = restaurant.rent_monthly * Decimal("0.15")  # Estimation
        metrics["assurances"] = restaurant.rent_monthly * Decimal("0.05")  # Estimation
        metrics["marketing"] = total_expenses * Decimal("0.03")  # 3% du total
        metrics["autres_externes"] = total_expenses * Decimal("0.07")  # 7% autres

        # Personnel (estimation basée sur les employés)
        total_personnel_cost = sum(
            emp.salary_gross_monthly * Decimal("1.42")  # Brut + charges
            for emp in restaurant.employees
        )
        metrics["salaires_bruts"] = total_personnel_cost / Decimal("1.42")
        metrics["charges_sociales"] = total_personnel_cost - metrics["salaires_bruts"]

        metrics["amortissements"] = restaurant.equipment_value / Decimal("60")  # 5 ans
        metrics["autres_charges"] = total_expenses * Decimal("0.05")  # 5% autres

        metrics["total_charges"] = (
            metrics["achats_mp"]
            + metrics["loyer"]
            + metrics["energie"]
            + metrics["assurances"]
            + metrics["marketing"]
            + metrics["autres_externes"]
            + metrics["salaires_bruts"]
            + metrics["charges_sociales"]
            + metrics["amortissements"]
            + metrics["autres_charges"]
        )

        # Résultats
        metrics["resultat_exploitation"] = (
            metrics["total_produits"] - metrics["total_charges"]
        )
        metrics["interets"] = Decimal("0")  # À implémenter avec les emprunts
        metrics["resultat_avant_impots"] = (
            metrics["resultat_exploitation"] - metrics["interets"]
        )

        # Impôts (estimation 25% si bénéfice)
        if metrics["resultat_avant_impots"] > 0:
            metrics["impots"] = metrics["resultat_avant_impots"] * Decimal("0.25")
        else:
            metrics["impots"] = Decimal("0")

        metrics["resultat_net"] = metrics["resultat_avant_impots"] - metrics["impots"]

        return metrics

    def _show_business_kpis(
        self, restaurant: Restaurant, metrics: dict[str, Decimal]
    ) -> None:
        """Affiche les KPIs métier."""
        ca_ht = metrics["ca_ht"]

        # Calcul des KPIs
        if ca_ht > 0:
            food_cost_pct = metrics["achats_mp"] / ca_ht * 100
            personnel_cost_pct = (
                (metrics["salaires_bruts"] + metrics["charges_sociales"]) / ca_ht * 100
            )
            marge_brute_pct = (ca_ht - metrics["achats_mp"]) / ca_ht * 100
            marge_nette_pct = metrics["resultat_net"] / ca_ht * 100
        else:
            food_cost_pct = personnel_cost_pct = marge_brute_pct = marge_nette_pct = (
                Decimal("0")
            )

        # Ticket moyen estimé
        if (
            hasattr(restaurant, "_last_customers_served")
            and restaurant._last_customers_served > 0
        ):
            ticket_moyen = ca_ht / Decimal(restaurant._last_customers_served)
        else:
            ticket_moyen = Decimal("0")

        # Taux de rotation (estimation)
        if restaurant.capacity_current > 0:
            rotation_rate = Decimal("2.3")  # Valeur par défaut, à calculer réellement
        else:
            rotation_rate = Decimal("0")

        kpis = [
            "KPIs MÉTIER:",
            "",
            f"• Food Cost: {food_cost_pct:.1f}% (Objectif: <30%)",
            f"• Coût personnel: {personnel_cost_pct:.1f}% (Objectif: <35%)",
            f"• Marge brute: {marge_brute_pct:.1f}%",
            f"• Marge nette: {marge_nette_pct:.1f}%",
            f"• Ticket moyen: {ticket_moyen:.2f}€",
            f"• Taux de rotation: {rotation_rate:.1f} (Objectif: >2.0)",
            f"• Capacité utilisée: {restaurant.capacity_current} couverts",
        ]

        # Couleur selon la performance
        if marge_nette_pct > 10:
            style = "success"
        elif marge_nette_pct > 0:
            style = "warning"
        else:
            style = "error"

        print_box(kpis, style=style)

    def _show_financial_analysis(self, metrics: dict[str, Decimal]) -> None:
        """Affiche l'analyse financière et les recommandations."""
        analysis = ["ANALYSE FINANCIÈRE:"]
        recommendations = []

        ca_ht = metrics["ca_ht"]
        resultat_net = metrics["resultat_net"]

        # Analyse de la rentabilité
        if resultat_net > 0:
            analysis.append("✅ Entreprise rentable")
            if resultat_net / ca_ht > Decimal("0.15"):
                analysis.append("✅ Très bonne rentabilité (>15%)")
            elif resultat_net / ca_ht > Decimal("0.08"):
                analysis.append("⚠️ Rentabilité correcte (8-15%)")
            else:
                analysis.append("⚠️ Rentabilité faible (<8%)")
                recommendations.append("Améliorer la marge ou réduire les coûts")
        else:
            analysis.append("❌ Entreprise déficitaire")
            recommendations.append("URGENT: Réduire les charges ou augmenter le CA")

        # Analyse du food cost
        if ca_ht > 0:
            food_cost_pct = metrics["achats_mp"] / ca_ht * 100
            if food_cost_pct > 35:
                analysis.append(f"❌ Food cost trop élevé ({food_cost_pct:.1f}%)")
                recommendations.append("Optimiser les achats et réduire le gaspillage")
            elif food_cost_pct > 30:
                analysis.append(f"⚠️ Food cost limite ({food_cost_pct:.1f}%)")
                recommendations.append("Surveiller les coûts matière")
            else:
                analysis.append(f"✅ Food cost maîtrisé ({food_cost_pct:.1f}%)")

        # Analyse des charges de personnel
        if ca_ht > 0:
            personnel_pct = (
                (metrics["salaires_bruts"] + metrics["charges_sociales"]) / ca_ht * 100
            )
            if personnel_pct > 40:
                analysis.append(
                    f"❌ Charges personnel trop élevées ({personnel_pct:.1f}%)"
                )
                recommendations.append("Optimiser les plannings et la productivité")
            elif personnel_pct > 35:
                analysis.append(f"⚠️ Charges personnel élevées ({personnel_pct:.1f}%)")
            else:
                analysis.append(
                    f"✅ Charges personnel maîtrisées ({personnel_pct:.1f}%)"
                )

        # Affichage de l'analyse
        if analysis:
            print_box(analysis, "DIAGNOSTIC", "info")

        # Affichage des recommandations
        if recommendations:
            rec_lines = ["RECOMMANDATIONS:"] + [f"• {rec}" for rec in recommendations]
            print_box(rec_lines, style="warning")

    def show_cash_flow_statement(self, restaurant: Restaurant, ledger: Ledger) -> None:
        """Affiche le tableau de flux de trésorerie."""
        clear_screen()

        cash_flow = [
            f"TABLEAU DE FLUX DE TRÉSORERIE - {restaurant.name.upper()}",
            "",
            "FLUX DE TRÉSORERIE D'EXPLOITATION",
            f"├─ Résultat net                        │ {Decimal('0'):>15.2f} €",
            f"├─ Amortissements                      │ {Decimal('0'):>15.2f} €",
            f"├─ Variation stocks                    │ {Decimal('0'):>15.2f} €",
            f"├─ Variation créances clients          │ {Decimal('0'):>15.2f} €",
            f"└─ Variation dettes fournisseurs       │ {Decimal('0'):>15.2f} €",
            f"FLUX NET D'EXPLOITATION                │ {Decimal('0'):>15.2f} €",
            "",
            "FLUX DE TRÉSORERIE D'INVESTISSEMENT",
            f"├─ Acquisitions d'immobilisations      │ {Decimal('0'):>15.2f} €",
            f"└─ Cessions d'immobilisations          │ {Decimal('0'):>15.2f} €",
            f"FLUX NET D'INVESTISSEMENT              │ {Decimal('0'):>15.2f} €",
            "",
            "FLUX DE TRÉSORERIE DE FINANCEMENT",
            f"├─ Augmentation de capital             │ {Decimal('0'):>15.2f} €",
            f"├─ Emprunts contractés                 │ {Decimal('0'):>15.2f} €",
            f"└─ Remboursements d'emprunts           │ {Decimal('0'):>15.2f} €",
            f"FLUX NET DE FINANCEMENT                │ {Decimal('0'):>15.2f} €",
            "",
            f"VARIATION DE TRÉSORERIE                │ {Decimal('0'):>15.2f} €",
            f"Trésorerie début de période           │ {Decimal('0'):>15.2f} €",
            f"TRÉSORERIE FIN DE PÉRIODE              │ {restaurant.cash:>15.2f} €",
        ]

        print_box(cash_flow, style="info")

        # Analyse de la trésorerie
        treasury_analysis = [
            "ANALYSE DE TRÉSORERIE:",
            "",
            f"• Trésorerie actuelle: {restaurant.cash:.0f}€",
            f"• Charges fixes mensuelles: {restaurant.rent_monthly + restaurant.fixed_costs_monthly:.0f}€",
            f"• Autonomie financière: {self._calculate_autonomy(restaurant):.1f} mois",
        ]

        if restaurant.cash < restaurant.rent_monthly:
            treasury_analysis.append("❌ ALERTE: Trésorerie insuffisante pour le loyer")
            style = "error"
        elif (
            restaurant.cash
            < (restaurant.rent_monthly + restaurant.fixed_costs_monthly) * 2
        ):
            treasury_analysis.append("⚠️ Trésorerie faible (< 2 mois de charges)")
            style = "warning"
        else:
            treasury_analysis.append("✅ Trésorerie saine")
            style = "success"

        print_box(treasury_analysis, style=style)

    def _calculate_autonomy(self, restaurant: Restaurant) -> Decimal:
        """Calcule l'autonomie financière en mois."""
        monthly_fixed_costs = restaurant.rent_monthly + restaurant.fixed_costs_monthly
        if monthly_fixed_costs > 0:
            return restaurant.cash / monthly_fixed_costs
        return Decimal("999")  # Autonomie "infinie" si pas de charges fixes

    def show_balance_sheet(self, restaurant: Restaurant, ledger: Ledger) -> None:
        """Affiche le bilan comptable."""
        clear_screen()

        balance_sheet = [
            f"BILAN COMPTABLE - {restaurant.name.upper()}",
            "",
            "ACTIF                                  │ PASSIF",
            "                                       │",
            "ACTIF IMMOBILISÉ                       │ CAPITAUX PROPRES",
            f"├─ Fonds de commerce        {Decimal('0'):>10.2f} € │ ├─ Capital social        {Decimal('0'):>10.2f} €",
            f"├─ Matériel & équipement    {restaurant.equipment_value:>10.2f} € │ ├─ Réserves             {Decimal('0'):>10.2f} €",
            f"└─ Amortissements          {Decimal('0'):>10.2f} € │ └─ Résultat de l'exercice {Decimal('0'):>10.2f} €",
            f"TOTAL ACTIF IMMOBILISÉ     {restaurant.equipment_value:>10.2f} € │ TOTAL CAPITAUX PROPRES   {Decimal('0'):>10.2f} €",
            "                                       │",
            "ACTIF CIRCULANT                        │ DETTES",
            f"├─ Stocks                   {Decimal('0'):>10.2f} € │ ├─ Emprunts bancaires    {Decimal('0'):>10.2f} €",
            f"├─ Créances clients         {Decimal('0'):>10.2f} € │ ├─ Dettes fournisseurs   {Decimal('0'):>10.2f} €",
            f"└─ Disponibilités          {restaurant.cash:>10.2f} € │ ├─ Dettes fiscales       {Decimal('0'):>10.2f} €",
            f"TOTAL ACTIF CIRCULANT      {restaurant.cash:>10.2f} € │ └─ Dettes sociales       {Decimal('0'):>10.2f} €",
            "                                       │ TOTAL DETTES             {Decimal('0'):>10.2f} €",
            "                                       │",
            f"TOTAL ACTIF               {restaurant.cash + restaurant.equipment_value:>10.2f} € │ TOTAL PASSIF            {Decimal('0'):>10.2f} €",
        ]

        print_box(balance_sheet, style="info")
