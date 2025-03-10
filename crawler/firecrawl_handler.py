"""
Gestion du crawling
"""
import logging
from typing import Dict, List, Any
from config import FIRECRAWL_CONFIG
from crawler.utils import clean_startup_data, save_crawl_results
from crawler.web_crawler import Crawler

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def configure_crawler(config: Dict = None) -> Crawler:
    """
    Configure le crawler

    Args:
        config: Configuration personnalisée (optionnel)

    Returns:
        Instance configurée du crawler
    """
    if config is None:
        config = FIRECRAWL_CONFIG

    crawler = Crawler(
        base_url=config["url"],
        selectors=config["selectors"],
        max_pages=config["max_pages"]
    )

    return crawler

def run_crawler(config: Dict = None) -> List[Dict[str, Any]]:
    """
    Exécute le crawler et retourne les résultats

    Args:
        config: Configuration personnalisée (optionnel)

    Returns:
        Liste des données extraites
    """
    crawler = configure_crawler(config)

    try:
        # Tentative de crawling du site réel
        logger.info("Tentative de crawling du site réel...")
        raw_results = crawler.crawl()

        if not raw_results:
            # Si aucun résultat, utiliser les données d'exemple
            logger.warning("Aucune donnée extraite. Utilisation des données d'exemple...")
            raw_results = crawler.get_sample_data()
    except Exception as e:
        # En cas d'erreur, utiliser les données d'exemple
        logger.error(f"Erreur lors du crawling: {e}")
        logger.info("Utilisation des données d'exemple...")
        raw_results = crawler.get_sample_data()

    # Nettoyage et normalisation des résultats
    cleaned_results = [clean_startup_data(result) for result in raw_results]

    # Sauvegarde des résultats
    save_crawl_results(cleaned_results)

    return cleaned_results

def extract_startup_metadata(raw_results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Extrait les métadonnées des startups (tags, catégories, etc.)

    Args:
        raw_results: Résultats bruts du crawl

    Returns:
        Dictionnaire des métadonnées
    """
    metadata = {
        "tags": set(),
        "domains": set(),
        "locations": set()
    }

    for startup in raw_results:
        # Collecte des tags
        if "tags" in startup:
            for tag in startup["tags"]:
                metadata["tags"].add(tag)

        # Collecte des domaines d'activité
        if "domain" in startup:
            metadata["domains"].add(startup["domain"])

        # Collecte des localisations
        if "location" in startup:
            metadata["locations"].add(startup["location"])

    # Conversion des sets en listes pour la sérialisation JSON
    return {k: sorted(list(v)) for k, v in metadata.items()}