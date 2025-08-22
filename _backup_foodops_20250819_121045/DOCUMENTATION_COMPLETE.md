# 📚 DOCUMENTATION COMPLÈTE FOODOPS PRO

## 🎯 **PRÉSENTATION GÉNÉRALE**

### **Qu'est-ce que FoodOps Pro ?**

FoodOps Pro est un **simulateur de gestion d'entreprise** spécialement conçu pour l'enseignement des sciences de gestion dans le secteur de la restauration. Il combine **réalisme professionnel** et **accessibilité pédagogique** pour former les futurs entrepreneurs.

### **🎓 Public Cible**
- **Étudiants** en école de commerce, BTS, université
- **Formateurs** en entrepreneuriat et gestion d'entreprise
- **Professionnels** en reconversion ou formation continue
- **Passionnés** de simulation d'entreprise

### **🏆 Objectifs Pédagogiques**
1. **Comprendre** les enjeux de la gestion d'entreprise
2. **Maîtriser** les concepts de coût, marge, rentabilité
3. **Développer** une vision stratégique long terme
4. **Apprendre** la prise de décision sous contraintes
5. **Intégrer** les aspects marketing, finance, opérations

---

## 🎮 **COMMENT JOUER ?**

### **🚀 Lancement Rapide**

#### **Version Simple (Débutants)**
```bash
python Foodopsmini.py
```
- **Pour qui ?** Découverte, enfants, apprentissage de base
- **Durée ?** 30-60 minutes
- **Concepts ?** Prix, personnel, concurrence

#### **Version Professionnelle (Avancée)**
```bash
python -m src.foodops_pro.cli_pro
```
- **Pour qui ?** Étudiants, professionnels, formation
- **Durée ?** 2-4 heures
- **Concepts ?** Qualité, stocks, marketing, finance, comptabilité

### **📋 Déroulement d'une Partie**

1. **CONFIGURATION** (5 min)
   - Choix du nom et type de restaurant
   - Budget initial et objectifs
   - Paramètres de difficulté

2. **TOURS DE JEU** (20-30 min/tour)
   - **Décisions** : Prix, qualité, personnel, marketing
   - **Simulation** : Allocation de marché automatique
   - **Résultats** : CA, profit, satisfaction, réputation

3. **ANALYSE** (10 min/tour)
   - Tableaux de bord détaillés
   - Comparaison avec concurrents
   - Recommandations stratégiques

---

## 🧠 **MÉCANIQUES DE JEU DÉTAILLÉES**

### **🎯 Système de Qualité (⭐⭐⭐⭐⭐)**

#### **5 Niveaux de Qualité**
- **1⭐ Économique** : -30% coût, -20% satisfaction
- **2⭐ Standard** : Prix de référence
- **3⭐ Supérieur** : +25% coût, +15% satisfaction
- **4⭐ Premium** : +50% coût, +30% satisfaction
- **5⭐ Luxe** : +100% coût, +50% satisfaction

#### **Impact sur le Gameplay**
- **Coût matières** : Directement proportionnel
- **Satisfaction client** : Influence la réputation
- **Attractivité** : Variable selon les segments
- **Différenciation** : Avantage concurrentiel

### **🌱 Saisonnalité Dynamique**

#### **Variations Automatiques**
- **Prix** : -30% à +40% selon saison
- **Qualité** : ±1⭐ pour produits de saison
- **Demande** : Bonus par segment (été = +30% familles)
- **Disponibilité** : Ruptures possibles hors saison

#### **Événements Spéciaux**
- **Noël** : +50% saumon, +30% fromages
- **Été** : +20% salades, -30% tomates
- **Pâques** : +20% œufs
- **Canicule** : +10% salades, +40% demande

### **📦 Gestion Stocks FEFO**

#### **First Expired, First Out**
- **Rotation automatique** : Les produits les plus anciens sortent en premier
- **Dégradation progressive** : Perte de qualité selon l'âge
- **Alertes expiration** : Notifications J-2
- **Promotions automatiques** : Écoulement des stocks proches

#### **Impact Financier**
- **Pertes** : 2-5% selon gestion
- **Ruptures** : Perte de ventes
- **Optimisation** : Réduction des coûts

### **📈 Marketing & Communication**

#### **Types de Campagnes**
- **Réseaux sociaux** : 50€/jour, 2.5% conversion, cible jeunes
- **Publicité locale** : 80€/jour, 3.5% conversion, cible familles
- **Programme fidélité** : 30€/jour, 15% conversion, tous segments
- **Événements** : 200€/jour, 8% conversion, cible foodies

#### **Gestion Réputation**
- **Avis clients** : Impact pondéré selon plateforme
- **Évolution progressive** : Réputation sur 10
- **Réponse aux avis** : Influence la perception

### **💰 Finance Avancée**

#### **Comptabilité Complète**
- **Plan comptable** : Adapté à la restauration
- **Écriture double** : Débit/Crédit automatique
- **Bilan** : Actifs, Passifs, Capitaux propres
- **Compte de résultat** : Produits, Charges, Résultat

#### **Analyses Financières**
- **Rentabilité par plat** : Marge unitaire et totale
- **Prévision trésorerie** : 30 jours glissants
- **Ratios financiers** : Liquidité, ROE, ROA, endettement
- **Seuils de rentabilité** : Point mort par recette

---

## 📊 **STRATÉGIES DE JEU**

### **🎯 Stratégie Économique**
- **Objectif** : Volume maximum, prix bas
- **Qualité** : 1-2⭐ (économique)
- **Prix** : -20% vs marché
- **Cible** : Étudiants, familles budget
- **KPIs** : 30-40% part de marché, marge 30-40%

### **🎯 Stratégie Premium**
- **Objectif** : Équilibre qualité/prix
- **Qualité** : 3-4⭐ (supérieur/premium)
- **Prix** : +20% vs marché
- **Cible** : Familles, foodies occasionnels
- **KPIs** : 20-30% part de marché, marge 50-65%

### **🎯 Stratégie Luxe**
- **Objectif** : Excellence, niche premium
- **Qualité** : 5⭐ (luxe)
- **Prix** : +50% vs marché
- **Cible** : Foodies, occasions spéciales
- **KPIs** : 10-20% part de marché, marge 60-80%

---

## 📈 **KPIs ET MÉTRIQUES**

### **🎯 KPIs Opérationnels**
- **Clients/jour** : Volume d'activité
- **Ticket moyen** : Valeur par client
- **Taux d'occupation** : Utilisation capacité
- **Temps d'attente** : Qualité de service
- **Satisfaction client** : Note sur 5

### **💰 KPIs Financiers**
- **Chiffre d'affaires** : Prix × Volume
- **Marge brute** : CA - Coût matières
- **Résultat net** : Après toutes charges
- **Trésorerie** : Position de liquidité
- **ROE** : Rentabilité des capitaux propres

### **📈 KPIs Marketing**
- **Nouveaux clients** : Acquisition
- **Taux de fidélisation** : Rétention
- **ROI marketing** : Retour sur investissement
- **Réputation en ligne** : Avis et notes
- **Portée sociale** : Audience touchée

---

## 🎓 **UTILISATION PÉDAGOGIQUE**

### **📚 En Cours**

#### **Séance Type (2h)**
1. **Introduction** (15 min) : Présentation du jeu et objectifs
2. **Configuration** (15 min) : Création restaurants, choix stratégies
3. **Jeu** (60 min) : 3-4 tours avec décisions collectives
4. **Analyse** (20 min) : Débriefing résultats et stratégies
5. **Synthèse** (10 min) : Concepts clés et apprentissages

#### **Concepts Enseignés**
- **Gestion** : Coûts, marges, rentabilité
- **Marketing** : Segmentation, positionnement, mix
- **Finance** : Trésorerie, ratios, investissements
- **Stratégie** : Différenciation, avantage concurrentiel
- **Opérations** : Stocks, qualité, efficacité

### **🏆 Évaluations Possibles**

#### **Évaluation Formative**
- **Décisions justifiées** : Pourquoi ces choix ?
- **Analyse de résultats** : Que nous apprennent les KPIs ?
- **Stratégies alternatives** : Qu'auriez-vous fait différemment ?

#### **Évaluation Sommative**
- **Business plan** : Stratégie 3 ans
- **Analyse concurrentielle** : Forces/faiblesses
- **Présentation orale** : Défense de stratégie

---

## 🔧 **CONFIGURATION AVANCÉE**

### **👨‍🏫 Mode Professeur**

#### **Paramètres Modifiables**
- **Difficulté** : Volatilité marché, événements aléatoires
- **Durée** : Nombre de tours, temps par tour
- **Segments** : Taille, budget, sensibilités
- **Concurrence** : Nombre, stratégies IA

#### **Rapports Détaillés**
- **Performance individuelle** : Par étudiant/équipe
- **Analyse comparative** : Classements, évolutions
- **Apprentissages** : Concepts maîtrisés/à revoir

### **📊 Tableaux de Bord**

#### **Vue Enseignant**
- **Progression pédagogique** : Objectifs atteints
- **Engagement** : Participation, motivation
- **Difficultés** : Points de blocage identifiés
- **Recommandations** : Adaptations suggérées

---

## 🚀 **ÉVOLUTIONS FUTURES**

### **🎯 Modules en Développement**
- **Innovation R&D** : Création nouveaux produits
- **Expansion multi-sites** : Gestion de chaîne
- **Durabilité RSE** : Impact environnemental
- **Digital & Tech** : Commande en ligne, livraison

### **🌐 Fonctionnalités Avancées**
- **Mode en ligne** : Parties multi-établissements
- **IA adaptative** : Concurrence intelligente
- **Réalité augmentée** : Visualisation 3D restaurant
- **Blockchain** : Traçabilité ingrédients

---

## 💡 **CONSEILS D'UTILISATION**

### **🎯 Pour les Enseignants**
1. **Commencez simple** : Version mini puis pro
2. **Préparez les concepts** : Expliquez avant de jouer
3. **Encouragez l'expérimentation** : Pas de "bonne" stratégie unique
4. **Débriefer systématiquement** : L'apprentissage vient de l'analyse
5. **Adaptez la difficulté** : Selon le niveau des étudiants

### **🎯 Pour les Étudiants**
1. **Lisez les indicateurs** : Chaque KPI raconte une histoire
2. **Testez différentes stratégies** : Économique vs Premium
3. **Analysez la concurrence** : Qu'est-ce qui marche ?
4. **Pensez long terme** : Réputation et fidélisation
5. **Justifiez vos décisions** : Pourquoi ce choix ?

---

## 🎉 **CONCLUSION**

FoodOps Pro transforme l'apprentissage de la gestion d'entreprise en **expérience immersive et engageante**. En combinant **réalisme professionnel** et **accessibilité pédagogique**, il permet aux étudiants de **vivre concrètement** les défis de l'entrepreneuriat.

**🎯 Résultat :** Des futurs entrepreneurs mieux préparés aux réalités du monde de l'entreprise !

---

*📧 Contact : [votre-email] | 🌐 Site : [votre-site] | 📱 Support : [support]*
