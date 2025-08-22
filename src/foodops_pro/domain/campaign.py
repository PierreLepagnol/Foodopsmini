"""Gestionnaire de campagne pour enchaîner plusieurs scénarios."""

from dataclasses import dataclass, field
from typing import List

from .scenario import Scenario
from ..io.persistence import CampaignPersistence, CampaignProgress


@dataclass
class CampaignManager:
    """Gère une campagne composée de plusieurs scénarios.

    Attributes:
        name: Nom de la campagne.
        scenarios: Liste ordonnée des scénarios.
        persistence: Gestionnaire de persistance pour sauvegarder la progression.
    """

    name: str
    scenarios: List[Scenario]
    persistence: CampaignPersistence
    progress: CampaignProgress = field(init=False)

    def __post_init__(self) -> None:
        """Charge ou initialise la progression de la campagne."""
        scenario_names = [s.name for s in self.scenarios]
        loaded = self.persistence.load_progress(self.name)
        if loaded and loaded.scenario_names == scenario_names:
            self.progress = loaded
        else:
            self.progress = CampaignProgress(
                campaign_name=self.name,
                scenario_names=scenario_names,
                current_index=0,
            )
            self.persistence.save_progress(self.progress)

    def current_scenario(self) -> Scenario:
        """Retourne le scénario actuel."""
        return self.scenarios[self.progress.current_index]

    def advance(self) -> bool:
        """Avance au scénario suivant si possible et sauvegarde la progression.

        Returns:
            True si le scénario a changé, False si la campagne est terminée.
        """
        if self.progress.current_index < len(self.scenarios) - 1:
            self.progress.current_index += 1
            self.persistence.save_progress(self.progress)
            return True
        return False

    def is_completed(self) -> bool:
        """Indique si tous les scénarios de la campagne ont été terminés."""
        return self.progress.current_index >= len(self.scenarios) - 1

    def unlocked_features(self) -> List[str]:
        """Retourne toutes les fonctionnalités débloquées jusqu'à présent."""
        features: List[str] = []
        for idx in range(self.progress.current_index + 1):
            features.extend(self.scenarios[idx].new_features)
        return features
