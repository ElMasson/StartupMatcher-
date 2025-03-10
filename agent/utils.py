"""
Fonctions utilitaires pour les agents
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
import json
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_intent(user_message: str) -> str:
    """
    Extrait l'intention principale du message utilisateur

    Args:
        user_message: Message de l'utilisateur

    Returns:
        Intention identifiée
    """
    # Patterns à rechercher pour chaque intention
    intent_patterns = {
        "search": [
            r"recherche", r"trouve", r"cherche", r"identifie", r"liste",
            r"quelles? startup", r"quelles? entreprises?"
        ],
        "combine": [
            r"combin", r"associe", r"synergie", r"ensembles?", r"plusieurs",
            r"paires?", r"groupes?"
        ],
        "details": [
            r"détails", r"plus d'info", r"en savoir plus", r"approfondi",
            r"contact", r"coordonnées"
        ],
        "refine": [
            r"affine", r"précise", r"filtre", r"spécifique", r"domaine",
            r"localisation", r"technologie"
        ]
    }

    # Recherche des patterns dans le message
    user_message_lower = user_message.lower()
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, user_message_lower):
                return intent

    # Par défaut, on considère qu'il s'agit d'une recherche
    return "search"


def parse_message_content(user_message: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Analyse le contenu du message utilisateur pour extraire des filtres

    Args:
        user_message: Message de l'utilisateur

    Returns:
        Tuple contenant le message nettoyé et un dictionnaire de filtres (ou None)
    """
    # Patterns pour les filtres explicites
    filter_patterns = {
        "tags": r"tags?[:\s]+([^.]+)",
        "domain": r"domaine[:\s]+([^.]+)",
        "location": r"localisation[:\s]+([^.]+)"
    }

    # Initialisation des filtres
    filters = {}

    # Recherche des filtres dans le message
    for filter_key, pattern in filter_patterns.items():
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            value = match.group(1).strip()

            # Traitement spécial pour les tags (liste)
            if filter_key == "tags":
                tags = [tag.strip() for tag in value.split(",")]
                filters[filter_key] = tags
            else:
                filters[filter_key] = value

    # Si aucun filtre n'a été trouvé, on retourne None
    if not filters:
        return user_message, None

    # Nettoyage du message pour retirer les filtres explicites
    cleaned_message = user_message
    for filter_key, pattern in filter_patterns.items():
        cleaned_message = re.sub(pattern, "", cleaned_message, flags=re.IGNORECASE)

    # Nettoyage des espaces et ponctuation en excès
    cleaned_message = re.sub(r'\s+', ' ', cleaned_message).strip()
    cleaned_message = re.sub(r'\s*[.,]\s*', '. ', cleaned_message).strip()

    return cleaned_message, filters


def format_agent_response(content: str, startups: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Formate la réponse de l'agent pour l'interface utilisateur

    Args:
        content: Contenu de la réponse
        startups: Liste des startups à afficher (optionnel)

    Returns:
        Réponse formatée
    """
    response = {
        "content": content,
        "has_startups": startups is not None and len(startups) > 0
    }

    if startups:
        response["startups"] = startups

    return response


def create_startup_summary(startup: Dict[str, Any]) -> str:
    """
    Crée un résumé d'une startup pour l'affichage rapide

    Args:
        startup: Données de la startup

    Returns:
        Résumé formaté
    """
    name = startup.get("name", "Startup sans nom")
    description = startup.get("description", "Pas de description disponible.")

    # Limitation de la description à 100 caractères
    if len(description) > 100:
        description = description[:97] + "..."

    # Récupération des tags
    tags = startup.get("tags", [])
    tags_str = ", ".join(tags[:3])  # Limiter à 3 tags
    if len(tags) > 3:
        tags_str += ", ..."

    # Construction du résumé
    summary = f"{name}: {description}"
    if tags_str:
        summary += f" [Tags: {tags_str}]"

    return summary