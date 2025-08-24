from game_engine.domain.menu.ingredients_VO import CATALOG
from FoodOPS_V1.domain.restaurant_VO import Restaurant
from FoodOPS_V1.domain.recipe_VO import Complexity, SimpleRecipe, Technique

# from FoodOPS_V1.rules.costing import recipe_cost_and_price
from game_engine.utilsV0 import get_input

from FoodOPS_V1.domain.recipe_VO import recipe_prep_minutes_per_portion


def format_currency_eur(x: float) -> str:
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")


def run_recipes_shop(r: Restaurant, current_tour: int) -> None:
    inv = r.inventory
    catalog = CATALOG

    while True:
        print("\n=== Recettes & Achats ===")
        print("1) Voir stock ingrédients")
        print("2) Acheter ingrédients (kg)")
        print("3) Produire des portions (recette simple)")
        print("4) Voir produits finis")
        print("5) Retour")
        ch = input("> ").strip()

        if ch == "1":
            if not inv.ingredients:
                print("Stock ingrédients: (vide)")
            else:
                print("Stock ingrédients (kg):")
                for (_, _), si in inv.ingredients.items():
                    print(
                        f" - {si.ingredient.name} [{si.ingredient.grade.name}] : {si.kg:.2f} kg"
                    )

        elif ch == "2":
            # achat simple: choisir ingrédient exact (avec sa gamme) du catalogue
            print("\nCatalogue ingrédients:")
            for i, ing in enumerate(catalog, start=1):
                print(
                    f"{i}) {ing.name} [{ing.grade.name}] — {format_currency_eur(ing.base_priceformat_currency_eur_per_kg)}/kg"
                )
            k = get_input(
                "Sélection: ", lambda x: 1 <= x <= len(catalog), "Choix invalide."
            )
            ing = catalog[k - 1]
            kg = get_input(
                "Quantité (kg) à acheter: ",
                lambda x: x > 0,
                "Quantité invalide.",
            )

            cost = round(ing.base_priceformat_currency_eur_per_kg * kg, 2)
            if r.funds < cost:
                print(
                    f"Trésorerie insuffisante. Coût = {format_currency_eur(cost)}, Fonds = {format_currency_eur(r.funds)}"
                )
                continue
            r.funds -= cost
            inv.add_ingredient(ing, kg)
            print(
                f"Acheté {kg:.2f} kg de {ing.name} [{ing.grade.name}] pour {format_currency_eur(cost)}."
            )

        elif ch == "3":
            # Produire une recette simple à partir d'un ingrédient DISPONIBLE en stock
            if not inv.ingredients:
                print("Aucun ingrédient en stock.")
                continue

            # étape 1: choisir un nom d'ingrédient dispo
            names = sorted(set(n for (n, _g) in inv.ingredients.keys()))
            print("\nIngrédients disponibles (par nom):")
            for i, n in enumerate(names, start=1):
                print(f"{i}) {n}")
            kn = get_input("Nom: ", lambda x: 1 <= x <= len(names), "Choix invalide.")
            name = names[kn - 1]

            # étape 2: choisir la variante (gamme) en stock
            variants = inv.get_available_variants(name)
            print("\nVariantes en stock:")
            for i, si in enumerate(variants, start=1):
                print(
                    f"{i}) {si.ingredient.name} [{si.ingredient.grade.name}] — {si.kg:.2f} kg dispo"
                )
            kv = get_input(
                "Variante: ", lambda x: 1 <= x <= len(variants), "Choix invalide."
            )
            ing = variants[kv - 1].ingredient

            # étape 3: définir la recette simple (technique + complexité + portion_kg)
            print(
                "\nTechnique: 1) FROID  2) GRILLE  3) SAUTE  4) ROTI  5) FRIT  6) VAPEUR"
            )
            kt = get_input("> ", lambda x: 1 <= x <= 6, "Choix invalide.")
            tech = [
                Technique.FROID,
                Technique.GRILLE,
                Technique.SAUTE,
                Technique.ROTI,
                Technique.FRIT,
                Technique.VAPEUR,
            ][kt - 1]

            print("Complexité: 1) SIMPLE  2) COMPLEXE")
            kc = get_input("> ", lambda x: 1 <= x <= 2, "Choix invalide.")
            cplx = [Complexity.SIMPLE, Complexity.COMPLEXE][kc - 1]

            portion_kg = get_input(
                "Portion (kg/portion), ex 0.16: ",
                lambda x: x > 0,
                "Portion invalide.",
            )

            recipe_name = (
                get_input(
                    "Nom de recette (ex: 'Burger boeuf', 'Saumon mi-cuit'): ",
                    lambda x: x != "",
                    "Nom de recette invalide.",
                )
                or f"{name} - {tech.name.title()}"
            )
            # on crée la recette simple
            recipe = SimpleRecipe.from_ingredient(
                recipe_name, ing, portion_kg, tech, cplx
            )
            # calcule prix conseillé selon type de resto
            # cogs, price = recipe_cost_and_price(r.type, recipe)
            recipe.selling_price = recipe.suggest_price(r.type)
            print(
                f"Prix conseillé: {format_currency_eur(recipe.selling_price)}  (COGS/portion ≈ {format_currency_eur(recipe.base_cost)})"
            )

            portions = get_input(
                "Portions à produire: ",
                lambda x: x > 0,
                "Nombre invalide.",
            )

            mins_per_portion = recipe_prep_minutes_per_portion(recipe)
            mins_need = int(round(mins_per_portion * portions))

            # vérifier la banque de minutes RH
            if r.rh_minutes_left <= 0:
                print(
                    "❌ Équipe saturée ce tour : plus de minutes de production disponibles."
                )
                continue

            if mins_need > r.rh_minutes_left:
                max_portions = max(
                    0, r.rh_minutes_left // max(1, int(mins_per_portion))
                )
                if max_portions <= 0:
                    print(
                        "❌ Équipe saturée : impossible de produire davantage ce tour."
                    )
                    continue
                print(
                    f"⚠️ Capacité RH limite : production plafonnée à {max_portions} portions (au lieu de {portions})."
                )
                portions = max_portions
                mins_need = int(round(mins_per_portion * portions))

            # consomme minutes RH
            _ = r.consume_rh_minutes(mins_need)

            ok, cogs_total, msg = inv.produce_from_recipe(
                recipe, portions, current_tour
            )
            if not ok:
                print(f"❌ {msg}")
                continue

            # on mémorise le COGS du tour sur le restaurant (reconnaissance à la production)
            r.turn_cogs = round(r.turn_cogs + cogs_total, 2)
            # mémoriser “dernière recette utilisée” si tu veux la remettre dans r.menu aussi
            if all(rr.name != recipe.name for rr in r.menu):
                r.menu.append(recipe)

            print(
                f"✅ {msg}  | COGS reconnu ce tour: {format_currency_eur(cogs_total)}"
            )

        elif ch == "4":
            if not inv.finished:
                print("Aucun produit fini.")
            else:
                print("Produits finis (FIFO):")
                for b in inv.finished:
                    print(
                        f" - {b.recipe_name} : {b.portions} portions, prix {format_currency_eur(b.selling_price)}, péremption T{b.expiry_tour}"
                    )

        elif ch == "5":
            return

        else:
            print("Choix invalide.")
