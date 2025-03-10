"""
Fonctions utilitaires pour le crawling
"""
import json
import os
from typing import Dict, List, Any
from datetime import datetime


def save_crawl_results(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Sauvegarde les résultats du crawl dans un fichier JSON

    Args:
        data: Données à sauvegarder
        filename: Nom du fichier (optionnel)

    Returns:
        Chemin du fichier sauvegardé
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"startups_crawl_{timestamp}.json"

    # Création du dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def load_crawl_results(filepath: str) -> List[Dict[str, Any]]:
    """
    Charge les résultats d'un crawl à partir d'un fichier JSON

    Args:
        filepath: Chemin du fichier à charger

    Returns:
        Données chargées
    """
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_startup_data(startup_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nettoie et normalise les données d'une startup

    Args:
        startup_data: Données brutes d'une startup

    Returns:
        Données nettoyées
    """
    # Suppression des espaces en début et fin de chaîne
    for key, value in startup_data.items():
        if isinstance(value, str):
            startup_data[key] = value.strip()

    # Normalisation des tags (conversion en liste si nécessaire)
    if "tags" in startup_data and isinstance(startup_data["tags"], str):
        startup_data["tags"] = [tag.strip() for tag in startup_data["tags"].split(",")]

    return startup_data