"""Simple leaderboard utility for tracking player performance.

This module exposes a :class:`Leaderboard` class that stores scores for
players or teams and can return a ranking ordered by score. Scores are
numerical and higher values indicate better performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Leaderboard:
    """Maintain a mapping of player names to their scores.

    The leaderboard keeps track of numeric scores for each player or team.
    Scores can be updated or set directly. Rankings are returned in
    descending order (highest score first).
    """

    scores: Dict[str, float] = field(default_factory=dict)

    def set_score(self, player: str, value: float) -> None:
        """Set the absolute score for a player."""
        self.scores[player] = float(value)

    def update_score(self, player: str, delta: float) -> None:
        """Increment a player's score by ``delta``."""
        self.scores[player] = self.scores.get(player, 0.0) + float(delta)

    def reset(self) -> None:
        """Clear all scores from the leaderboard."""
        self.scores.clear()

    def get_ranking(self) -> List[Tuple[str, float]]:
        """Return the ranking as a list of ``(player, score)`` tuples."""
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
