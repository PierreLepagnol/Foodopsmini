# FoodOps Pro

Jeu de gestion de restaurant **réaliste, pédagogique et accessible** en python.

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

## 🛠️ Installation & mise en route

1. Installer les dépendances du projet

```bash
# Installe les dépendances avec uv (recommandée)
uv sync
```

2. Lancer le projet selon mode de jeu

- 👨‍🏫 Mode Administrateur
Interface de configuration pour professeurs
Configurez tous les paramètres de la partie

```bash
uv run -m cli_pro --admin
```

- 🍽️ Mode Professionnel Complet
Version Pro - interface enrichie
Achat de fonds de commerce, décisions avancées

```bash
# Lancer le jeu avec
uv run -m cli_pro

```

- 🧪 Mode Test & Démonstration
Lance les démonstrations et tests du système

```bash
uv run demo.py
```




```bash
# Version classique
python -m src.foodops_pro.cli
python -m src.foodops_pro.cli --scenario examples/scenarios/base.yaml
python -m src.foodops_pro.cli --debug --seed 42
```

```bash
# Version Pro (interface enrichie)
python -m src.foodops_pro.cli_pro
python -m src.foodops_pro.cli_pro --scenario examples/scenarios/base.yaml
```

```bash
# Mode Administrateur (Professeur)
python -m src.foodops_pro.cli_pro --admin
```

Choisissez votre :
### Presets de configuration

**📋 Configurations prêtes à l'emploi :**

- `admin_configs/preset_demo.yaml` : Démo rapide (1 joueur, 3 tours, budget 40-60k€)
- `admin_configs/preset_cours.yaml` : Cours standard (4 joueurs, 12 tours, budget 25-45k€)
- `admin_configs/preset_concours.yaml` : Concours (8 joueurs, 18 tours, budget fixe 20k€, IA difficile)

```bash
# Utiliser un preset
python -m src.foodops_pro.cli_pro --scenario admin_configs/preset_demo.yaml
```

## 🏗️ Architecture

```
src/foodops_pro/
├── cli.py               # CLI classique
├── cli_pro.py           # CLI Pro (UI avancée, mode admin, fonds de commerce)
├── ui/                  # Interface console pro & rapports
│   ├── console_ui.py
│   ├── decision_menu.py
│   └── financial_reports.py
├── admin/               # Mode administrateur (config prof)
│   └── admin_config.py
├── domain/
│   ├── commerce.py      # Fonds de commerce (nouveau)
│   ├── ingredient.py
│   ├── recipe.py
│   ├── restaurant.py
│   ├── employee.py
│   ├── supplier.py
│   ├── stock.py
│   └── scenario.py
├── core/
│   ├── market.py        # Allocation demande & concurrence
│   ├── costing.py       # Calcul coûts recettes
│   ├── ledger.py        # Comptabilité française
│   └── payroll_fr.py    # Paie (charges, heures sup)
├── io/
│   ├── data_loader.py   # Chargement CSV/JSON/YAML
│   ├── persistence.py   # Sauvegarde parties
│   └── export.py        # Export résultats et KPIs
├── data/
│   ├── ingredients.csv  # 35 ingrédients avec prix réels
│   ├── recipes.csv      # 20 recettes équilibrées
│   ├── recipe_items.csv # Fiches techniques détaillées
│   ├── suppliers.csv    # 8 fournisseurs avec conditions
│   └── hr_tables.json   # Tables RH françaises

examples/scenarios/
└── base.yaml

tests/
├── test_market_allocation.py
├── test_recipe_costing.py
├── test_ledger_vat.py
├── test_payroll.py
└── test_integration.py
```

## 🎮 Comment jouer (Classique)

1. **Lancement** : `python -m src.foodops_pro.cli`
2. **Configuration** : Choisissez le nombre de joueurs (1-4) et le type de restaurant
3. **Chaque tour** :
   - Ajustez vos prix de vente
   - Définissez votre niveau de staffing (0=fermé, 1=léger, 2=normal, 3=renforcé)
4. **Résultats** : Analysez vos KPIs et votre position concurrentielle
5. **Fin de partie** : Classement par trésorerie finale

## 🎮 Comment jouer (Pro)

1. **Lancement** : `python -m src.foodops_pro.cli_pro`
2. **Briefing** : l’écran d’accueil affiche le scénario (contexte, objectifs, segments)
3. **Achat** : choisissez un fonds de commerce (prix, loyer, rénovation, trafic, concurrence)
4. **Configuration** : nommez votre restaurant, un menu de base est appliqué
5. **Tour de jeu (décisions enrichies)** :
   - 📋 Menu & Pricing, 👥 RH, 🛒 Achats, 📈 Marketing, 🏗 Investissements, 💰 Finance, 📊 Rapports
6. **Résultats** : demande allouée, clients servis, utilisation, CA, ticket moyen, marges, etc.
7. **Fin** : classement final par trésorerie et analyses

## 👨‍🏫 Guide Professeur (Mode Administrateur)

Démarrer : `python -m src.foodops_pro.cli_pro --admin`

- 📋 Session : nom du cours, professeur, code de cours, année
- 🎮 Jeu : joueurs max, nombre de tours, budgets, IA (nombre + difficulté)
- 📊 Marché : taille du marché, croissance, intensité concurrentielle
- 🎯 Réalisme : événements aléatoires, saisonnalité, cycles économiques, fréquence
- 📝 Notation : critères pondérés (survie, rentabilité, croissance, efficacité, stratégie)
- 🔒 Restrictions : types de restaurants, limites d’employés, limites de prix (progressif)
- 💾 Sauvegarde : YAML dans `admin_configs/`
- ▶️ Lancer : démarre la partie avec vos paramètres

Scénarios pédagogiques types :
- Débutant : budget 40-60k€, 6-8 tours, IA facile, peu d’événements
- Intermédiaire : budget 25-40k€, 12 tours, IA moyenne, événements modérés
- Avancé : budget 15-25k€, 18-24 tours, IA difficile, événements fréquents, cycles activés
- Concours : conditions identiques, notation stricte, classement final, export résultats

## 📊 KPIs et rapports (Pro)

- **Opérationnels** : clients servis, taux d’utilisation
- **Financiers** : CA, ticket moyen, marge brute et nette, food cost %
- **Marché** : part de marché, satisfaction de la demande
- **RH** : coût personnel, productivité
- **Rapports** : compte de résultat, bilan, flux de trésorerie, KPIs et analyse

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

- [ ] Achats & Stocks complets (FEFO visible dans le CLI Pro)
- [ ] RH avancé (licenciement, formation, horaires)
- [ ] Événements aléatoires/saisonniers/cycles (paramétrés en admin)
- [ ] Sauvegarde/chargement de parties enrichi
- [ ] Graphiques et tableaux de bord console
- [ ] Mode campagne avec progression
- [ ] Multijoueur en réseau
- [ ] Interface web (ultérieur)

## 📄 Licence

Thomas LEPAGNOL Propiétaire du code source