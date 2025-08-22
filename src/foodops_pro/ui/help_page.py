"""Page d'aide en jeu pour les indicateurs clés."""
from .console_ui import ConsoleUI


def show_help_page(ui: ConsoleUI) -> None:
    """Affiche les principaux indicateurs du jeu."""
    ui.clear_screen()
    ui.show_info("📖 AIDE : INDICATEURS CLÉS")

    indicators = [
        ("💰 Trésorerie", "Argent disponible pour payer vos dépenses."),
        ("📈 Chiffre d'affaires", "Revenus générés par les ventes."),
        ("🥘 Coût matière", "Coût des ingrédients utilisés."),
        ("👥 Coût personnel", "Salaires et charges du personnel."),
        ("📊 Marge", "Profit après coûts (objectif 15-25%)."),
        ("😊 Satisfaction client", "Note moyenne > 3.5 pour fidéliser."),
        ("🏪 Taux d'occupation", "Clients servis vs capacité (70-85% idéal)."),
    ]

    for name, desc in indicators:
        print(f"\n{name}\n   {desc}")

    ui.pause()
