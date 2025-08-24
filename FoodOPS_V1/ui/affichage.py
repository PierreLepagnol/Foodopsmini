from FoodOPS_V1.domain.restaurant import Restaurant
from FoodOPS_V1.core.results import TurnResult


def format_to_euro(x: float) -> str:
    """Format a float as a euro currency string (no decimals, thin spaces)."""
    return f"{x:,.0f} €".replace(",", " ").replace(".0", "")


def _pct(a: float, b: float) -> str:
    """Calculate and format a percentage ratio between two values.

    Parameters
    ----------
    a : float
        The numerator value.
    b : float
        The denominator value.

    Returns
    -------
    str
        Formatted percentage string (e.g., " 75.0%").
        Returns "—" if b <= 0 or calculation fails.
    """
    if b <= 0:
        return "—"
    ratio = a / b
    percentage = max(0.0, min(100.0, ratio * 100.0))
    return f"{percentage:5.1f}%"


def _bar(current: int, maxv: int, width: int = 24, fill_char: str = "█") -> str:
    """Generate a text-based progress bar representation.

    Parameters
    ----------
    current : int
        The current value to represent.
    maxv : int
        The maximum possible value (100% fill).
    width : int, optional
        Total width of the bar in characters (default: 24).
    fill_char : str, optional
        Character used to fill the bar (default: "█").

    Returns
    -------
    str
        A string representation of the progress bar.
        Returns empty spaces if maxv <= 0.
    """
    if maxv <= 0:
        return " " * width
    ratio = max(0.0, min(1.0, float(current) / float(maxv)))
    n = int(round(ratio * width))
    return fill_char * n + " " * (width - n)


def _num(x) -> int:
    """Safely convert a value to an integer.

    Parameters
    ----------
    x : Any
        The value to convert to an integer.

    Returns
    -------
    int
        The converted integer value, or 0 if conversion fails.
    """
    try:
        return int(x)
    except Exception:
        return 0


def _posneg(val):
    """Affiche les valeurs positives sans signe, et les négatives avec un signe négatif."""
    return f"{val:,.2f} €".replace(",", " ")


def print_income_statement(cr, title: str):
    print(title)
    CA = _posneg(cr["Chiffre d'affaires (70)"])
    ACHAT_CONSOMME = _posneg(cr["Achats consommés (60)"])
    SERVICES_EXTERIEURS = _posneg(cr["Services extérieurs (61/62)"])
    CHARGES_PERSONNEL = _posneg(cr["Charges de personnel (64)"])
    DOTATIONS_AMORTISSEMENTS = _posneg(cr["Dotations amortissements (68)"])
    RESULTAT_EXPLOITATION = _posneg(cr["Résultat d'exploitation"])
    print("=" * 40)
    print(f"💶 Chiffre d'affaires (70) : {CA}")
    print(f"🛒 Achats consommés (60) : {ACHAT_CONSOMME}")
    print(f"🛠 Services extérieurs (61/62) : {SERVICES_EXTERIEURS}")
    print(f"👥 Charges de personnel (64) : {CHARGES_PERSONNEL}")
    print(f"📉 Dotations amortissements (68) : {DOTATIONS_AMORTISSEMENTS}")
    print("-" * 40)
    print(f"📈 Résultat d'exploitation : {RESULTAT_EXPLOITATION}")
    print("=" * 40)


def print_balance_sheet(balance_sheet):
    print("\n📒 Bilan")
    print("=" * 40)
    print("Actif :")
    print(f"💰 Trésorerie : {_posneg(balance_sheet['Trésorerie'])}")
    print(f"📦 Stock : {_posneg(balance_sheet['Stock'])}")
    print(
        f"🏢 Immobilisations nettes : {_posneg(balance_sheet['Immobilisations nettes'])}"
    )
    print("-" * 40)
    print("Passif :")
    print(f"🏦 Emprunts BPI : {_posneg(balance_sheet['Emprunts BPI'])}")
    print(f"🏦 Emprunts bancaires : {_posneg(balance_sheet['Emprunts bancaires'])}")
    print(f"📊 Capitaux propres : {_posneg(balance_sheet['Capitaux propres'])}")
    print("=" * 40)
    print(f"💰 Trésorerie début : {_posneg(balance_sheet['Trésorerie début'])}")
    print(f"💰 Trésorerie fin : {_posneg(balance_sheet['Trésorerie fin'])}")


def print_opening_balance(restaurant: Restaurant):
    """Print a simple human-readable opening balance for a restaurant.

    Shows the main balance sheet lines at tour 0 to help players understand
    their starting financial position.
    """
    # Solde des comptes à l'ouverture (tour 0)
    bs = restaurant.ledger.balance_sheet(tour_max=0)
    actif = bs.actif
    passif = bs.passif

    print("\n🧾  Bilan d'ouverture —", restaurant.name)
    print("═" * 52)
    print("ACTIF")
    print(f"🏭 Immobilisations (215): {format_to_euro(actif.immobilisations_brutes)}")
    print(f"(-) Amort. cumulés (2815): {format_to_euro(actif.amortissements_cumules)}")
    print(f"= Immobilisations nettes: {format_to_euro(actif.immobilisations_nettes)}")
    print(f"💶 Trésorerie (512): {format_to_euro(actif.trésorerie)}")
    print(f"👉 TOTAL ACTIF: {format_to_euro(actif.total)}")

    print("\nPASSIF")
    print(f"🧱 Capitaux propres (101): {format_to_euro(passif.capitaux_propres)}")
    print(f"🏦 Emprunts (164): {format_to_euro(passif.emprunts)}")
    print(f"👉 TOTAL PASSIF : {format_to_euro(passif.total)}")
    print("═" * 52)


def print_resume_financement(restaurant: Restaurant, financing_plan):
    local = restaurant.local
    equip_default = restaurant.equipment_invest
    plan = financing_plan

    print(f"\n💼 {restaurant.name} — {restaurant.type.value}")
    print(
        f"📍Local: {local.nom} | Capacité: {local.capacite_clients}couverts/jour | Loyer: {format_to_euro(local.loyer)}/mois"
    )
    print(f"🧰Équipementinitial: {format_to_euro(equip_default)}")
    print(
        f"🏦Banque: {format_to_euro(plan.bank_loan)}→Mensualité~{format_to_euro(plan.bank_monthly)}"
    )
    print(
        f"🏛️BPI: {format_to_euro(plan.bpi_loan)}→Mensualité~{format_to_euro(plan.bpi_monthly)}"
    )
    print(f"🧾Fraisdedossier(3%): {format_to_euro(plan.frais_dossier)}")
    print(f"💶Trésoreriededépart: {format_to_euro(plan.cash_initial)}")


# Impression d'un tour


def print_turn_result(resultat_tour: TurnResult) -> None:
    """
    Attend un objet 'tr' (SimpleNamespace ou dataclass) avec au minimum :
      restaurant_name: str
      tour: int
      clients_attr: int
      clients_serv: int
      capacity: int
      price_med: float
      ca: float
      cogs: float
      fixed_costs: float
      marketing: float
      rh_cost: float
      funds_start: float
      funds_end: float
    """

    name = resultat_tour.restaurant_name
    tour = resultat_tour.tour

    # Demande & capacité
    clients_attr = _num(resultat_tour.clients_attribues)
    clients_serv = _num(resultat_tour.clients_serv)
    capacity = _num(resultat_tour.capacity)

    # Prix & ventes
    price_med = float(resultat_tour.price_med)
    ca = float(resultat_tour.ca)
    cogs = float(resultat_tour.cogs)

    # OPEX
    fixed_costs = float(resultat_tour.fixed_costs)
    marketing = float(resultat_tour.marketing)
    rh_cost = float(resultat_tour.rh_cost)

    funds_start = float(resultat_tour.funds_start)
    funds_end = float(resultat_tour.funds_end)

    # KPIs dérivés
    asp = ca / clients_serv if clients_serv > 0 else price_med
    gross_margin = ca - cogs
    opex = fixed_costs + marketing + rh_cost
    operating_result = gross_margin - opex

    # Barres
    cap_bar = _bar(clients_serv, max(1, capacity))
    dem_bar = _bar(clients_serv, max(1, clients_attr))

    print(f"\n{'─' * 76}\n")
    print(f"📊 Résultat — {name} — Tour {tour}")
    print(f"\n{'─' * 76}\n")

    # Ligne demande/capacité
    print(
        f"Demande attribuée : {clients_attr:>6d}   Couvert(s) servi(s) : {clients_serv:>6d}"
    )
    print(
        f"Capacité RH/salle : {capacity:>6d}   Utilisation capacité : {_pct(clients_serv, capacity):>6}"
    )
    print(f"Couverture demande: {_pct(clients_serv, clients_attr):>6}")
    print(f"[{cap_bar}] Capacité")
    print(f"[{dem_bar}] Demande  ")

    # Prix & CA
    print(
        f"\n  Prix médian menu : {format_to_euro(price_med):>12}   Ticket moyen (réel) : {format_to_euro(asp):>12}"
    )
    print(f"Chiffre d'affaires: {format_to_euro(ca):>12}")

    # COGS & marge
    print(f"COGS (coût prod)  : {format_to_euro(cogs):>12}")
    print(
        f"Marge brute       : {format_to_euro(gross_margin):>12}   (taux: {_pct(gross_margin, ca)})"
    )

    # OPEX
    print(f"\n  Coûts fixes       : {format_to_euro(fixed_costs):>12}")
    print(f"Marketing         : {format_to_euro(marketing):>12}")
    print(f"Masse salariale   : {format_to_euro(rh_cost):>12}")
    print(f"OPEX total        : {format_to_euro(opex):>12}")

    # Résultat opé
    print(f"\n  Résultat opé.     : {format_to_euro(operating_result):>12}")

    # Tréso
    print(f"\n  Trésorerie début  : {format_to_euro(funds_start):>12}")
    print(f"Trésorerie fin    : {format_to_euro(funds_end):>12}")

    print(f"{'─' * 76}\n")

    # --- Affichage bonus : pertes de clients ---
    losses = resultat_tour.losses
    if isinstance(losses, dict) and losses.get("lost_total", 0) > 0:
        print(f"\n ⚠ Pertes clients : {losses['lost_total']}")
        print(f"\t- Stock insuffisant : {losses['lost_stock']}")
        print(f"\t- Capacité limitée  : {losses['lost_capacity']}")
        print(f"\t- Autres raisons    : {losses['lost_other']}")


def print_multi_summary(rows: list) -> None:
    """
    Affiche un tableau compact pour plusieurs restaurants sur un tour.
    Chaque 'row' doit contenir au moins:
      name, ca, cogs, opex, result
    """
    if not rows:
        return
    print("\n================= Synthèse par restaurant =================")
    print(f"{'Restaurant':30} {'CA':>12} {'COGS':>12} {'OPEX':>12} {'Rés.opé.':>12}")
    print("-" * 84)
    for r in rows:
        name = str(r.get("name", ""))[:30]
        ca = format_to_euro(r.get("ca", 0.0))
        cogs = format_to_euro(r.get("cogs", 0.0))
        opex = format_to_euro(r.get("opex", 0.0))
        res = format_to_euro(r.get("result", 0.0))
        print(f"{name:30} {ca:>12} {cogs:>12} {opex:>12} {res:>12}")
    print("===========================================================\n")
