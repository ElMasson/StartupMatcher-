"""
Fonction spécifique pour crawler les startups
"""
import logging
from typing import Dict, List, Any, Optional
import os
from datetime import datetime, timedelta

from crawler.firecrawl_handler import run_crawler, extract_startup_metadata
from crawler.utils import load_crawl_results, save_crawl_results

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_latest_crawl_file() -> Optional[str]:
    """
    Récupère le fichier de crawl le plus récent

    Returns:
        Chemin du fichier ou None si aucun fichier n'existe
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        return None

    crawl_files = [f for f in os.listdir(data_dir) if f.startswith("startups_crawl_") and f.endswith(".json")]
    if not crawl_files:
        return None

    # Tri par date de création
    crawl_files.sort(key=lambda x: os.path.getctime(os.path.join(data_dir, x)), reverse=True)
    return os.path.join(data_dir, crawl_files[0])


def is_crawl_outdated(filepath: str, max_age_days: int = 7) -> bool:
    """
    Vérifie si un crawl est trop ancien

    Args:
        filepath: Chemin du fichier de crawl
        max_age_days: Âge maximum en jours

    Returns:
        True si le crawl est trop ancien, False sinon
    """
    if not os.path.exists(filepath):
        return True

    file_timestamp = datetime.fromtimestamp(os.path.getctime(filepath))
    current_time = datetime.now()

    return (current_time - file_timestamp) > timedelta(days=max_age_days)


def get_startup_data(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Obtient les données des startups, soit depuis un cache récent,
    soit en lançant un nouveau crawl

    Args:
        force_refresh: Force un nouveau crawl même si un cache récent existe

    Returns:
        Liste des données des startups
    """
    latest_crawl = get_latest_crawl_file()

    # Si aucun crawl n'existe, ou s'il est trop ancien, ou si on force le rafraîchissement
    if latest_crawl is None or is_crawl_outdated(latest_crawl) or force_refresh:
        logger.info("Lancement d'un nouveau crawl des startups...")
        return run_crawler()

    # Sinon, on charge le crawl existant
    logger.info(f"Chargement des données depuis {latest_crawl}")
    return load_crawl_results(latest_crawl)


def search_startups(query: str, startups_data: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Recherche simple dans les données des startups

    Args:
        query: Requête de recherche
        startups_data: Données des startups (si None, les données seront chargées)

    Returns:
        Liste des startups correspondant à la requête
    """
    if startups_data is None:
        startups_data = get_startup_data()

    query = query.lower()
    results = []

    for startup in startups_data:
        # Recherche dans le nom
        if "name" in startup and query in startup["name"].lower():
            results.append(startup)
            continue

        # Recherche dans la description
        if "description" in startup and query in startup["description"].lower():
            results.append(startup)
            continue

        # Recherche dans les tags
        if "tags" in startup and any(query in tag.lower() for tag in startup["tags"]):
            results.append(startup)
            continue

    return results