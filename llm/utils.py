"""
Fonctions utilitaires pour le LLM
"""
import logging
import json
from typing import Dict, List, Any, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def format_message_history(messages: List[Dict[str, str]]) -> str:
    """
    Formate l'historique des messages pour le prompt

    Args:
        messages: Liste des messages

    Returns:
        Historique formaté
    """
    formatted_history = ""

    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")

        if role == "user":
            formatted_history += f"Utilisateur: {content}\n\n"
        elif role == "assistant":
            formatted_history += f"Assistant: {content}\n\n"
        elif role == "system":
            # Les messages système ne sont pas inclus dans l'historique formaté
            pass

    return formatted_history


def format_startup_for_llm(startup: Dict[str, Any]) -> str:
    """
    Formate les données d'une startup pour le LLM

    Args:
        startup: Données de la startup

    Returns:
        Texte formaté
    """
    return f"""
Nom: {startup.get('name', 'Non spécifié')}

Description: {startup.get('description', 'Non spécifiée')}

Tags: {', '.join(startup.get('tags', []))}

URL: {startup.get('url', 'Non spécifiée')}

Contact: {startup.get('contact', 'Non spécifié')}

Domaine d'activité: {startup.get('domain', 'Non spécifié')}

Localisation: {startup.get('location', 'Non spécifiée')}
"""


def format_startups_list_for_llm(startups: List[Dict[str, Any]]) -> str:
    """
    Formate une liste de startups pour le LLM

    Args:
        startups: Liste des startups

    Returns:
        Texte formaté
    """
    formatted_text = "Voici les startups pertinentes pour votre besoin:\n\n"

    for i, startup in enumerate(startups, 1):
        formatted_text += f"## Startup {i}: {startup.get('name', 'Non spécifié')}\n\n"
        formatted_text += format_startup_for_llm(startup)
        formatted_text += "\n" + "-" * 50 + "\n\n"

    return formatted_text


def parse_json_response(response: str) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
    """
    Analyse une réponse JSON du LLM

    Args:
        response: Réponse du LLM

    Returns:
        Données JSON analysées ou None en cas d'erreur
    """
    # Extraction du bloc JSON si présent
    start_marker = "```json"
    end_marker = "```"

    if start_marker in response:
        start_idx = response.find(start_marker) + len(start_marker)
        end_idx = response.find(end_marker, start_idx)

        if end_idx > start_idx:
            json_str = response[start_idx:end_idx].strip()

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Erreur lors de l'analyse JSON: {e}")
                return None

    # Tentative directe d'analyse JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Ce n'est pas du JSON valide
        return None