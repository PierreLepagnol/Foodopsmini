# foodops/ui/director_office.py


from FoodOPS_V1.domain.restaurant import Restaurant

from FoodOPS_V1.ui.director_recipes import run_recipes_shop


def format_currency_eur(amount: float) -> str:
    """
    Format a float amount as a Euro currency string with proper formatting.

    Args:
        amount: The monetary amount to format

    Returns:
        A formatted string like "1 500 €" or "0 €"

    Examples:
        >>> format_currency_eur(1500.0)
        "1 500 €"
        >>> format_currency_eur(0.0)
        "0 €"
    """
    return f"{amount:,.0f} €".replace(",", " ").replace(".0", "")


def _prompt_float(prompt: str, default: float = 0.0) -> float:
    """
    Read a number from stdin and parse it as a float.

    - Accepts both dot and comma as decimal separators
    - Returns the provided default if parsing fails or input is empty

    Args:
        prompt: Message shown to the user before reading input
        default: Fallback value when the input cannot be parsed

    Returns:
        The parsed float or the default value
    """
    # Accept comma as decimal separator to be friendly with French inputs
    try:
        s = input(prompt).strip().replace(",", ".")
        return float(s)
    except Exception:
        return default


def _prompt_int(prompt: str, default: int = 0) -> int:
    """
    Read a number from stdin and parse it as an integer.

    - Trims whitespace
    - Returns the provided default if parsing fails or input is empty

    Args:
        prompt: Message shown to the user before reading input
        default: Fallback value when the input cannot be parsed

    Returns:
        The parsed integer or the default value
    """
    try:
        return int(input(prompt).strip())
    except Exception:
        return default


# def _ensure_hr_fields(r:Restaurant):
#     """
#     Ensure the restaurant-like object `r` exposes expected HR/ops fields.

#     This avoids AttributeError later by creating attributes with sensible
#     defaults only when they are missing on the object.
#     """
#     # Team list: simple list of employee objects
#     if not hasattr(r, "equipe"):
#         r.equipe = []
#     # Global salary delta applied to all salaries (e.g., market alignment)
#     if not hasattr(r, "hr_salary_delta"):
#         r.hr_salary_delta = 0.0  # % global vs marché
#     # Monthly marketing budget (used to nudge notoriety and overheads)
#     if not hasattr(r, "marketing_budget"):
#         r.marketing_budget = 0.0
#     # Menu pricing markup relative to recommended/base prices
#     if not hasattr(r, "pricing_markup"):
#         r.pricing_markup = 0.0  # % appliqué sur les prix conseillés
#     # Quality and service indices used in simple demand heuristics
#     if not hasattr(r, "quality_index"):
#         r.quality_index = 0.6
#     if not hasattr(r, "service_index"):
#         r.service_index = 0.6


def _hr_cost_month(r) -> float:
    """
    Compute a simplified monthly HR cost for the current team.

    Sums each employee's `salaire_mensuel` and applies the global
    `hr_salary_delta` adjustment.

    Returns:
        Total monthly HR cost rounded to two decimals
    """
    # Somme brute simplifiée
    total = 0.0
    for emp in r.equipe:
        total += getattr(emp, "salaire_mensuel", 0.0)
    # Ajustement global
    total *= 1.0 + getattr(r, "hr_salary_delta", 0.0)
    return round(total, 2)


def _show_team(r: Restaurant):
    """
    Print a compact view of the team and the current monthly cost.
    """
    print("\n--- Équipe actuelle ---")
    if not r.equipe:
        print("(vide)")
    else:
        for i, emp in enumerate(r.equipe, 1):
            sal = getattr(emp, "salaire_mensuel", 0.0)
            print(
                f"{i}. {emp.nom} {emp.prenom} - {emp.poste} - {format_currency_eur(sal)}"
            )
    print("-" * 23)
    print(f"Coût mensuel: {format_currency_eur(_hr_cost_month(r))}")


# ——— Actions ———


def _action_recruter(r: Restaurant):
    """
    Interactive recruitment flow using a minimal fictional candidate pool.

    Lets the user select a candidate and propose a salary. The candidate
    accepts if the proposal is at least 97% of their reference salary.
    On success, a lightweight employee object is appended to `r.equipe`.
    """
    # Faux vivier minimaliste
    pool = [
        {
            "nom": "Alex",
            "prenom": "Roux",
            "poste": "Équipier polyvalent",
            "salaire_mensuel": 1550,
        },
        {
            "nom": "Marie",
            "prenom": "Lefevre",
            "poste": "Serveur",
            "salaire_mensuel": 1650,
        },
        {
            "nom": "Karim",
            "prenom": "Garcia",
            "poste": "Manager",
            "salaire_mensuel": 2500,
        },
        {
            "nom": "Sophie",
            "prenom": "Bernard",
            "poste": "Plongeur",
            "salaire_mensuel": 1500,
        },
        {
            "nom": "Lucas",
            "prenom": "Petit",
            "poste": "Cuisinier",
            "salaire_mensuel": 1900,
        },
    ]
    for i, c in enumerate(pool, 1):
        print(
            f"{i}. {c['nom']} {c['prenom']} - {c['poste']} - {format_currency_eur(c['salaire_mensuel'])}/mois"
        )
    idx = _prompt_int("Sélectionnez un candidat: ", 0)
    if 1 <= idx <= len(pool):
        c = pool[idx - 1]
        prop = _prompt_float("Salaire proposé: ", c["salaire_mensuel"])
        # Simple acceptance rule: candidate accepts if offer is close to reference
        seuil = c["salaire_mensuel"] * 0.97
        if prop >= seuil:
            # Register the newly hired employee (lightweight ad-hoc object)
            emp = type("Emp", (), {})()
            emp.nom = c["nom"]
            emp.prenom = c["prenom"]
            emp.poste = c["poste"]
            emp.salaire_mensuel = prop
            r.equipe.append(emp)
            print("Embauche réussie!")
        else:
            print("Refusé.")
    else:
        print("Annulé.")


def _action_licencier(r: Restaurant):
    """
    Interactive flow to fire an employee from the team.

    Removes the selected employee from `r.equipe` and applies a simplified
    severance cost equal to 50% of their monthly salary, deducted from funds.
    """
    if not r.equipe:
        print("Aucun salarié.")
        return
    _show_team(r)
    idx = _prompt_int("Qui licencier ? (numéro) ", 0)
    if 1 <= idx <= len(r.equipe):
        emp = r.equipe.pop(idx - 1)
        # Simplified severance cost: half a month of salary
        cout = getattr(emp, "salaire_mensuel", 0.0) * 0.5
        r.funds -= cout
        print(f"{emp.nom} {emp.prenom} licencié. Coût: {format_currency_eur(cout)}")
    else:
        print("Annulé.")


def _action_ajuster_salaires(r: Restaurant):
    """
    Set a global salary delta for the team.

    Asks for a percentage adjustment and clamps it between -10% and +10%.
    This value is used by `_hr_cost_month` when computing HR costs.
    """
    delta = (
        _prompt_float("Ajustement global salaires en % (ex: 5 ou -5): ", 0.0) / 100.0
    )
    r.hr_salary_delta = max(-0.1, min(0.1, delta))  # borne +/-10%
    print(f"Delta salaires appliqué: {r.hr_salary_delta * 100:.1f}%")


def _action_marketing(r: Restaurant):
    """
    Configure the monthly marketing budget and its effects.

    - Stores the budget on `r.marketing_budget`
    - Adds the amount to `r.overheads["autres"]` so it impacts the P&L
    - Slightly increases `r.notoriety` with a diminishing cap
    """
    budget = _prompt_float(
        "Budget marketing mensuel (€): ", getattr(r, "marketing_budget", 0.0)
    )
    budget = max(0.0, budget)
    r.marketing_budget = budget
    # On met ça dans overheads['autres'] pour que ça impacte le compte de résultat
    r.overheads["autres"] = r.overheads.get("autres", 0.0) + budget
    # Petit boost de notoriété plafonné
    r.notoriety = min(
        1.0, getattr(r, "notoriety", r.notoriety) + min(0.05, budget / 20000.0)
    )
    print(
        f"Marketing mensuel: {format_currency_eur(budget)} — Notoriété: {r.notoriety:.2f}"
    )


def _action_prix_menu(r: Restaurant):
    """
    Configure the menu pricing markup.

    Reads a percentage from the user, converts it to a 0.0-1.0 ratio, and
    stores it on `r.pricing_markup` (clamped between 0% and 100%).
    """
    mk = (
        _prompt_float(
            "Markup prix menu en % (ex: 0, 10, 25): ",
            getattr(r, "pricing_markup", 0.0) * 100,
        )
        / 100.0
    )
    r.pricing_markup = max(0.0, min(1.0, mk))  # 0% à 100%
    print(f"Markup menu réglé à {r.pricing_markup * 100:.0f}%")


def _action_maintenance_qualite(r: Restaurant):
    """
    One-off spending to improve the quality index.

    Deducts `spend` from `r.funds` and increases `r.quality_index` with a
    small capped gain. Does nothing if no spending is entered.
    """
    spend = _prompt_float("Budget maintenance/qualité ce tour (€): ", 0.0)
    if spend > 0:
        r.funds -= spend
        r.quality_index = min(
            1.0, getattr(r, "quality_index", 0.6) + min(0.08, spend / 25000.0)
        )
        print(
            f"Qualité: {r.quality_index:.2f} — Trésorerie: {format_currency_eur(r.funds)}"
        )
    else:
        print("Aucun changement.")


def _action_formation_service(r: Restaurant):
    """
    One-off spending to improve the service index.

    Deducts `spend` from `r.funds` and increases `r.service_index` with a
    small capped gain. Does nothing if no spending is entered.
    """
    spend = _prompt_float("Budget formation service ce tour (€): ", 0.0)
    if spend > 0:
        r.funds -= spend
        r.service_index = min(
            1.0, getattr(r, "service_index", 0.6) + min(0.08, spend / 25000.0)
        )
        print(
            f"Service: {r.service_index:.2f} — Trésorerie: {format_currency_eur(r.funds)}"
        )
    else:
        print("Aucun changement.")


def _action_recapacity_rh(r: Restaurant):
    """
    Display a quick recap of the HR situation (team and monthly cost).
    """
    _show_team(r)


# ——— Entrée principale ———


def bureau_directeur(equipe, type_resto, resto=None, current_tour=1):
    """
    Interactive CLI for the director's office.

    Presents a simple menu to manage team, salaries, marketing, pricing,
    and one-off quality/service actions. The function manipulates a
    restaurant-like object `r` kept as an attribute on this function to
    maintain state across calls within the same run.

    Args:
        equipe: Legacy parameter kept for backward compatibility (team list)
        type_resto: Restaurant type identifier (unused here but kept for API)
        resto: Full restaurant object when available (used by recipes shop)
        current_tour: Current turn number, forwarded to the recipes shop

    Returns:
        The current team list (`r.equipe`) for backward compatibility.
    """
    # si tu as accès à l'objet resto, passe-le directement (equipe restera dans resto)
    # r est injecté par game.py : on manipule l'objet directement
    # Ici, on retourne seulement l'équipe (back-compat de l'appel existant).
    current_restaurant = getattr(bureau_directeur, "_r", None)
    if current_restaurant is None:
        # Fallback lightweight container used when a full restaurant object
        # is not provided by the caller
        class Dummy:
            equipe = []
            # equipe = equipe or []
            funds = 0.0
            notoriety = 0.5
            overheads = {"autres": 0.0}
            local = type("L", (), {"visibility": 1.0})()

        bureau_directeur._r = Dummy()
    r = bureau_directeur._r
    # _ensure_hr_fields(r)

    while True:
        print("\n=== Bureau du Directeur ===")
        print("1. Voir équipe")
        print("2. Recruter")
        print("3. Licencier")
        print("4. Ajuster salaires (global)")
        print("5. Budget marketing")
        print("6. Politique de prix (markup)")
        print("7. Maintenance / Qualité")
        print("8. Formation service")
        print("9. Récap RH")
        print("0. Quitter bureau")
        choice = input("> ").strip()

        if choice == "1":
            _show_team(r)
        elif choice == "2":
            _action_recruter(r)
        elif choice == "3":
            _action_licencier(r)
        elif choice == "4":
            _action_ajuster_salaires(r)
        elif choice == "5":
            _action_marketing(r)
        elif choice == "6":
            run_recipes_shop(resto, current_tour)
            # tu dois faire passer current_tour depuis game.py
        elif choice == "7":
            _action_maintenance_qualite(r)
        elif choice == "8":
            _action_formation_service(r)
        elif choice == "9":
            _action_recapacity_rh(r)
        elif choice == "0":
            break
        else:
            print("Choix invalide.")

    return r.equipe
