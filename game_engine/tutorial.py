"""
Tutoriel interactif
"""

from game_engine.console_ui import ConsoleUI


class InteractiveTutorial:
    """Tutoriel interactif pour apprendre FoodOps Pro."""

    def __init__(self, ui: ConsoleUI):
        self.ui = ui
        self.current_step = 0
        self.tutorial_data = self._load_tutorial_steps()

    def _load_tutorial_steps(self) -> list[dict]:
        """Charge les étapes du tutoriel."""
        return [
            {
                "title": "🎮 Bienvenue dans FoodOps Pro !",
                "content": [
                    "Félicitations ! Vous venez d'acquérir votre premier restaurant.",
                    "",
                    "🎯 VOTRE MISSION:",
                    "• Gérer un restaurant rentable",
                    "• Satisfaire vos clients",
                    "• Battre la concurrence",
                    "• Développer votre réputation",
                    "",
                    "📚 Ce tutoriel vous apprendra les bases en 5 étapes simples.",
                ],
                "action": "Appuyez sur Entrée pour commencer",
                "interactive": False,
            },
            {
                "title": "💰 Étape 1: Comprendre vos finances",
                "content": [
                    "Votre restaurant a un budget de départ de 10,000€.",
                    "",
                    "📊 INDICATEURS CLÉS:",
                    "• Chiffre d'affaires = Prix × Nombre de clients",
                    "• Coûts = Matières premières + Personnel + Charges",
                    "• Profit = Chiffre d'affaires - Coûts",
                    "",
                    "🎯 OBJECTIF: Réaliser un profit positif chaque tour !",
                    "",
                    "💡 CONSEIL: Surveillez votre marge (profit/CA).",
                    "   Une bonne marge se situe entre 15% et 25%.",
                ],
                "action": "Tapez 'compris' pour continuer",
                "interactive": True,
                "expected": "compris",
            },
            {
                "title": "🍽️ Étape 2: Fixer vos prix",
                "content": [
                    "Le prix est votre principal levier stratégique.",
                    "",
                    "📈 IMPACT DU PRIX:",
                    "• Prix bas = Plus de clients, moins de marge",
                    "• Prix élevé = Moins de clients, plus de marge",
                    "",
                    "🎯 SEGMENTS DE CLIENTÈLE:",
                    "• Étudiants: Budget 11€, aiment les prix bas",
                    "• Familles: Budget 17€, équilibre prix/qualité",
                    "• Foodies: Budget 25€, privilégient la qualité",
                    "",
                    "💡 CONSEIL: Commencez par 12-15€ pour tester le marché.",
                ],
                "action": "Quel prix recommanderiez-vous pour débuter ? (10-20€)",
                "interactive": True,
                "validation": lambda x: 10 <= float(x) <= 20,
                "feedback": "Excellent choix ! Un prix entre 12-15€ est idéal pour débuter.",
            },
            {
                "title": "⭐ Étape 3: Gérer la qualité",
                "content": [
                    "La qualité différencie votre restaurant de la concurrence.",
                    "",
                    "🌟 NIVEAUX DE QUALITÉ:",
                    "• 1⭐ Économique: -30% coût, -20% satisfaction",
                    "• 2⭐ Standard: Prix de référence",
                    "• 3⭐ Supérieur: +25% coût, +15% satisfaction",
                    "• 4⭐ Premium: +50% coût, +30% satisfaction",
                    "• 5⭐ Luxe: +100% coût, +50% satisfaction",
                    "",
                    "🎯 STRATÉGIES:",
                    "• Économique: Volume maximum, prix bas",
                    "• Premium: Marge élevée, clientèle fidèle",
                    "",
                    "💡 CONSEIL: La qualité 3⭐ offre le meilleur équilibre.",
                ],
                "action": "Quelle stratégie préférez-vous ? (economique/premium/equilibre)",
                "interactive": True,
                "validation": lambda x: x.lower()
                in ["economique", "premium", "equilibre"],
                "feedback": "Bonne réflexion ! Chaque stratégie a ses avantages selon le marché.",
            },
            {
                "title": "👥 Étape 4: Optimiser votre personnel",
                "content": [
                    "Votre équipe détermine la capacité de votre restaurant.",
                    "",
                    "🏢 NIVEAUX DE PERSONNEL:",
                    "• Niveau 1: Équipe réduite, 120 clients max",
                    "• Niveau 2: Équipe normale, 150 clients max",
                    "• Niveau 3: Équipe renforcée, 180 clients max",
                    "",
                    "💰 COÛTS:",
                    "• Plus de personnel = Plus de capacité = Plus de coûts",
                    "• Équilibrez selon votre demande attendue",
                    "",
                    "⚠️ ATTENTION: Trop de personnel = Coûts inutiles",
                    "              Pas assez = Clients refusés",
                    "",
                    "💡 CONSEIL: Commencez par le niveau 2, ajustez ensuite.",
                ],
                "action": "Combien de clients pensez-vous servir au début ? (80-200)",
                "interactive": True,
                "validation": lambda x: 80 <= int(x) <= 200,
                "feedback": "Parfait ! Adaptez votre personnel à cette prévision.",
            },
            {
                "title": "🎯 Étape 5: Analyser vos résultats",
                "content": [
                    "Après chaque tour, analysez vos performances.",
                    "",
                    "📊 INDICATEURS À SURVEILLER:",
                    "• Clients servis vs capacité (taux d'occupation)",
                    "• Satisfaction client (objectif: > 3.5/5)",
                    "• Part de marché (votre position vs concurrents)",
                    "• Marge nette (objectif: 15-25%)",
                    "",
                    "🔍 QUESTIONS À SE POSER:",
                    "• Pourquoi ai-je gagné/perdu des clients ?",
                    "• Ma stratégie est-elle cohérente ?",
                    "• Comment améliorer ma performance ?",
                    "",
                    "💡 CONSEIL: Changez UN paramètre à la fois pour",
                    "   comprendre son impact.",
                ],
                "action": "Êtes-vous prêt à gérer votre restaurant ? (oui/non)",
                "interactive": True,
                "expected": "oui",
            },
            {
                "title": "🎉 Félicitations !",
                "content": [
                    "Vous maîtrisez maintenant les bases de FoodOps Pro !",
                    "",
                    "🎯 RÉCAPITULATIF:",
                    "✓ Finances: Surveillez profit et marge",
                    "✓ Prix: Équilibrez volume et rentabilité",
                    "✓ Qualité: Différenciez-vous de la concurrence",
                    "✓ Personnel: Adaptez la capacité à la demande",
                    "✓ Analyse: Apprenez de chaque tour",
                    "",
                    "🚀 PROCHAINES ÉTAPES:",
                    "• Lancez votre première partie",
                    "• Expérimentez différentes stratégies",
                    "• Découvrez les fonctionnalités avancées",
                    "",
                    "💡 ASTUCE: Consultez l'aide (?) à tout moment !",
                    "",
                    "Bonne chance, futur entrepreneur ! 🍔",
                ],
                "action": "Appuyez sur Entrée pour terminer le tutoriel",
                "interactive": False,
            },
        ]

    def start_tutorial(self) -> bool:
        """
        Lance le tutoriel interactif.

        Returns:
            True si le tutoriel est terminé, False si abandonné
        """
        clear_screen()
        show_info("🎓 TUTORIEL INTERACTIF FOODOPS PRO")

        print("\n📚 Ce tutoriel vous apprendra à jouer en 5 minutes.")
        print("💡 Vous pouvez quitter à tout moment en tapant 'quit'.")

        if not ask_yes_no("\nCommencer le tutoriel ?", default=True):
            return False

        for i, step in enumerate(self.tutorial_data):
            if not self._show_step(step, i + 1):
                return False

        return True

    def _show_step(self, step: dict, step_number: int) -> bool:
        """
        Affiche une étape du tutoriel.

        Args:
            step: Données de l'étape
            step_number: Numéro de l'étape

        Returns:
            True pour continuer, False pour quitter
        """
        clear_screen()

        # Afficher le titre avec numéro d'étape
        title = f"{step['title']} ({step_number}/{len(self.tutorial_data)})"
        show_info(title)

        # Afficher le contenu
        for line in step["content"]:
            print(f"   {line}")

        # Gestion de l'interaction
        if step["interactive"]:
            return self._handle_interactive_step(step)
        else:
            input(f"   {step['action']}")
            return True

    def _handle_interactive_step(self, step: dict) -> bool:
        """Gère une étape interactive."""
        while True:
            response = input(f"   {step['action']}: ").strip()

            if response.lower() == "quit":
                return False

            # Validation spécifique
            if "validation" in step:
                if step["validation"](response):
                    if "feedback" in step:
                        print(f"   ✅ {step['feedback']}")
                    input("\n   Appuyez sur Entrée pour continuer...")
                    return True
                else:
                    print("   ❌ Réponse invalide, essayez encore.")
                    continue

            # Validation par réponse attendue
            if "expected" in step:
                if response.lower() == step["expected"].lower():
                    print("   ✅ Parfait !")
                    input("\n   Appuyez sur Entrée pour continuer...")
                    return True
                else:
                    print(f"   💡 Tapez '{step['expected']}' pour continuer.")
                    continue

            # Pas de validation spécifique
            return True

    def show_quick_help(self) -> None:
        """Affiche une aide rapide."""
        clear_screen()
        show_info("❓ AIDE RAPIDE FOODOPS PRO")

        help_sections = {
            "🎯 OBJECTIF": ["Gérer un restaurant rentable et battre la concurrence"],
            "💰 FINANCES": [
                "• Profit = Chiffre d'affaires - Coûts",
                "• Objectif marge: 15-25%",
                "• Surveillez votre trésorerie",
            ],
            "🍽️ STRATÉGIE PRIX": [
                "• Prix bas = Plus de clients, moins de marge",
                "• Prix élevé = Moins de clients, plus de marge",
                "• Segments: Étudiants (11€), Familles (17€), Foodies (25€)",
            ],
            "⭐ QUALITÉ": [
                "• 1⭐ Économique → 5⭐ Luxe",
                "• Plus de qualité = Plus de coûts + Plus de satisfaction",
                "• Différenciation concurrentielle",
            ],
            "👥 PERSONNEL": [
                "• Niveau 1: 120 clients max",
                "• Niveau 2: 150 clients max",
                "• Niveau 3: 180 clients max",
            ],
            "📊 INDICATEURS": [
                "• Satisfaction client: > 3.5/5",
                "• Taux d'occupation: 70-85%",
                "• Part de marché: Position vs concurrents",
            ],
        }

        for section, items in help_sections.items():
            print(f"\n{section}:")
            for item in items:
                print(f"   {item}")

        pause()

    def show_strategy_tips(self) -> None:
        """Affiche des conseils stratégiques."""
        clear_screen()
        show_info("💡 CONSEILS STRATÉGIQUES")

        tips = [
            {
                "title": "🎯 DÉBUTANT",
                "tips": [
                    "Commencez par prix 12-15€, qualité 2-3⭐",
                    "Observez vos concurrents et adaptez-vous",
                    "Changez UN paramètre à la fois",
                    "Visez 15-20% de marge nette",
                ],
            },
            {
                "title": "📈 INTERMÉDIAIRE",
                "tips": [
                    "Analysez quel segment vous rapporte le plus",
                    "Ajustez votre stratégie selon les événements",
                    "Investissez dans le marketing si rentable",
                    "Surveillez votre réputation",
                ],
            },
            {
                "title": "🏆 EXPERT",
                "tips": [
                    "Anticipez les réactions de la concurrence",
                    "Optimisez votre mix qualité/prix/personnel",
                    "Profitez des événements saisonniers",
                    "Développez une stratégie long terme",
                ],
            },
        ]

        for tip_group in tips:
            print(f"\n{tip_group['title']}:")
            for tip in tip_group["tips"]:
                print(f"   • {tip}")

        pause()
