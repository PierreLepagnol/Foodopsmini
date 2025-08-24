"""
Gestionnaire de sauvegarde et chargement
"""

import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class SaveManager:
    """Gestionnaire de sauvegarde et chargement des parties."""

    def __init__(self, save_directory: str = "saves"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)

    def save_game(self, game_data: dict[str, Any], save_name: str) -> str:
        """
        Sauvegarde une partie en cours.

        Args:
            game_data: Données de la partie
            save_name: Nom de la sauvegarde (optionnel)

        Returns:
            Nom du fichier de sauvegarde créé
        """
        if save_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"partie_{timestamp}"

        # Préparer les données pour la sérialisation
        serializable_data = self._prepare_for_serialization(game_data)

        # Ajouter les métadonnées
        save_data = {
            "metadata": {
                "save_name": save_name,
                "save_date": datetime.now().isoformat(),
                "game_version": "1.0",
                "turn": game_data.get("current_turn", 1),
                "players": len(game_data.get("restaurants", [])),
                "scenario": game_data.get("scenario_name", "Standard"),
            },
            "game_data": serializable_data,
        }

        # Sauvegarder dans un fichier JSON
        save_file = self.save_directory / f"{save_name}.json"

        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        return save_name

    def load_game(self, save_name: str) -> dict[str, Any]:
        """
        Charge une partie sauvegardée.

        Args:
            save_name: Nom de la sauvegarde

        Returns:
            Données de la partie chargée
        """
        save_file = self.save_directory / f"{save_name}.json"

        if not save_file.exists():
            raise FileNotFoundError(f"Sauvegarde '{save_name}' introuvable")

        with open(save_file, encoding="utf-8") as f:
            save_data = json.load(f)

        # Vérifier la version
        metadata = save_data.get("metadata", {})
        if metadata.get("game_version") != "1.0":
            print("⚠️ Version de sauvegarde différente, compatibilité non garantie")

        # Restaurer les données
        game_data = self._restore_from_serialization(save_data["game_data"])
        game_data["metadata"] = metadata

        return game_data

    def list_saves(self) -> list[dict[str, Any]]:
        """
        Liste toutes les sauvegardes disponibles.

        Returns:
            Liste des métadonnées des sauvegardes
        """
        saves = []

        for save_file in self.save_directory.glob("*.json"):
            with open(save_file, encoding="utf-8") as f:
                save_data = json.load(f)

            metadata = save_data.get("metadata", {})
            metadata["file_name"] = save_file.stem
            metadata["file_size"] = save_file.stat().st_size

            saves.append(metadata)

        # Trier par date de sauvegarde (plus récent en premier)
        saves.sort(key=lambda x: x.get("save_date", ""), reverse=True)

        return saves

    def delete_save(self, save_name: str) -> bool:
        """
        Supprime une sauvegarde.

        Args:
            save_name: Nom de la sauvegarde

        Returns:
            True si supprimée avec succès
        """
        save_file = self.save_directory / f"{save_name}.json"

        if save_file.exists():
            save_file.unlink()
            return True

        return False

    def _prepare_for_serialization(self, data: Any) -> Any:
        """Prépare les données pour la sérialisation JSON."""
        if isinstance(data, dict):
            return {
                key: self._prepare_for_serialization(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._prepare_for_serialization(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        elif hasattr(data, "__dict__"):
            # Objet avec attributs - convertir en dictionnaire
            if hasattr(data, "__dataclass_fields__"):
                # Dataclass
                return {
                    "__class__": data.__class__.__name__,
                    "__module__": data.__class__.__module__,
                    **self._prepare_for_serialization(asdict(data)),
                }
            else:
                # Objet normal
                return {
                    "__class__": data.__class__.__name__,
                    "__module__": data.__class__.__module__,
                    **self._prepare_for_serialization(data.__dict__),
                }
        else:
            return data

    def _restore_from_serialization(self, data: Any) -> Any:
        """Restaure les données depuis la sérialisation JSON."""
        if isinstance(data, dict):
            if "__class__" in data and "__module__" in data:
                # Objet sérialisé - pour l'instant, retourner comme dictionnaire
                # TODO: Implémenter la désérialisation complète des objets
                restored_data = {
                    key: self._restore_from_serialization(value)
                    for key, value in data.items()
                    if key not in ["__class__", "__module__"]
                }
                restored_data["__original_class__"] = data["__class__"]
                return restored_data
            else:
                return {
                    key: self._restore_from_serialization(value)
                    for key, value in data.items()
                }
        elif isinstance(data, list):
            return [self._restore_from_serialization(item) for item in data]
        else:
            return data

    def export_save(self, save_name: str, export_path: str) -> bool:
        """
        Exporte une sauvegarde vers un fichier externe.

        Args:
            save_name: Nom de la sauvegarde
            export_path: Chemin d'export

        Returns:
            True si exportée avec succès
        """
        save_file = self.save_directory / f"{save_name}.json"
        export_file = Path(export_path)

        if save_file.exists():
            import shutil

            shutil.copy2(save_file, export_file)
            return True

        return False

    def import_save(self, import_path: str, save_name: str = None) -> str:
        """
        Importe une sauvegarde depuis un fichier externe.

        Args:
            import_path: Chemin du fichier à importer
            save_name: Nom pour la sauvegarde importée

        Returns:
            Nom de la sauvegarde importée
        """
        import_file = Path(import_path)

        if not import_file.exists():
            raise FileNotFoundError(f"Fichier d'import introuvable: {import_path}")

        # Valider le fichier
        with open(import_file, encoding="utf-8") as f:
            save_data = json.load(f)

        if "metadata" not in save_data or "game_data" not in save_data:
            raise ValueError("Format de sauvegarde invalide")

        # Déterminer le nom de sauvegarde
        if save_name is None:
            original_name = save_data["metadata"].get("save_name", "import")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"{original_name}_import_{timestamp}"

        # Copier le fichier
        import shutil

        target_file = self.save_directory / f"{save_name}.json"
        shutil.copy2(import_file, target_file)

        return save_name

    def get_save_info(self, save_name: str) -> dict[str, Any]:
        """
        Récupère les informations détaillées d'une sauvegarde.

        Args:
            save_name: Nom de la sauvegarde

        Returns:
            Informations détaillées
        """
        save_file = self.save_directory / f"{save_name}.json"

        if not save_file.exists():
            raise FileNotFoundError(f"Sauvegarde '{save_name}' introuvable")

        with open(save_file, encoding="utf-8") as f:
            save_data = json.load(f)

        metadata = save_data.get("metadata", {})
        game_data = save_data.get("game_data", {})

        # Analyser les données de jeu
        restaurants = game_data.get("restaurants", [])

        info = {
            **metadata,
            "file_size": save_file.stat().st_size,
            "restaurants_count": len(restaurants),
            "restaurant_names": [
                r.get("name", "Restaurant") for r in restaurants[:3]
            ],  # 3 premiers
            "current_turn": game_data.get("current_turn", 1),
            "total_turns": game_data.get("total_turns", 10),
        }

        return info

    def cleanup_old_saves(self, keep_count: int = 10) -> int:
        """
        Nettoie les anciennes sauvegardes.

        Args:
            keep_count: Nombre de sauvegardes à conserver

        Returns:
            Nombre de sauvegardes supprimées
        """
        saves = self.list_saves()

        if len(saves) <= keep_count:
            return 0

        # Supprimer les plus anciennes
        to_delete = saves[keep_count:]
        deleted_count = 0

        for save in to_delete:
            if self.delete_save(save["file_name"]):
                deleted_count += 1

        return deleted_count
