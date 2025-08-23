"""
Système d'achievements/succès pour FoodOps Pro.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime


class AchievementCategory(Enum):
    """Catégories d'achievements."""

    FINANCIAL = "financier"
    OPERATIONAL = "operationnel"
    STRATEGIC = "strategique"
    SOCIAL = "social"
    SPECIAL = "special"


class AchievementRarity(Enum):
    """Rareté des achievements."""

    COMMON = "commun"
    UNCOMMON = "peu_commun"
    RARE = "rare"
    EPIC = "épique"
    LEGENDARY = "légendaire"


@dataclass
class Achievement:
    """Définition d'un achievement."""

    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    points: int
    icon: str

    # Conditions d'obtention
    condition_func: Callable[[Dict[str, Any]], bool] = None
    hidden: bool = False  # Achievement secret

    # Métadonnées
    unlock_date: Optional[datetime] = None
    progress: float = 0.0  # 0.0 à 1.0 pour les achievements progressifs

    def is_unlocked(self) -> bool:
        """Vérifie si l'achievement est débloqué."""
        return self.unlock_date is not None

    def unlock(self) -> None:
        """Débloque l'achievement."""
        if not self.is_unlocked():
            self.unlock_date = datetime.now()
            self.progress = 1.0


class AchievementManager:
    """Gestionnaire des achievements."""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: List[str] = []
        self.total_points = 0

        # Charger les achievements
        self._load_achievements()

    def _load_achievements(self) -> None:
        """Charge la liste des achievements disponibles."""
        achievements_data = [
            # Achievements financiers
            {
                "id": "first_profit",
                "name": "Premier Profit",
                "description": "Réalisez votre premier profit positif",
                "category": AchievementCategory.FINANCIAL,
                "rarity": AchievementRarity.COMMON,
                "points": 10,
                "icon": "💰",
                "condition": lambda data: data.get("profit", 0) > 0,
            },
            {
                "id": "big_profit",
                "name": "Gros Bénéfices",
                "description": "Réalisez plus de 1000€ de profit en un tour",
                "category": AchievementCategory.FINANCIAL,
                "rarity": AchievementRarity.UNCOMMON,
                "points": 25,
                "icon": "💎",
                "condition": lambda data: data.get("profit", 0) >= 1000,
            },
            {
                "id": "millionaire",
                "name": "Millionnaire",
                "description": "Accumulez 1 million d'euros de chiffre d'affaires total",
                "category": AchievementCategory.FINANCIAL,
                "rarity": AchievementRarity.EPIC,
                "points": 100,
                "icon": "🏆",
                "condition": lambda data: data.get("total_revenue", 0) >= 1000000,
            },
            # Achievements opérationnels
            {
                "id": "full_house",
                "name": "Complet !",
                "description": "Atteignez 100% de taux d'occupation",
                "category": AchievementCategory.OPERATIONAL,
                "rarity": AchievementRarity.COMMON,
                "points": 15,
                "icon": "🏠",
                "condition": lambda data: data.get("occupation_rate", 0) >= 1.0,
            },
            {
                "id": "quality_master",
                "name": "Maître Qualité",
                "description": "Maintenez la qualité 5⭐ pendant 5 tours consécutifs",
                "category": AchievementCategory.OPERATIONAL,
                "rarity": AchievementRarity.RARE,
                "points": 50,
                "icon": "⭐",
                "condition": lambda data: data.get("consecutive_5_star", 0) >= 5,
            },
            {
                "id": "efficiency_expert",
                "name": "Expert en Efficacité",
                "description": "Servez 200+ clients avec seulement 2 employés",
                "category": AchievementCategory.OPERATIONAL,
                "rarity": AchievementRarity.RARE,
                "points": 40,
                "icon": "⚡",
                "condition": lambda data: data.get("clients_served", 0) >= 200
                and data.get("staff_level", 3) <= 2,
            },
            # Achievements stratégiques
            {
                "id": "market_leader",
                "name": "Leader du Marché",
                "description": "Obtenez 50% de part de marché",
                "category": AchievementCategory.STRATEGIC,
                "rarity": AchievementRarity.RARE,
                "points": 60,
                "icon": "👑",
                "condition": lambda data: data.get("market_share", 0) >= 0.5,
            },
            {
                "id": "price_warrior",
                "name": "Guerrier des Prix",
                "description": "Gagnez avec le prix le plus bas du marché",
                "category": AchievementCategory.STRATEGIC,
                "rarity": AchievementRarity.UNCOMMON,
                "points": 30,
                "icon": "⚔️",
                "condition": lambda data: data.get("lowest_price", False)
                and data.get("profit", 0) > 0,
            },
            {
                "id": "premium_strategy",
                "name": "Stratégie Premium",
                "description": "Gagnez avec le prix le plus élevé du marché",
                "category": AchievementCategory.STRATEGIC,
                "rarity": AchievementRarity.UNCOMMON,
                "points": 35,
                "icon": "💎",
                "condition": lambda data: data.get("highest_price", False)
                and data.get("profit", 0) > 0,
            },
            # Achievements sociaux
            {
                "id": "customer_favorite",
                "name": "Chouchou des Clients",
                "description": "Atteignez 4.5/5 de satisfaction client",
                "category": AchievementCategory.SOCIAL,
                "rarity": AchievementRarity.UNCOMMON,
                "points": 25,
                "icon": "😍",
                "condition": lambda data: data.get("customer_satisfaction", 0) >= 4.5,
            },
            {
                "id": "reputation_master",
                "name": "Maître de la Réputation",
                "description": "Atteignez 9/10 de réputation",
                "category": AchievementCategory.SOCIAL,
                "rarity": AchievementRarity.RARE,
                "points": 50,
                "icon": "🌟",
                "condition": lambda data: data.get("reputation", 0) >= 9.0,
            },
            {
                "id": "social_media_star",
                "name": "Star des Réseaux",
                "description": "Obtenez 100 avis positifs",
                "category": AchievementCategory.SOCIAL,
                "rarity": AchievementRarity.RARE,
                "points": 45,
                "icon": "📱",
                "condition": lambda data: data.get("positive_reviews", 0) >= 100,
            },
            # Achievements spéciaux
            {
                "id": "survivor",
                "name": "Survivant",
                "description": "Survivez à 3 événements négatifs consécutifs",
                "category": AchievementCategory.SPECIAL,
                "rarity": AchievementRarity.RARE,
                "points": 55,
                "icon": "🛡️",
                "condition": lambda data: data.get("consecutive_negative_events", 0)
                >= 3,
            },
            {
                "id": "comeback_king",
                "name": "Roi du Comeback",
                "description": "Passez de négatif à +1000€ de profit en un tour",
                "category": AchievementCategory.SPECIAL,
                "rarity": AchievementRarity.EPIC,
                "points": 75,
                "icon": "🔥",
                "condition": lambda data: data.get("previous_profit", 0) < 0
                and data.get("profit", 0) >= 1000,
            },
            {
                "id": "perfectionist",
                "name": "Perfectionniste",
                "description": "Terminez une partie sans jamais perdre d'argent",
                "category": AchievementCategory.SPECIAL,
                "rarity": AchievementRarity.LEGENDARY,
                "points": 150,
                "icon": "🏅",
                "condition": lambda data: data.get("game_completed", False)
                and data.get("min_profit", 0) >= 0,
                "hidden": True,
            },
            {
                "id": "speed_runner",
                "name": "Speed Runner",
                "description": "Atteignez 1M€ de CA en moins de 10 tours",
                "category": AchievementCategory.SPECIAL,
                "rarity": AchievementRarity.LEGENDARY,
                "points": 200,
                "icon": "🚀",
                "condition": lambda data: data.get("total_revenue", 0) >= 1000000
                and data.get("turn", 11) <= 10,
                "hidden": True,
            },
        ]

        # Créer les objets Achievement
        for ach_data in achievements_data:
            achievement = Achievement(
                id=ach_data["id"],
                name=ach_data["name"],
                description=ach_data["description"],
                category=ach_data["category"],
                rarity=ach_data["rarity"],
                points=ach_data["points"],
                icon=ach_data["icon"],
                condition_func=ach_data["condition"],
                hidden=ach_data.get("hidden", False),
            )

            self.achievements[achievement.id] = achievement

    def check_achievements(self, game_data: Dict[str, Any]) -> List[Achievement]:
        """
        Vérifie et débloque les achievements basés sur les données de jeu.

        Args:
            game_data: Données actuelles du jeu

        Returns:
            Liste des nouveaux achievements débloqués
        """
        newly_unlocked = []

        for achievement in self.achievements.values():
            if achievement.is_unlocked():
                continue

            if achievement.condition_func and achievement.condition_func(game_data):
                achievement.unlock()
                newly_unlocked.append(achievement)
                self.unlocked_achievements.append(achievement.id)
                self.total_points += achievement.points

        return newly_unlocked

    def get_achievement_progress(self) -> Dict[str, Any]:
        """Retourne les statistiques de progression des achievements."""
        total_achievements = len(self.achievements)
        unlocked_count = len(self.unlocked_achievements)

        # Compter par catégorie
        category_stats = {}
        for category in AchievementCategory:
            category_achievements = [
                a for a in self.achievements.values() if a.category == category
            ]
            category_unlocked = [a for a in category_achievements if a.is_unlocked()]

            category_stats[category.value] = {
                "total": len(category_achievements),
                "unlocked": len(category_unlocked),
                "percentage": len(category_unlocked) / len(category_achievements) * 100
                if category_achievements
                else 0,
            }

        # Compter par rareté
        rarity_stats = {}
        for rarity in AchievementRarity:
            rarity_achievements = [
                a for a in self.achievements.values() if a.rarity == rarity
            ]
            rarity_unlocked = [a for a in rarity_achievements if a.is_unlocked()]

            rarity_stats[rarity.value] = {
                "total": len(rarity_achievements),
                "unlocked": len(rarity_unlocked),
            }

        return {
            "total_achievements": total_achievements,
            "unlocked_achievements": unlocked_count,
            "completion_percentage": unlocked_count / total_achievements * 100,
            "total_points": self.total_points,
            "category_stats": category_stats,
            "rarity_stats": rarity_stats,
        }

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Retourne la liste des achievements débloqués."""
        return [self.achievements[ach_id] for ach_id in self.unlocked_achievements]

    def get_available_achievements(
        self, include_hidden: bool = False
    ) -> List[Achievement]:
        """Retourne la liste des achievements disponibles (non débloqués)."""
        available = []

        for achievement in self.achievements.values():
            if achievement.is_unlocked():
                continue

            if achievement.hidden and not include_hidden:
                continue

            available.append(achievement)

        return available

    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Retourne un achievement par son ID."""
        return self.achievements.get(achievement_id)

    def format_achievement_notification(self, achievement: Achievement) -> str:
        """Formate une notification d'achievement débloqué."""
        rarity_colors = {
            AchievementRarity.COMMON: "🟢",
            AchievementRarity.UNCOMMON: "🔵",
            AchievementRarity.RARE: "🟣",
            AchievementRarity.EPIC: "🟠",
            AchievementRarity.LEGENDARY: "🟡",
        }

        color = rarity_colors.get(achievement.rarity, "⚪")

        notification = f"\n🎉 ACHIEVEMENT DÉBLOQUÉ ! {color}\n"
        notification += f"{achievement.icon} {achievement.name}\n"
        notification += f"📝 {achievement.description}\n"
        notification += f"🏆 +{achievement.points} points\n"
        notification += f"💎 Rareté: {achievement.rarity.value.title()}"

        return notification

    def get_leaderboard_data(self) -> Dict[str, Any]:
        """Retourne les données pour un classement."""
        return {
            "total_points": self.total_points,
            "achievements_unlocked": len(self.unlocked_achievements),
            "completion_rate": len(self.unlocked_achievements)
            / len(self.achievements)
            * 100,
            "rare_achievements": len(
                [
                    a
                    for a in self.get_unlocked_achievements()
                    if a.rarity
                    in [
                        AchievementRarity.RARE,
                        AchievementRarity.EPIC,
                        AchievementRarity.LEGENDARY,
                    ]
                ]
            ),
        }
