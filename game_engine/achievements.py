"""
Système d'achievements/succès
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


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
    condition_func: Callable[[dict[str, Any]], bool] = None
    hidden: bool = False  # Achievement secret

    # Métadonnées
    unlock_date: datetime | None = None
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
        self.achievements: dict[str, Achievement] = {}
        self.unlocked_achievements: list[str] = []
        self.total_points = 0

        # Charger les achievements
        self._load_achievements()

    def _load_achievements(self) -> None:
        """Charge la liste des achievements disponibles."""
        with open("data/achievements.json", "r") as f:
            achievements_data = json.load(f)

        for ach_data in achievements_data:
            achievement = Achievement(**ach_data)
            self.achievements[achievement.id] = achievement

    def check_achievements(self, game_data: dict[str, Any]) -> list[Achievement]:
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

    def get_achievement_progress(self) -> dict[str, Any]:
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

    def get_unlocked_achievements(self) -> list[Achievement]:
        """Retourne la liste des achievements débloqués."""
        return [self.achievements[ach_id] for ach_id in self.unlocked_achievements]

    def get_available_achievements(
        self, include_hidden: bool = False
    ) -> list[Achievement]:
        """Retourne la liste des achievements disponibles (non débloqués)."""
        available = []

        for achievement in self.achievements.values():
            if achievement.is_unlocked():
                continue

            if achievement.hidden and not include_hidden:
                continue

            available.append(achievement)

        return available

    def get_achievement_by_id(self, achievement_id: str) -> Achievement | None:
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

    def get_leaderboard_data(self) -> dict[str, Any]:
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
