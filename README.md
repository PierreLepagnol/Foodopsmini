# FoodOps Pro

Jeu de gestion de restaurant **réaliste, pédagogique et accessible** en Python 3.11+.

## 🎯 Objectif pédagogique

Former des futurs entrepreneurs/restaurateurs aux aspects clés de la gestion :
- **Menu engineering** et calcul de coûts avec rendements
- **Gestion des achats** et stocks (FEFO - First Expired, First Out)
- **Ressources humaines** selon le droit du travail français
- **Comptabilité** française (Plan Comptable Général simplifié)
- **Analyse de marché** et gestion de la concurrence

## ✨ Fonctionnalités

- **Jeu tour par tour** multi-joueurs (1-4 joueurs sur la même machine)
- **Modèles réalistes** : 35+ ingrédients, 20+ recettes, fournisseurs, employés
- **Marché dynamique** avec 3 segments de clientèle et concurrence IA
- **Comptabilité française** avec TVA (10%, 5.5%, 20%), charges sociales, amortissements
- **KPIs métier** : ticket moyen, coût matière, marge, taux de saturation, cash-flow
- **Données paramétrables** via CSV/JSON et scénarios YAML

## 🚀 Installation et lancement

### Installation des dépendances

```bash
pip install pyyaml pandas pytest
```

### Lancement du jeu

```bash
# Lancer une partie
python -m src.foodops_pro.cli

# Avec un scénario spécifique
python -m src.foodops_pro.cli --scenario examples/scenarios/base.yaml

# Mode debug avec graine fixe
python -m src.foodops_pro.cli --debug --seed 42
```

### Démonstration

```bash
# Voir une démonstration des fonctionnalités
python demo.py
```

## 🏗️ Architecture

```
src/foodops_pro/
├── domain/          # Modèles métier
│   ├── ingredient.py    # Ingrédients avec coûts et TVA
│   ├── recipe.py        # Recettes avec rendements
│   ├── restaurant.py    # Restaurants et types
│   ├── employee.py      # Employés et contrats français
│   ├── supplier.py      # Fournisseurs et conditions
│   ├── stock.py         # Gestion stocks FEFO
│   └── scenario.py      # Scénarios et segments marché
├── core/            # Logique business
│   ├── market.py        # Allocation demande et concurrence
│   ├── costing.py       # Calcul coûts recettes
│   ├── ledger.py        # Comptabilité PCG française
│   └── payroll_fr.py    # Paie française (charges, heures sup)
├── io/              # Persistance et données
│   ├── data_loader.py   # Chargement CSV/JSON/YAML
│   ├── persistence.py   # Sauvegarde parties
│   └── export.py        # Export résultats et KPIs
├── data/            # Données seed réalistes
│   ├── ingredients.csv  # 35 ingrédients avec prix réels
│   ├── recipes.csv      # 20 recettes équilibrées
│   ├── recipe_items.csv # Fiches techniques détaillées
│   ├── suppliers.csv    # 8 fournisseurs avec conditions
│   └── hr_tables.json   # Tables RH françaises
└── cli.py           # Interface console

examples/scenarios/  # Scénarios configurables
└── base.yaml       # Scénario d'initiation 3 segments

tests/              # Tests unitaires (pytest)
├── test_market_allocation.py  # Tests allocation marché
├── test_recipe_costing.py     # Tests calcul coûts
├── test_ledger_vat.py         # Tests comptabilité TVA
├── test_payroll.py            # Tests paie française
└── test_integration.py       # Tests d'intégration
```

## 🎮 Comment jouer

1. **Lancement** : `python -m src.foodops_pro.cli`
2. **Configuration** : Choisissez le nombre de joueurs (1-4) et le type de restaurant
3. **Chaque tour** :
   - Ajustez vos prix de vente
   - Définissez votre niveau de staffing (0=fermé, 1=léger, 2=normal, 3=renforcé)
   - Gérez vos commandes fournisseurs (TODO)
4. **Résultats** : Analysez vos KPIs et votre position concurrentielle
5. **Fin de partie** : Classement par trésorerie finale

## 📊 KPIs et métriques

- **Opérationnels** : clients servis, taux d'utilisation, clients perdus
- **Financiers** : CA, ticket moyen, marge, coût matière %
- **Marché** : part de marché, satisfaction demande
- **RH** : coût personnel, productivité équipe

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_market_allocation.py -v
python -m pytest tests/test_ledger_vat.py -v
python -m pytest tests/test_payroll.py -v

# Tests d'intégration
python -m pytest tests/test_integration.py -v
```

## 📈 Données réalistes

### Ingrédients (35+)
- **Viandes** : steak haché (8.50€/kg), poulet (7.20€/kg), saumon (15.80€/kg)
- **Légumes** : tomate (3.20€/kg), salade (2.10€/kg), avocat (8.20€/kg)
- **Épicerie** : pâtes (2.80€/kg), riz (3.50€/kg), huile olive (8.90€/L)
- **TVA** : 5.5% (produits alimentaires), 20% (huiles, sauces)

### Recettes (20+)
- **Fast-food** : burger classique, wrap poulet, menu enfant
- **Classique** : pâtes bolognaise, steak-frites, salade césar
- **Gastronomique** : bowl saumon, risotto champignons
- **Rendements** : pertes préparation et cuisson intégrées

### Segments de marché
- **Étudiants** (35%) : budget 11€, sensibles au prix, préfèrent fast-food
- **Familles** (40%) : budget 17€, équilibrés, préfèrent classique
- **Foodies** (25%) : budget 25€, sensibles qualité, préfèrent gastronomique

## 🔧 Configuration avancée

### Scénarios personnalisés
Modifiez `examples/scenarios/base.yaml` pour :
- Ajuster les segments de marché
- Modifier les taux de TVA
- Configurer la concurrence IA
- Définir la saisonnalité

### Données personnalisées
Modifiez les fichiers CSV dans `src/foodops_pro/data/` :
- Ajoutez vos propres ingrédients et prix
- Créez de nouvelles recettes
- Configurez les fournisseurs
- Adaptez les tables RH

## 🎓 Aspects pédagogiques

### Menu Engineering
- Calcul précis des coûts matière avec rendements
- Analyse de marge par recette
- Optimisation du mix produit

### Gestion Financière
- Comptabilité française (PCG)
- Gestion de la TVA (collectée/déductible)
- Calcul des charges sociales
- Suivi de trésorerie

### Stratégie Marketing
- Positionnement prix selon les segments
- Analyse concurrentielle
- Gestion de la capacité

## 📝 TODO et améliorations

- [ ] Gestion complète des commandes fournisseurs dans le CLI
- [ ] Système de recrutement/licenciement d'employés
- [ ] Événements aléatoires (grèves, festivals, contrôles)
- [ ] Interface web (Flask/Django)
- [ ] Sauvegarde/chargement de parties
- [ ] Graphiques et tableaux de bord
- [ ] Mode campagne avec progression
- [ ] Multijoueur en réseau

## 📄 Licence

MIT License - Projet éducatif libre d'utilisation et de modification.
