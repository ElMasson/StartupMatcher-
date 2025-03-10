"""
Gestion globale des agents
"""
import logging
from typing import Dict, List, Any, Optional
from agent.crew_manager import process_user_request
from llm.mistral_handler import call_mistral
from crawler.startup_crawler import get_startup_data

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentHandler:
    """
    Gestionnaire centralisé des agents IA
    """

    def __init__(self):
        """
        Initialisation du gestionnaire d'agents
        """
        # Cache pour les données des startups
        self._startup_data = None

    def get_startup_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les données des startups, en utilisant un cache si disponible

        Args:
            force_refresh: Force le rafraîchissement du cache

        Returns:
            Données des startups
        """
        if self._startup_data is None or force_refresh:
            logger.info("Récupération des données des startups...")
            self._startup_data = get_startup_data(force_refresh=force_refresh)

        return self._startup_data

    def process_user_message(self, user_message: str,
                           message_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Traite un message utilisateur et génère une réponse appropriée

        Args:
            user_message: Message de l'utilisateur
            message_history: Historique des messages (optionnel)

        Returns:
            Réponse formatée
        """
        logger.info(f"Traitement du message utilisateur: {user_message[:50]}...")

        # S'assurer que les données des startups sont chargées
        self.get_startup_data()

        # Utilisation de la crew d'agents pour traiter la requête
        try:
            return process_user_request(user_message, message_history)
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête avec CrewAI: {e}")

            # Fallback: utilisation directe de Mistral
            prompt = f"""
            Vous êtes un assistant spécialisé dans les startups de La French Tech Réunion.
            
            Requête de l'utilisateur: {user_message}
            
            Veuillez fournir une réponse utile basée sur vos connaissances générales des startups et de l'innovation.
            Si vous ne pouvez pas répondre précisément, proposez des suggestions générales ou des questions de clarification.
            """

            messages = [
                {"role": "system", "content": "Vous êtes un assistant spécialisé dans les startups de La French Tech Réunion."},
                {"role": "user", "content": prompt}
            ]

            response = call_mistral(messages)
            return {"content": response}

    def _extract_startup_name(self, user_message: str,
                            message_history: List[Dict[str, str]] = None) -> Optional[str]:
        """
        Tente d'extraire le nom d'une startup mentionnée dans le message

        Args:
            user_message: Message de l'utilisateur
            message_history: Historique des messages (optionnel)

        Returns:
            Nom de la startup ou None si non trouvé
        """
        # Liste de toutes les startups
        all_startups = self.get_startup_data()
        startup_names = [startup.get("name", "").lower() for startup in all_startups]

        # Recherche dans le message actuel
        for name in startup_names:
            if name and name in user_message.lower():
                return name

        # Si non trouvé et historique disponible, recherche dans le dernier message de l'assistant
        if message_history:
            for msg in reversed(message_history):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    for name in startup_names:
                        if name and name in content.lower():
                            return name
                    break

        return None

    def _find_startup_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Recherche une startup par son nom

        Args:
            name: Nom de la startup

        Returns:
            Données de la startup ou None si non trouvée
        """
        all_startups = self.get_startup_data()

        for startup in all_startups:
            if startup.get("name", "").lower() == name.lower():
                return startup

        return None

    def get_startup_details(self, startup_name: str, user_query: str = None) -> Dict[str, Any]:
        """
        Récupère les détails d'une startup spécifique

        Args:
            startup_name: Nom de la startup
            user_query: Requête de l'utilisateur (optionnel)

        Returns:
            Détails de la startup au format attendu par l'interface
        """
        startup = self._find_startup_by_name(startup_name)

        if not startup:
            return {"content": f"Je ne trouve pas de startup nommée '{startup_name}' dans ma base de données."}

        # Si aucune requête spécifique, générer une présentation générale
        if not user_query:
            user_query = f"Présente-moi la startup {startup_name}"

        # Construction d'un prompt pour Mistral
        prompt = f"""
        Vous êtes un expert des startups de La French Tech Réunion.
        
        Voici les informations sur la startup {startup_name}:
        
        Nom: {startup.get('name', 'Non spécifié')}
        
        Description: {startup.get('description', 'Non spécifiée')}
        
        Tags/Technologies: {', '.join(startup.get('tags', []))}
        
        Domaine d'activité: {startup.get('domain', 'Non spécifié')}
        
        Localisation: {startup.get('location', 'Non spécifiée')}
        
        Site web: {startup.get('url', 'Non spécifié')}
        
        Contact: {startup.get('contact', 'Non spécifié')}
        
        Requête de l'utilisateur: {user_query}
        
        Veuillez fournir une réponse détaillée et pertinente à la requête de l'utilisateur
        en vous basant sur les informations fournies sur cette startup.
        """

        messages = [
            {"role": "system", "content": "Vous êtes un expert des startups de La French Tech Réunion."},
            {"role": "user", "content": prompt}
        ]

        # Appel à Mistral
        response = call_mistral(messages)

        # Formatage de la réponse
        return {
            "content": response,
            "has_startups": True,
            "startups": [startup]
        }