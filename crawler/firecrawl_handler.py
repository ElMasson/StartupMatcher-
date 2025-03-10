"""
Gestion du crawling avec système de cache
"""
import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import FIRECRAWL_CONFIG
from crawler.utils import clean_startup_data, save_crawl_results
from crawler.web_crawler import Crawler

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dossier de cache
CACHE_DIR = "data/cache"

def ensure_cache_dir():
    """
    S'assure que le dossier de cache existe
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_info_path():
    """
    Retourne le chemin du fichier d'information de cache
    """
    return os.path.join(CACHE_DIR, "cache_info.json")

def get_cache_data_path():
    """
    Retourne le chemin du fichier de données en cache
    """
    return os.path.join(CACHE_DIR, "startups_data.json")

def save_cache_info(info: Dict[str, Any]):
    """
    Sauvegarde les informations du cache

    Args:
        info: Informations à sauvegarder
    """
    ensure_cache_dir()
    with open(get_cache_info_path(), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

def save_cache_data(data: List[Dict[str, Any]]):
    """
    Sauvegarde les données en cache

    Args:
        data: Données à sauvegarder
    """
    ensure_cache_dir()
    with open(get_cache_data_path(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cache_info() -> Optional[Dict[str, Any]]:
    """
    Charge les informations du cache

    Returns:
        Informations du cache ou None si non existant
    """
    path = get_cache_info_path()
    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erreur lors du chargement des infos du cache: {e}")
        return None

def load_cache_data() -> Optional[List[Dict[str, Any]]]:
    """
    Charge les données du cache

    Returns:
        Données en cache ou None si non existantes
    """
    path = get_cache_data_path()
    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erreur lors du chargement des données du cache: {e}")
        return None

def configure_crawler(config: Dict = None) -> Crawler:
    """
    Configure le crawler avec des paramètres optimisés

    Args:
        config: Configuration personnalisée (optionnel)

    Returns:
        Instance configurée du crawler
    """
    if config is None:
        config = FIRECRAWL_CONFIG

    # Configuration améliorée pour un crawling plus robuste
    crawler = Crawler(
        base_url=config["url"],
        selectors=config["selectors"],
        max_pages=config["max_pages"],
        delay_range=(1.5, 4.0)  # Délai plus important pour être respectueux du serveur
    )

    return crawler

def run_crawler(config: Dict = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Exécute le crawler avec gestion de cache intelligente

    Args:
        config: Configuration personnalisée (optionnel)
        force_refresh: Force un nouveau crawl même si le cache est récent

    Returns:
        Liste des données extraites
    """
    # Vérification du cache si on ne force pas le rafraîchissement
    if not force_refresh:
        cache_info = load_cache_info()
        cache_data = load_cache_data()

        # Si le cache existe et est valide (moins de 24h)
        if cache_info and cache_data:
            last_update = datetime.fromisoformat(cache_info.get("last_update", "2000-01-01T00:00:00"))
            now = datetime.now()
            # Vérifier si le cache a moins de 24 heures (86400 secondes)
            if (now - last_update).total_seconds() < 86400:
                logger.info(f"Utilisation des données en cache (dernière mise à jour: {last_update.isoformat()})")
                return cache_data
            else:
                logger.info(f"Cache expiré (dernière mise à jour: {last_update.isoformat()}). Rafraîchissement...")
        else:
            logger.info("Pas de cache valide trouvé. Exécution d'un nouveau crawl...")
    else:
        logger.info("Rafraîchissement forcé des données. Exécution d'un nouveau crawl...")

    # Préparation du crawler
    crawler = configure_crawler(config)

    try:
        # Tentative de crawling du site réel
        logger.info("Démarrage du crawling du site de La French Tech Réunion...")
        raw_results = crawler.crawl()

        if not raw_results:
            # Si aucun résultat, utiliser les données d'exemple
            logger.warning("Aucune donnée extraite. Utilisation des données d'exemple...")
            raw_results = crawler.get_sample_data()

            # Enregistrer l'échec dans l'info du cache
            cache_info = {
                "last_update": datetime.now().isoformat(),
                "status": "fallback",
                "count": len(raw_results),
                "message": "Échec du crawling, utilisation des données d'exemple"
            }
        else:
            # Enregistrer le succès dans l'info du cache
            cache_info = {
                "last_update": datetime.now().isoformat(),
                "status": "success",
                "count": len(raw_results),
                "message": "Crawling réussi"
            }

    except Exception as e:
        # En cas d'erreur, utiliser les données d'exemple
        logger.error(f"Erreur lors du crawling: {e}")
        logger.info("Utilisation des données d'exemple...")
        raw_results = crawler.get_sample_data()

        # Enregistrer l'erreur dans l'info du cache
        cache_info = {
            "last_update": datetime.now().isoformat(),
            "status": "error",
            "count": len(raw_results),
            "message": f"Erreur lors du crawling: {str(e)}"
        }

    # Nettoyage et normalisation des résultats
    cleaned_results = [clean_startup_data(result) for result in raw_results]

    # Sauvegarde des résultats dans le cache
    save_cache_info(cache_info)
    save_cache_data(cleaned_results)
    logger.info(f"Données mises en cache ({len(cleaned_results)} startups)")

    # Sauvegarde des résultats dans le fichier de crawl normal
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
        if "tags" in startup and startup["tags"]:
            for tag in startup["tags"]:
                if tag.strip():  # Vérifier que le tag n'est pas vide
                    metadata["tags"].add(tag.strip())

        # Collecte des domaines d'activité
        if "domain" in startup and startup["domain"]:
            metadata["domains"].add(startup["domain"].strip())

        # Collecte des localisations
        if "location" in startup and startup["location"]:
            metadata["locations"].add(startup["location"].strip())

    # Conversion des sets en listes triées pour la sérialisation JSON
    return {k: sorted(list(v)) for k, v in metadata.items()}

def get_startup_metadata() -> Dict[str, List[str]]:
    """
    Récupère les métadonnées des startups depuis le cache ou en faisant un crawl

    Returns:
        Dictionnaire des métadonnées
    """
    # Essayer de charger depuis le cache
    cache_data = load_cache_data()

    if cache_data:
        return extract_startup_metadata(cache_data)

    # Si pas de cache, faire un crawl
    startups_data = run_crawler()
    return extract_startup_metadata(startups_data)