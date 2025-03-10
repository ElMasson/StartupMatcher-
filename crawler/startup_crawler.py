"""
Fonction spécifique pour crawler et gérer les données des startups
"""
import logging
import os
import json
import threading
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# Tentative d'importation de schedule, mais on peut fonctionner sans
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    logging.warning("Le module 'schedule' n'est pas installé. Les mises à jour périodiques automatiques ne seront pas disponibles.")
    logging.warning("Pour installer schedule: pip install schedule")

from crawler.firecrawl_handler import run_crawler, load_cache_data, load_cache_info
from crawler.utils import load_crawl_results, save_crawl_results
from crawler.ft_reunion_crawler import FrenchTechReunionCrawler

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Verrou pour les opérations thread-safe
data_lock = threading.Lock()

# Cache en mémoire
_startup_data_cache = None
_last_cache_check = None
_background_thread = None
_background_running = False

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


def is_crawl_outdated(filepath: str, max_age_days: int = 1) -> bool:
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


def background_update():
    """
    Fonction pour la mise à jour en arrière-plan des données
    """
    global _background_running

    _background_running = True
    logger.info("Démarrage du thread de mise à jour en arrière-plan")

    def update_job():
        """Tâche de mise à jour périodique"""
        with data_lock:
            logger.info("Exécution de la mise à jour périodique des données des startups")
            try:
                # Force le rafraîchissement des données
                get_startup_data(force_refresh=True)
                logger.info("Mise à jour périodique terminée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour périodique: {e}")

    if SCHEDULE_AVAILABLE:
        # Planifier la mise à jour quotidienne à 3h du matin
        schedule.every().day.at("03:00").do(update_job)

        # Boucle principale du thread d'arrière-plan
        while _background_running:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    else:
        # Version simplifiée sans schedule: mise à jour toutes les 24 heures
        while _background_running:
            update_job()
            # Attendre 24 heures
            sleep_time = 24 * 60 * 60  # 24 heures en secondes

            # Diviser le temps d'attente en intervalles pour vérifier si le thread doit s'arrêter
            interval = 60  # 1 minute
            for _ in range(sleep_time // interval):
                if not _background_running:
                    break
                time.sleep(interval)


def start_background_updates():
    """
    Démarre le thread de mise à jour en arrière-plan
    """
    global _background_thread, _background_running

    if _background_thread is None or not _background_thread.is_alive():
        _background_running = True
        _background_thread = threading.Thread(target=background_update, daemon=True)
        _background_thread.start()
        if SCHEDULE_AVAILABLE:
            logger.info("Thread de mise à jour en arrière-plan démarré avec schedule")
        else:
            logger.info("Thread de mise à jour en arrière-plan démarré (mode simplifié)")


def stop_background_updates():
    """
    Arrête le thread de mise à jour en arrière-plan
    """
    global _background_running

    if _background_running:
        _background_running = False
        logger.info("Arrêt du thread de mise à jour en arrière-plan")


def check_cache_freshness() -> Tuple[bool, Optional[str]]:
    """
    Vérifie si le cache est frais ou s'il doit être mis à jour

    Returns:
        Tuple (est_frais, raison)
    """
    # Vérifier l'info du cache
    cache_info = load_cache_info()

    if not cache_info:
        return False, "Pas d'information de cache trouvée"

    last_update = datetime.fromisoformat(cache_info.get("last_update", "2000-01-01T00:00:00"))
    now = datetime.now()

    # Si le cache a plus de 24 heures
    if (now - last_update).total_seconds() > 86400:
        return False, f"Cache trop ancien (dernière mise à jour: {last_update.isoformat()})"

    # Si le cache a un statut d'erreur, vérifier s'il a plus de 1 heure
    if cache_info.get("status") == "error" and (now - last_update).total_seconds() > 3600:
        return False, f"Cache en erreur et âgé de plus d'une heure"

    # Si le cache est en mode fallback, vérifier s'il a plus de 4 heures
    if cache_info.get("status") == "fallback" and (now - last_update).total_seconds() > 14400:
        return False, f"Cache en mode fallback et âgé de plus de 4 heures"

    return True, None


def get_startup_data(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Obtient les données des startups, soit depuis un cache récent,
    soit en lançant un nouveau crawl, avec gestion de cache en mémoire

    Args:
        force_refresh: Force un nouveau crawl même si un cache récent existe

    Returns:
        Liste des données des startups
    """
    global _startup_data_cache, _last_cache_check

    # Verrou pour les opérations thread-safe
    with data_lock:
        current_time = datetime.now()

        # Si on doit forcer le rafraîchissement
        if force_refresh:
            logger.info("Forçage du rafraîchissement des données des startups")

            try:
                # Essayer d'abord avec le crawler spécifique à La French Tech Réunion
                ft_crawler = FrenchTechReunionCrawler()
                startups = ft_crawler.run()

                if startups:
                    logger.info(f"Le crawler La French Tech Réunion a trouvé {len(startups)} startups")
                    # Sauvegarder les résultats
                    save_crawl_results(startups)

                    # Enregistrer aussi dans le fichier des startups manuelles
                    manual_file = "data/startups_manual.json"

                    try:
                        # Essayer d'abord de lire les startups existantes
                        if os.path.exists(manual_file):
                            with open(manual_file, 'r', encoding='utf-8') as f:
                                existing_startups = json.load(f)
                        else:
                            existing_startups = []

                        # Fusionner avec les nouvelles startups (en évitant les doublons)
                        existing_ids = {s.get("id") for s in existing_startups}
                        startups_to_add = [s for s in startups if s.get("id") not in existing_ids]

                        # Combiner les listes
                        combined_startups = existing_startups + startups_to_add

                        # Sauvegarder dans le fichier manuel
                        os.makedirs(os.path.dirname(manual_file), exist_ok=True)
                        with open(manual_file, 'w', encoding='utf-8') as f:
                            json.dump(combined_startups, f, ensure_ascii=False, indent=2)

                        logger.info(f"Ajouté {len(startups_to_add)} nouvelles startups au fichier manuel")
                    except Exception as e:
                        logger.error(f"Erreur lors de la sauvegarde dans le fichier manuel: {e}")

                    _startup_data_cache = startups
                    _last_cache_check = current_time
                    return startups
                else:
                    logger.warning(
                        "Le crawler La French Tech Réunion n'a trouvé aucune startup, essai avec le crawler générique")
            except Exception as e:
                logger.error(f"Erreur avec le crawler La French Tech Réunion: {e}")
                logger.info("Essai avec le crawler générique...")

            # Si le crawler spécifique a échoué, utiliser le crawler générique
            _startup_data_cache = run_crawler(force_refresh=True)
            _last_cache_check = current_time
            return _startup_data_cache

        # Si le cache en mémoire est disponible et a été vérifié récemment (moins de 10 minutes)
        if (_startup_data_cache is not None and _last_cache_check is not None and
                (current_time - _last_cache_check).total_seconds() < 600):
            logger.info("Utilisation du cache en mémoire (vérifié il y a moins de 10 minutes)")
            return _startup_data_cache

        # Vérifier si le cache sur disque est frais
        is_fresh, reason = check_cache_freshness()

        if is_fresh:
            # Charger depuis le cache sur disque
            logger.info("Chargement des données depuis le cache sur disque")
            _startup_data_cache = load_cache_data()
            _last_cache_check = current_time

            # Démarrer le thread de mise à jour en arrière-plan si ce n'est pas déjà fait
            if not _background_running:
                start_background_updates()

            return _startup_data_cache
        else:
            # Lancer un nouveau crawl
            logger.info(f"Rafraîchissement des données: {reason}")

            try:
                # Essayer d'abord avec le crawler spécifique à La French Tech Réunion
                ft_crawler = FrenchTechReunionCrawler()
                startups = ft_crawler.run()

                if startups:
                    logger.info(f"Le crawler La French Tech Réunion a trouvé {len(startups)} startups")
                    # Sauvegarder les résultats
                    save_crawl_results(startups)

                    # Enregistrer aussi dans le fichier des startups manuelles
                    manual_file = "data/startups_manual.json"

                    try:
                        # Essayer d'abord de lire les startups existantes
                        if os.path.exists(manual_file):
                            with open(manual_file, 'r', encoding='utf-8') as f:
                                existing_startups = json.load(f)
                        else:
                            existing_startups = []

                        # Fusionner avec les nouvelles startups (en évitant les doublons)
                        existing_ids = {s.get("id") for s in existing_startups}
                        startups_to_add = [s for s in startups if s.get("id") not in existing_ids]

                        # Combiner les listes
                        combined_startups = existing_startups + startups_to_add

                        # Sauvegarder dans le fichier manuel
                        os.makedirs(os.path.dirname(manual_file), exist_ok=True)
                        with open(manual_file, 'w', encoding='utf-8') as f:
                            json.dump(combined_startups, f, ensure_ascii=False, indent=2)

                        logger.info(f"Ajouté {len(startups_to_add)} nouvelles startups au fichier manuel")
                    except Exception as e:
                        logger.error(f"Erreur lors de la sauvegarde dans le fichier manuel: {e}")

                    _startup_data_cache = startups
                    _last_cache_check = current_time

                    # Démarrer le thread de mise à jour en arrière-plan si ce n'est pas déjà fait
                    if not _background_running:
                        start_background_updates()

                    return startups
                else:
                    logger.warning(
                        "Le crawler La French Tech Réunion n'a trouvé aucune startup, essai avec le crawler générique")
            except Exception as e:
                logger.error(f"Erreur avec le crawler La French Tech Réunion: {e}")
                logger.info("Essai avec le crawler générique...")

            # Si le crawler spécifique a échoué, utiliser le crawler générique
            _startup_data_cache = run_crawler()
            _last_cache_check = current_time

            # Démarrer le thread de mise à jour en arrière-plan si ce n'est pas déjà fait
            if not _background_running:
                start_background_updates()

            return _startup_data_cache


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
        # Calcul d'un score de pertinence
        score = 0

        # Recherche dans le nom (poids élevé)
        if "name" in startup and startup["name"]:
            name_lower = startup["name"].lower()
            if query in name_lower:
                score += 10
                # Bonus si le query est au début du nom
                if name_lower.startswith(query):
                    score += 5

        # Recherche dans la description
        if "description" in startup and startup["description"]:
            if query in startup["description"].lower():
                score += 5

        # Recherche dans les tags (poids moyen)
        if "tags" in startup:
            for tag in startup["tags"]:
                if query in tag.lower():
                    score += 7
                    break

        # Recherche dans le domaine (poids élevé)
        if "domain" in startup and startup["domain"]:
            if query in startup["domain"].lower():
                score += 8

        # Recherche dans la localisation
        if "location" in startup and startup["location"]:
            if query in startup["location"].lower():
                score += 3

        # Si on a trouvé quelque chose, ajouter à la liste des résultats
        if score > 0:
            # Ajouter le score pour tri ultérieur
            startup_with_score = startup.copy()
            startup_with_score["_search_score"] = score
            results.append(startup_with_score)

    # Trier par score décroissant
    results.sort(key=lambda x: x.get("_search_score", 0), reverse=True)

    # Supprimer le score des résultats
    for result in results:
        if "_search_score" in result:
            del result["_search_score"]

    return results


def get_startup_by_id(startup_id: str, startups_data: List[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Récupère une startup par son ID

    Args:
        startup_id: ID de la startup
        startups_data: Données des startups (si None, les données seront chargées)

    Returns:
        Données de la startup ou None si non trouvée
    """
    if startups_data is None:
        startups_data = get_startup_data()

    for startup in startups_data:
        if startup.get("id") == startup_id:
            return startup

    return None


def get_startup_by_name(name: str, startups_data: List[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Récupère une startup par son nom

    Args:
        name: Nom de la startup
        startups_data: Données des startups (si None, les données seront chargées)

    Returns:
        Données de la startup ou None si non trouvée
    """
    if startups_data is None:
        startups_data = get_startup_data()

    name_lower = name.lower()
    for startup in startups_data:
        if startup.get("name", "").lower() == name_lower:
            return startup

    return None


def get_startups_by_domain(domain: str, startups_data: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Récupère les startups par domaine d'activité

    Args:
        domain: Domaine d'activité
        startups_data: Données des startups (si None, les données seront chargées)

    Returns:
        Liste des startups du domaine spécifié
    """
    if startups_data is None:
        startups_data = get_startup_data()

    domain_lower = domain.lower()
    return [
        startup for startup in startups_data
        if startup.get("domain", "").lower() == domain_lower
    ]


def get_startups_by_tag(tag: str, startups_data: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Récupère les startups par tag

    Args:
        tag: Tag à rechercher
        startups_data: Données des startups (si None, les données seront chargées)

    Returns:
        Liste des startups ayant le tag spécifié
    """
    if startups_data is None:
        startups_data = get_startup_data()

    tag_lower = tag.lower()
    return [
        startup for startup in startups_data
        if any(t.lower() == tag_lower for t in startup.get("tags", []))
    ]