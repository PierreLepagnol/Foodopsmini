from __future__ import annotations

"""Module de parcours pédagogique pour FoodOps.

Ce module propose une structure simple pour définir des modules
pédagogiques avec objectif, quiz de validation et génération
de certificat lorsque tout le parcours est complété.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class QuizQuestion:
    """Représente une question de quiz."""

    question: str
    options: List[str]
    answer_index: int  # index de la bonne réponse dans ``options``

    def is_correct(self, choice: int) -> bool:
        """Vérifie si la réponse choisie est correcte."""
        return choice == self.answer_index


@dataclass
class TrainingModule:
    """Module d'apprentissage avec objectif et quiz."""

    name: str
    objective: str
    quiz: List[QuizQuestion] = field(default_factory=list)


@dataclass
class TrainingPath:
    """Parcours de formation composé de plusieurs modules."""

    modules: List[TrainingModule]
    current_index: int = 0

    def current_module(self) -> TrainingModule | None:
        """Retourne le module en cours ou ``None`` si terminé."""
        if self.current_index < len(self.modules):
            return self.modules[self.current_index]
        return None

    def answer_current_quiz(self, choice: int) -> bool:
        """Valide la réponse du quiz du module courant.

        Si la réponse est correcte, passe au module suivant.
        """
        module = self.current_module()
        if not module or not module.quiz:
            return False
        question = module.quiz[0]
        ok = question.is_correct(choice)
        if ok:
            self.current_index += 1
        return ok

    def is_completed(self) -> bool:
        """Indique si tous les modules ont été validés."""
        return self.current_index >= len(self.modules)

    def generate_certificate(self, learner: str, filename: str | None = None) -> str:
        """Génère un certificat simple pour l'apprenant.

        Parameters
        ----------
        learner: str
            Nom de l'apprenant.
        filename: str | None
            Chemin du fichier où sauvegarder le certificat. Si ``None``,
            le certificat est seulement renvoyé.

        Returns
        -------
        str
            Le texte du certificat généré.

        Raises
        ------
        ValueError
            Si le parcours n'est pas terminé.
        """
        if not self.is_completed():
            raise ValueError("Parcours non terminé")
        certificate = (
            f"Certificat de réussite - {learner}\n" f"Modules complétés: {len(self.modules)}"
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(certificate)
        return certificate


# Parcours par défaut utilisé par l'application ou les tests
DEFAULT_PATH = TrainingPath(
    modules=[
        TrainingModule(
            name="Gestion des stocks FEFO",
            objective="Gérer son stock avec la méthode First Expired, First Out.",
            quiz=[
                QuizQuestion(
                    question="Quel est l'objectif principal de la méthode FEFO ?",
                    options=[
                        "Vendre en premier les produits les plus chers",
                        "Utiliser d'abord les produits qui expirent le plus tôt",
                        "Réduire les coûts de main d'œuvre",
                    ],
                    answer_index=1,
                )
            ],
        ),
        TrainingModule(
            name="Menu engineering",
            objective="Optimiser son menu pour améliorer la marge.",
            quiz=[
                QuizQuestion(
                    question="Quelle action améliore la marge d'une recette ?",
                    options=[
                        "Augmenter le prix sans toucher aux ingrédients",
                        "Diminuer la taille de la portion ou le coût des ingrédients",
                        "Augmenter le nombre de serveurs",
                    ],
                    answer_index=1,
                )
            ],
        ),
        TrainingModule(
            name="Comptabilité de base",
            objective="Calculer un compte de résultat simplifié.",
            quiz=[
                QuizQuestion(
                    question="Quel élément n'entre pas dans le compte de résultat ?",
                    options=[
                        "Chiffre d'affaires",
                        "Stock de marchandises",
                        "Charges d'exploitation",
                    ],
                    answer_index=1,
                )
            ],
        ),
    ]
)

