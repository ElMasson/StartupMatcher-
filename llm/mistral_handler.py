"""
Gestion des appels à l'API Mistral
"""
import os
import logging
from typing import Dict, List, Any, Union
from mistralai import Mistral, UserMessage, SystemMessage
from config import LLM_CONFIG

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation du client Mistral avec la nouvelle API
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def get_llm_config() -> Dict[str, Any]:
    """
    Récupère la configuration du LLM

    Returns:
        Configuration du LLM
    """
    return LLM_CONFIG.copy()

def call_mistral(messages: List[Dict[str, str]], config: Dict[str, Any] = None) -> str:
    """
    Appelle Mistral avec les messages fournis

    Args:
        messages: Liste des messages (format ChatCompletion)
        config: Configuration personnalisée (optionnel)

    Returns:
        Réponse du LLM
    """
    if config is None:
        config = get_llm_config()

    model = config.get("model", "mistral-large-latest")
    temperature = config.get("temperature", 0.2)
    max_tokens = config.get("max_tokens", 4000)

    logger.info(f"Appel de Mistral (modèle: {model}, temperature: {temperature})...")

    try:
        # Conversion des messages au format compatible avec la nouvelle API
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "").lower()
            content = msg.get("content", "")

            if role == "system":
                formatted_messages.append({"role": "system", "content": content})
            elif role == "user":
                formatted_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                formatted_messages.append({"role": "assistant", "content": content})
            else:
                # Par défaut, considérer comme un message utilisateur
                formatted_messages.append({"role": "user", "content": content})

        # Utilisation de la nouvelle méthode d'appel de l'API Mistral
        response = client.chat.complete(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extraction de la réponse
        content = response.choices[0].message.content
        logger.info("Réponse de Mistral reçue")

        return content

    except Exception as e:
        logger.error(f"Erreur lors de l'appel à Mistral: {e}")
        return f"Une erreur est survenue lors de la communication avec Mistral: {str(e)}"