from typing import List, Tuple

from FoodOPS_V1.core.accounting import Ledger
from FoodOPS_V1.core.market import allocate_customers_to_restaurants, clamp_capacity
from game_engine.domain.local_VO import CATALOG_LOCALS
from FoodOPS_V1.domain.restaurant_VO import Restaurant, make_restaurant
from game_engine.domain.types_VO import RestaurantType
from FoodOPS_V1.domain.scenario_VO import Scenario, propose_financing
from FoodOPS_V1.ui.affichage import (
    print_balance_sheet,
    print_income_statement,
    print_opening_balance,
    print_resume_financement,
    print_turn_result,
)
from FoodOPS_V1.ui.director_office import bureau_directeur
from game_engine.utilsV0 import get_input
from FoodOPS_V1.core.results import TurnResult
from FoodOPS_V1.rules.recipe_factory import build_menu_for_type


def initialisation_restaurants() -> List[Restaurant]:
    """Crée interactivement les restaurants joueurs avec financement et comptabilité.

    Saisit le nombre de joueurs, puis pour chaque joueur :
    - Type de restaurant (Fast Food, Bistrot, Gastro)
    - Sélection automatique du local et équipement
    - Calcul du plan de financement
    - Initialisation de la comptabilité avec écriture d'ouverture
    - Affichage du résumé financier et bilan initial

    Returns:
        Liste des restaurants initialisés et prêts à jouer
    """
    restaurants = []

    # Saisie du nombre de joueurs ici (la CLI n'envoie plus le param)
    nb_joueurs = int(
        get_input(
            input_message="Nombre de joueurs (1-8) : ",
            error_message="⚠️ Saisis un entier entre 1 et 8.",
            fn_validation=lambda x: 1 <= x <= 8,
        )
    )
    for i in range(nb_joueurs):
        print(f"\n— Joueur {i + 1} —")
        print("Types : 1) Fast Food  2) Bistrot  3) GASTRO")
        type = get_input(
            input_message="Type de restaurant : ",
            error_message="⚠️ Choisis 1, 2 ou 3.",
            fn_validation=lambda x: x in (1, 2, 3),
        )

        type_dict = {1: "FAST_FOOD", 2: "BISTRO", 3: "GASTRO"}
        type_resto = type_dict[type]

        # Sélection du local (simple: premier de la liste pour ce type)
        local = CATALOG_LOCALS[0]

        # Équipement par défaut selon type (tu pourras affiner)

        equip_default_dict = {
            "FAST_FOOD": 80_000.0,
            "BISTRO": 120_000.0,
            "Gastro": 180_000.0,
        }
        equip_default = equip_default_dict[type_resto]

        # Plan de financement selon règles admin
        plan = propose_financing(local.prix_fond, equip_default)

        menus_by_type = build_menu_for_type(RestaurantType[type_resto])
        # Création du restaurant
        restaurant = Restaurant(
            name=f"Resto {i + 1}",
            type=RestaurantType[type_resto],
            local=local,
            funds=plan.cash_initial,  # trésorerie après financement - investissement - frais
            equipment_invest=equip_default,
            menu=menus_by_type[RestaurantType[type_resto]],
            notoriety=0.5,
            monthly_bpi=plan.bpi_monthly,
            monthly_bank=plan.bank_monthly,
            bpi_outstanding=plan.bpi_outstanding,
            bank_outstanding=plan.bank_outstanding,
        )

        # Initialiser la compta + écriture d'ouverture
        restaurant.ledger = Ledger()
        restaurant.post_opening()

        # Résumé financement et bilan d'ouverture
        print_resume_financement(restaurant, plan)
        print_opening_balance(restaurant)

        restaurants.append(restaurant)

    return restaurants


def initialisation_restaurants_auto(
    nb_joueurs: int = 1, types: List[str | RestaurantType] | None = None
) -> List[Restaurant]:
    """Initialise automatiquement une liste de restaurants joueurs.

    Crée `nb_joueurs` restaurants sans interaction, en effectuant pour chacun:
    - Sélection du type (cyle FAST_FOOD → BISTRO → GASTRO par défaut)
    - Sélection d'un local par défaut (1er du catalogue)
    - Détermination d'un investissement équipement par type
    - Calcul du plan de financement et trésorerie initiale
    - Initialisation du grand livre et écriture d'ouverture
    - Génération d'un menu adapté au concept
    - Affichage du résumé de financement et du bilan d'ouverture

    Args:
        nb_joueurs: Nombre de restaurants à créer (>=1)
        types: Optionnel, liste de types ("FAST_FOOD" | "BISTRO" | "GASTRO" ou RestaurantType)
               utilisés séquentiellement et cyclés si la liste est plus courte que `nb_joueurs`.

    Returns:
        Liste de restaurants initialisés et prêts à jouer.
    """
    assert nb_joueurs >= 1, "nb_joueurs doit être >= 1"

    def _normalize_type(t: str | RestaurantType) -> RestaurantType:
        if isinstance(t, RestaurantType):
            return t
        # autoriser soit le name (FAST_FOOD), soit la value ("FAST_FOOD")
        try:
            return RestaurantType[t]
        except Exception:
            # ultime tentative par value
            for m in RestaurantType:
                if m.value == t:
                    return m
            raise ValueError(f"Type de restaurant invalide: {t}")

    cycle = [RestaurantType.FAST_FOOD, RestaurantType.BISTRO, RestaurantType.GASTRO]
    chosen_types: List[RestaurantType] = []
    if types:
        normalized = [_normalize_type(t) for t in types]
        for i in range(nb_joueurs):
            chosen_types.append(normalized[i % len(normalized)])
    else:
        for i in range(nb_joueurs):
            chosen_types.append(cycle[i % len(cycle)])

    equip_default_by_type = {
        RestaurantType.FAST_FOOD: 80_000.0,
        RestaurantType.BISTRO: 120_000.0,
        RestaurantType.GASTRO: 180_000.0,
    }

    restaurants: List[Restaurant] = []
    for i in range(nb_joueurs):
        rtype = chosen_types[i]

        # Local par défaut (premier de la liste)
        local = CATALOG_LOCALS[0]

        equip_default = float(equip_default_by_type[rtype])

        # Plan de financement
        plan = propose_financing(local.prix_fond, equip_default)

        # Création du restaurant spécialisé via la factory
        restaurant = make_restaurant(
            kind=rtype,
            name=f"Resto {i + 1}",
            local=local,
            notoriety=0.5,
            funds=plan.cash_initial,
            equipment_invest=equip_default,
            monthly_bpi=plan.bpi_monthly,
            monthly_bank=plan.bank_monthly,
            bpi_outstanding=plan.bpi_outstanding,
            bank_outstanding=plan.bank_outstanding,
        )

        # Taux d'intérêt indicatifs (alignés avec propose_financing)
        restaurant.bpi_rate_annual = 0.025
        restaurant.bank_rate_annual = 0.045

        # Comptabilité: grand livre + écriture d'ouverture
        restaurant.ledger = Ledger()
        restaurant.post_opening(plan)

        # Menu adapté au concept
        restaurant.menu = build_menu_for_type(restaurant)

        # Résumés
        print_resume_financement(restaurant, plan)
        print_opening_balance(restaurant)

        restaurants.append(restaurant)

    return restaurants


DISPLAY_COMPTA = False


def _sell_from_finished_fifo(
    restaurant: Restaurant, quantity: int
) -> Tuple[int, float]:
    """Vend jusqu'à `quantity` portions depuis l'inventaire produits finis en FIFO.

    Traite l'inventaire par ordre chronologique (premier entré, premier sorti),
    met à jour les quantités en stock et calcule le chiffre d'affaires total.

    Args:
        restaurant: Restaurant avec l'inventaire à traiter
        quantity: Nombre maximum de portions à vendre (doit être >= 0)

    Returns:
        Tuple contenant:
        - int: Nombre total de portions effectivement vendues
        - float: Chiffre d'affaires total généré (arrondi à 2 décimales)

    Note:
        Les lots vides sont automatiquement supprimés de l'inventaire.
        Retourne (0, 0.0) si pas de stock ou quantité invalide.
    """
    inventaire = restaurant.inventory

    # Retour anticipé si pas d'inventaire disponible ou quantité demandée invalide
    if not inventaire.finished_product_batches or quantity <= 0:
        return (0, 0.0)

    # Initialiser les variables de suivi
    besoin = quantity  # Quantité restante à vendre
    vendu = 0  # Total des portions vendues jusqu'à présent
    chiffre_affaires = 0.0  # Chiffre d'affaires total accumulé
    i = 0  # Index du lot actuel dans la file FIFO

    # Traiter les lots en ordre FIFO jusqu'à ce qu'on ait vendu assez ou épuisé l'inventaire
    while i < len(inventaire.finished_product_batches) and besoin > 0:
        # Récupérer le lot actuel de la file FIFO
        lot = inventaire.finished_product_batches[i]

        # Calculer combien de portions on peut prendre de ce lot
        # Utiliser un accès sécurisé aux attributs au cas où l'attribut portions serait manquant
        portions_disponibles = int(getattr(lot, "portions", 0))
        prendre = min(portions_disponibles, besoin)

        # Traiter la vente si on peut prendre des portions de ce lot
        if prendre > 0:
            # Mettre à jour les totaux
            vendu += prendre

            # Calculer le chiffre d'affaires pour ce lot en utilisant son prix de vente spécifique
            # Utiliser un accès sécurisé aux attributs avec valeur par défaut pour les prix manquants
            prix_lot = float(getattr(lot, "selling_price", 0.0) or 0.0)
            chiffre_affaires += prendre * prix_lot

            # Mettre à jour l'inventaire du lot (réduire les portions disponibles)
            lot.portions -= prendre

            # Mettre à jour le besoin restant
            besoin -= prendre

        # Supprimer les lots vides de l'inventaire ou passer au lot suivant
        if lot.portions <= 0:
            # Le lot est épuisé, le supprimer de l'inventaire
            inventaire.finished.pop(i)
            # Ne pas incrémenter i puisqu'on a supprimé un élément
        else:
            # Le lot a encore des portions, passer au lot suivant
            i += 1

    # Retourner le total vendu et le chiffre d'affaires (arrondi pour éviter les problèmes de précision des flottants)
    return (vendu, round(chiffre_affaires, 2))


def _service_capacity_with_minutes(restaurant: Restaurant, clients_cap: int) -> int:
    """Calcule la capacité de service limitée par les minutes disponibles.

    Args:
        restaurant: Restaurant avec les minutes de service disponibles
        clients_cap: Capacité théorique en nombre de clients

    Returns:
        Capacité effective limitée par le temps de service disponible.
        Retourne la capacité d'entrée si les minutes sont illimitées.
    """
    # Calcule les minutes nécessaires par couvert selon le type de restaurant
    min_per_cover = restaurant.SERVICE_MINUTES_PER_COVER
    # Récupère les minutes de service encore disponibles
    minutes_left = restaurant.service_minutes_left

    # Si minutes illimitées ou temps par couvert invalide, pas de limitation
    if minutes_left == float("inf") or min_per_cover <= 0:
        return clients_cap

    # Retourne le minimum entre la capacité théorique et celle permise par le temps
    return min(minutes_left // min_per_cover, clients_cap)


def _consume_service_minutes(restaurant: Restaurant, clients_served: int) -> None:
    """Consomme les minutes de service nécessaires pour servir les clients.

    Args:
        restaurant: Restaurant dont consommer les minutes de service
        clients_served: Nombre de clients effectivement servis

    Note:
        Appelle la méthode du restaurant si disponible, sinon décrémente directement.
    """
    # Calcule les minutes nécessaires selon le type de restaurant
    min_per_cover = restaurant._service_minutes_per_cover()
    # Calcule le temps total requis pour servir tous les clients
    need = int(round(min_per_cover * max(0, int(clients_served))))

    # Appelle la méthode de consommation du restaurant si elle existe
    restaurant.consume_service_minutes(need)

    # Fallback : décrémente directement l'attribut si présent (pour compatibilité)
    restaurant.service_minutes_left = max(
        0, int(restaurant.service_minutes_left - need)
    )


def _apply_client_losses(
    restaurant: Restaurant,
    demanded: int,
    capacity_rh: int,
    cap_service: int,
    available_finished: int,
    sold: int,
) -> dict:
    """Calcule la répartition des pertes clients et applique une pénalité de notoriété.

    Analyse les causes de perte de clients :
    - manque_stock: capacité existante mais stock insuffisant
    - manque_capacite: limite RH/service avant même le stock
    - autre: arrondis/bruit/débordement vs demande

    Args:
        restaurant: Restaurant à analyser
        demanded: Nombre de clients demandant le service
        capacity_rh: Capacité RH/salle maximale
        cap_service: Capacité limitée par les minutes de service
        available_finished: Stock de produits finis disponible
        sold: Nombre effectivement servi

    Returns:
        Dictionnaire avec la répartition des pertes par cause

    Note:
        Applique une légère pénalité de notoriété basée sur le pourcentage de demande perdue.
    """
    asked = int(max(0, demanded))
    cap_stage = max(
        0, min(asked, int(capacity_rh))
    )  # capacité RH/salle de clamp_capacity
    cap_service_stage = max(
        0, min(cap_stage, int(cap_service))
    )  # borne par minutes de service
    stock_stage = max(
        0, min(cap_service_stage, int(available_finished))
    )  # borne par stock
    served = int(max(0, sold))

    lost_stock = max(0, stock_stage - served)
    lost_capacity = max(
        0, cap_service_stage - stock_stage
    )  # ce que la capacité n'a pas permis avant même le stock
    lost_other = max(
        0, asked - max(served, cap_service_stage)
    )  # bruit/arrondi/demande excédentaire

    total_lost = lost_stock + lost_capacity + lost_other

    # Effet notoriété très doux : -0.02 * %demande perdue (max 10 pts)
    if asked > 0 and total_lost > 0:
        frac = min(1.0, total_lost / asked)
        delta = min(0.10, 0.02 * frac * 100.0)  # 0..0.10
        noto = restaurant.notoriety
        restaurant.notoriety = max(0.0, min(1.0, round(noto * (1.0 - delta), 3)))

    return {
        "lost_total": total_lost,
        "lost_stock": lost_stock,
        "lost_capacity": lost_capacity,
        "lost_other": lost_other,
    }


def split_interest_principal(
    outstanding: float, annual_rate: float, monthly_payment: float
) -> Tuple[float, float, float]:
    """Calcule la répartition d'un paiement mensuel entre intérêts et capital.

    Pour un prêt donné, décompose le paiement mensuel en part d'intérêts
    (calculée sur l'encours restant) et part de remboursement du capital.

    Args:
        outstanding: Montant restant dû sur le prêt
        annual_rate: Taux d'intérêt annuel (ex: 0.045 pour 4.5%)
        monthly_payment: Montant du paiement mensuel fixe

    Returns:
        Tuple contenant:
        - interest_amount: Part d'intérêts du paiement mensuel
        - principal_amount: Part de capital remboursé
        - new_outstanding: Nouvel encours restant après paiement

    Note:
        Si le paiement mensuel ou l'encours sont <= 0, retourne (0, 0, encours_initial).
        Les montants sont arrondis à 2 décimales pour éviter les erreurs de précision.
    """
    if monthly_payment <= 0 or outstanding <= 0:
        return (0.0, 0.0, outstanding)

    # Calcul des intérêts mensuels sur l'encours restant
    interest_amount = round(outstanding * (annual_rate / 12.0), 2)

    # Part du capital = paiement mensuel - intérêts (minimum 0)
    principal_amount = max(0.0, round(monthly_payment - interest_amount, 2))

    # Nouvel encours = encours actuel - capital remboursé (minimum 0)
    new_outstanding = max(0.0, round(outstanding - principal_amount, 2))

    return (interest_amount, principal_amount, new_outstanding)


class Game:
    def __init__(self, restaurants: List[Restaurant], scenario: Scenario):
        """Moteur de jeu principal orchestrant les tours mensuels.

        Args:
            restaurants: Liste des restaurants joueurs
            scenario: Scénario de marché fournissant le contexte de demande
        """
        self.restaurants = restaurants
        self.scenario = scenario
        self.current_tour = 1

    def _show_scenario(self, scenario: Scenario) -> None:
        """Affiche les informations du scénario de marché pour informer le joueur.

        Args:
            scenario: Scénario à afficher avec population et segments

        Note:
            Affichage "best-effort" - gère les attributs manquants sans erreur.
        """
        pop = scenario.population_total
        shares = scenario.segments_share
        if pop and shares:
            print("\n=== Scénario du marché ===")
            print(f"Population mensuelle estimée : {int(pop)}")
            for seg, p in shares.items():
                print(f" - {seg}: {p * 100:.1f}%")
            print("==========================\n")

    def play(self) -> None:
        """Lance la boucle de jeu principale sur tous les tours.

        Cycle de vie par tour :
        1) Nettoyage des produits finis expirés
        2) Reset des minutes RH
        3) Allocation de la demande et limitation de capacité
        4) Limitation par minutes de service et stock fini
        5) Vente FIFO depuis l'inventaire et calcul du résultat opérationnel
        6) Calcul des pertes et application de la pénalité de notoriété
        7) Écritures comptables et flux d'emprunts
        8) Mise à jour de la trésorerie
        """
        # ——— Scénario ———
        self._show_scenario(self.scenario)

        restaurant = self.restaurants[0]
        # ——— Bureau du directeur juste après bilan initial ———
        for restaurant in self.restaurants:
            if restaurant.equipe and restaurant.type:
                print(f"\nOuverture du Bureau du Directeur pour {restaurant.name}")
                # signature historique: (equipe, type_resto)
                type_resto = restaurant.type
                restaurant.equipe = bureau_directeur(restaurant.equipe, type_resto)

        # ——— Boucle de jeu ———
        # Nombre de tours : si ton scenario expose nb_tours, on le prend. Sinon, 12 tours par défaut.
        nb_tours = self.scenario.nb_tours if self.scenario.nb_tours else 12

        while self.current_tour <= nb_tours:
            print(f"\n=== 📅 Tour {self.current_tour}/{nb_tours} ===")

            # 0) Péremption produits finis
            for resto in self.restaurants:
                resto.inventory.cleanup_expired(self.current_tour)

            # Reset minutes RH début de tour (fallback no-op si absent)
            for resto in self.restaurants:
                resto.reset_rh_minutes()

            # 1) Allocation de la demande (via le marché/scénario)
            attrib = allocate_customers_to_restaurants(self.restaurants, self.scenario)
            served_cap = clamp_capacity(self.restaurants, attrib)

            # 2) Boucle par restaurant
            for index_restaurant, restaurant in enumerate(self.restaurants):
                # Calcul du prix médian du menu du restaurant
                prix_median_menu = restaurant.compute_median_price()

                # Récupération de l'allocation de demande et contraintes de capacité pour ce restaurant
                clients_demandes = attrib[index_restaurant]
                capacite_max_clients = served_cap[index_restaurant]

                # Application de la contrainte de capacité de service basée sur les minutes de personnel disponibles
                capacite_service_clients = _service_capacity_with_minutes(
                    restaurant, capacite_max_clients
                )

                # Application de la contrainte de stock basée sur les portions finies disponibles
                portions_finies_disponibles = restaurant.get_available_portions()
                clients_reellement_servis = min(
                    clients_demandes,
                    capacite_service_clients,
                    portions_finies_disponibles,
                )

                # --- Calcul des pertes de clients par type de contrainte ---
                clients_perdus_par_stock = max(
                    0,
                    clients_demandes
                    - min(clients_demandes, portions_finies_disponibles),
                )
                clients_perdus_par_capacite = max(
                    0,
                    clients_demandes - min(clients_demandes, capacite_service_clients),
                )
                # Éviter le double comptage : "autre" représente les pertes restantes après contraintes de stock et capacité
                clients_perdus_autres = max(
                    0,
                    clients_demandes
                    - clients_reellement_servis
                    - max(clients_perdus_par_stock, clients_perdus_par_capacite),
                )
                pertes_clients = {
                    "lost_stock": clients_perdus_par_stock,
                    "lost_capacity": clients_perdus_par_capacite,
                    "lost_other": clients_perdus_autres,
                    "lost_total": clients_perdus_par_stock
                    + clients_perdus_par_capacite
                    + clients_perdus_autres,
                }

                # Consommation des minutes de service réelles basée sur les clients servis
                _consume_service_minutes(restaurant, clients_reellement_servis)

                # Exécution des ventes (FIFO depuis l'inventaire de produits finis) - chiffre d'affaires exact
                portions_vendues, chiffre_affaires_total = _sell_from_finished_fifo(
                    restaurant, clients_reellement_servis
                )

                # Calcul des financiers du tour (COGS reconnus au moment de la production)
                cout_marchandises_vendues = float(
                    getattr(restaurant, "turn_cogs", 0.0) or 0.0
                )
                charges_fixes = restaurant._fixed_costs_of()
                depenses_marketing = float(
                    getattr(restaurant, "marketing_budget", 0.0) or 0.0
                )
                couts_masse_salariale = restaurant._rh_cost_of()
                tresorerie_debut = float(getattr(restaurant, "funds", 0.0) or 0.0)

                # Résultat opérationnel (hors amortissements/intérêts - postés en comptabilité juste après)
                ventes_totales = float(chiffre_affaires_total)
                resultat_operationnel = (
                    ventes_totales
                    - cout_marchandises_vendues
                    - charges_fixes
                    - depenses_marketing
                    - couts_masse_salariale
                )
                tresorerie_fin = round(tresorerie_debut + resultat_operationnel, 2)

                # Application des pertes de clients (bonus mini)
                pertes_clients = _apply_client_losses(
                    restaurant,
                    demanded=clients_demandes,
                    capacity_rh=capacite_max_clients,
                    cap_service=capacite_service_clients,
                    available_finished=portions_finies_disponibles,
                    sold=portions_vendues,
                )
                # Tu peux logguer rapidement :
                if pertes_clients["lost_total"] > 0:
                    print(
                        f"⚠️ Pertes clients — {restaurant.name}: "
                        f"{pertes_clients['lost_total']} (stock: {pertes_clients['lost_stock']}, "
                        f"capacité: {pertes_clients['lost_capacity']}, autre: {pertes_clients['lost_other']})"
                    )

                # Objet "turn result" minimal pour affichage
                turn_result = TurnResult(
                    restaurant_name=restaurant.name,
                    tour=self.current_tour,
                    clients_attribues=clients_demandes,
                    clients_serv=portions_vendues,
                    capacity=capacite_max_clients,  # pour % capacité utilisée
                    price_med=prix_median_menu,
                    ca=round(chiffre_affaires_total, 2),
                    cogs=round(cout_marchandises_vendues, 2),
                    fixed_costs=round(charges_fixes, 2),
                    marketing=round(depenses_marketing, 2),
                    rh_cost=round(couts_masse_salariale, 2),
                    funds_start=round(tresorerie_debut, 2),
                    funds_end=round(tresorerie_fin, 2),
                    losses=pertes_clients,
                )

                # 3) Affichage gameplay
                print_turn_result(turn_result)

                # 4) COMPTABILISATION (posts standards)
                restaurant.post_sales(self.current_tour, turn_result.ca)
                restaurant.post_cogs(self.current_tour, turn_result.cogs)

                amount = turn_result.fixed_costs + turn_result.marketing
                restaurant.post_services_ext(self.current_tour, amount)

                restaurant.post_payroll(self.current_tour, turn_result.rh_cost)

                # Dotations aux amortissements
                dotation = restaurant.month_amortization()
                restaurant.post_depreciation(self.current_tour, dotation)

                # BPI
                bpi_interest, bpi_principal, restaurant.bpi_outstanding = (
                    split_interest_principal(
                        restaurant.bpi_outstanding,
                        restaurant.bpi_rate_annual,
                        restaurant.monthly_bpi,
                    )
                )
                restaurant.post_loan_payment(
                    self.current_tour, bpi_interest, bpi_principal, "BPI"
                )

                # Banque
                bank_interest, bank_principal, restaurant.bank_outstanding = (
                    split_interest_principal(
                        restaurant.bank_outstanding,
                        restaurant.bank_rate_annual,
                        restaurant.monthly_bank,
                    )
                )
                restaurant.post_loan_payment(
                    self.current_tour, bank_interest, bank_principal, "Banque"
                )

                # Mise à jour trésorerie gameplay (après flux financiers)
                total_loan_payments = (
                    bpi_interest + bpi_principal + bank_interest + bank_principal
                )
                restaurant.funds = round(
                    turn_result.funds_end - total_loan_payments,
                    2,
                )

                # Reset COGS de production (on l'a reconnu ce tour)
                restaurant.turn_cogs = 0.0

                # Mise à jour satisfaction RH selon l'utilisation (si présent)
                if hasattr(restaurant, "update_rh_satisfaction"):
                    try:
                        restaurant.update_rh_satisfaction()
                    except Exception:
                        pass

                # 5) AFFICHAGE COMPTA (si présent)
                if DISPLAY_COMPTA:
                    bal_mtd = restaurant.ledger.balance_accounts(
                        upto_tour=self.current_tour
                    )
                    print_income_statement(
                        bal_mtd,
                        title=f"Compte de résultat — {restaurant.name} — cumul à T{self.current_tour}",
                    )
                    print_balance_sheet(
                        bal_mtd,
                        title=f"Bilan — {restaurant.name} — à T{self.current_tour}",
                    )

            self.current_tour += 1
