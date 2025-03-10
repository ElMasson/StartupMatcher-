"""
Fonctions utilitaires pour le crawling
"""
import json
import os
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dossier pour les données
DATA_DIR = "data"

def ensure_data_dir():
    """
    S'assure que le dossier de données existe
    """
    os.makedirs(DATA_DIR, exist_ok=True)

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
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Résultats du crawl sauvegardés dans {filepath}")
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
        logger.warning(f"Fichier {filepath} non trouvé")
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Fichier {filepath} chargé avec succès ({len(data)} startups)")
            return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erreur lors du chargement du fichier {filepath}: {e}")
        return []


def clean_startup_data(startup_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nettoie et normalise les données d'une startup

    Args:
        startup_data: Données brutes d'une startup

    Returns:
        Données nettoyées
    """
    # Création d'une copie pour ne pas modifier l'original
    cleaned_data = startup_data.copy()

    # Suppression des espaces en début et fin de chaîne
    for key, value in cleaned_data.items():
        if isinstance(value, str):
            cleaned_data[key] = value.strip()

    # Normalisation des tags (conversion en liste et nettoyage)
    if "tags" in cleaned_data:
        if isinstance(cleaned_data["tags"], str):
            # Conversion de la chaîne en liste en séparant par des virgules
            cleaned_data["tags"] = [tag.strip() for tag in cleaned_data["tags"].split(",")]

        # Filtrage des tags vides
        cleaned_data["tags"] = [tag for tag in cleaned_data["tags"] if tag]

        # Élimination des doublons
        cleaned_data["tags"] = list(set(cleaned_data["tags"]))

    # Assurer que tous les champs nécessaires existent
    required_fields = {
        "name": "",
        "description": "",
        "tags": [],
        "url": "",
        "contact": "",
        "domain": "",
        "location": "La Réunion"
    }

    for field, default_value in required_fields.items():
        if field not in cleaned_data or cleaned_data[field] is None:
            cleaned_data[field] = default_value

    # Générer ou vérifier l'ID de la startup
    if "id" not in cleaned_data or not cleaned_data["id"]:
        # Création d'un ID basé sur le nom
        name_hash = hashlib.md5(cleaned_data["name"].encode()).hexdigest()[:8]
        cleaned_data["id"] = f"startup-{name_hash}"

    # Nettoyage et normalisation de l'URL
    if "url" in cleaned_data and cleaned_data["url"]:
        url = cleaned_data["url"]
        # Ajouter http:// si aucun protocole n'est spécifié
        if not re.match(r'^https?://', url):
            url = f"http://{url}"
        cleaned_data["url"] = url

    # Extraction d'email dans le contact si possible
    if "contact" in cleaned_data and cleaned_data["contact"]:
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', cleaned_data["contact"])
        if email_match:
            cleaned_data["email"] = email_match.group(0)

    # Si aucun domaine spécifié, tenter de le déduire des tags
    if not cleaned_data["domain"] and cleaned_data["tags"]:
        cleaned_data["domain"] = cleaned_data["tags"][0]

    return cleaned_data


def hash_startup(startup: Dict[str, Any]) -> str:
    """
    Génère un hash unique pour une startup

    Args:
        startup: Données de la startup

    Returns:
        Hash unique
    """
    # Créer une représentation déterministe de la startup
    startup_str = json.dumps(
        {k: v for k, v in sorted(startup.items()) if k != "id"},
        sort_keys=True,
        ensure_ascii=False
    )

    # Générer le hash
    return hashlib.md5(startup_str.encode('utf-8')).hexdigest()


def compare_startups(old_startups: List[Dict[str, Any]], new_startups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare deux ensembles de startups pour identifier les ajouts, modifications et suppressions

    Args:
        old_startups: Ancien ensemble de startups
        new_startups: Nouvel ensemble de startups

    Returns:
        Dictionnaire contenant les listes d'ajouts, modifications et suppressions
    """
    result = {
        "added": [],
        "modified": [],
        "removed": [],
        "unchanged": []
    }

    # Créer des dictionnaires pour faciliter la recherche
    old_dict = {startup["id"]: startup for startup in old_startups if "id" in startup}
    new_dict = {startup["id"]: startup for startup in new_startups if "id" in startup}

    # Créer des dictionnaires de hash
    old_hashes = {startup_id: hash_startup(startup) for startup_id, startup in old_dict.items()}
    new_hashes = {startup_id: hash_startup(startup) for startup_id, startup in new_dict.items()}

    # Trouver les startups ajoutées (présentes dans new mais pas dans old)
    for startup_id, startup in new_dict.items():
        if startup_id not in old_dict:
            result["added"].append(startup)

    # Trouver les startups supprimées (présentes dans old mais pas dans new)
    for startup_id, startup in old_dict.items():
        if startup_id not in new_dict:
            result["removed"].append(startup)

    # Trouver les startups modifiées et inchangées
    for startup_id in set(old_dict.keys()) & set(new_dict.keys()):
        if old_hashes[startup_id] != new_hashes[startup_id]:
            result["modified"].append(new_dict[startup_id])
        else:
            result["unchanged"].append(new_dict[startup_id])

    return result


def merge_startup_data(existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fusionne de nouvelles données de startups avec des données existantes

    Args:
        existing_data: Données existantes
        new_data: Nouvelles données

    Returns:
        Données fusionnées
    """
    # Créer un dictionnaire des données existantes
    existing_dict = {startup["id"]: startup for startup in existing_data if "id" in startup}

    # Créer la liste fusionnée
    merged_data = []

    # Parcourir les nouvelles données
    for startup in new_data:
        if "id" in startup and startup["id"] in existing_dict:
            # Si la startup existe déjà, fusionner les données
            existing = existing_dict[startup["id"]]
            merged = existing.copy()

            # Mettre à jour avec les nouvelles données
            for key, value in startup.items():
                # Pour les tags, fusionner les listes
                if key == "tags" and "tags" in existing:
                    merged["tags"] = list(set(existing["tags"] + value))
                # Pour les autres champs, privilégier la nouvelle valeur si elle existe
                elif value:
                    merged[key] = value

            merged_data.append(merged)
            # Supprimer du dictionnaire pour marquer comme traité
            del existing_dict[startup["id"]]
        else:
            # Si c'est une nouvelle startup, l'ajouter telle quelle
            merged_data.append(startup)

    # Ajouter les startups existantes qui n'ont pas été mises à jour
    for startup in existing_dict.values():
        merged_data.append(startup)

    return merged_data


def get_last_crawl_stats() -> Optional[Dict[str, Any]]:
    """
    Récupère les statistiques du dernier crawl

    Returns:
        Statistiques du dernier crawl ou None si aucun crawl n'a été effectué
    """
    # Vérifier si le dossier de cache existe
    cache_dir = os.path.join(DATA_DIR, "cache")
    cache_info_path = os.path.join(cache_dir, "cache_info.json")

    if not os.path.exists(cache_info_path):
        return None

    try:
        with open(cache_info_path, 'r', encoding='utf-8') as f:
            cache_info = json.load(f)

        # Ajouter quelques statistiques supplémentaires
        cache_data_path = os.path.join(cache_dir, "startups_data.json")
        if os.path.exists(cache_data_path):
            with open(cache_data_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            domains = set(startup.get("domain", "") for startup in cache_data if "domain" in startup)
            locations = set(startup.get("location", "") for startup in cache_data if "location" in startup)

            # Ajouter au cache_info
            cache_info["domains_count"] = len(domains)
            cache_info["locations_count"] = len(locations)

            # Nombre total de tags
            tags_count = 0
            unique_tags = set()
            for startup in cache_data:
                if "tags" in startup:
                    tags_count += len(startup["tags"])
                    unique_tags.update(startup["tags"])

            cache_info["tags_total"] = tags_count
            cache_info["tags_unique"] = len(unique_tags)

        return cache_info

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erreur lors de la récupération des statistiques de crawl: {e}")
        return None