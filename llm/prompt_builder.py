"""
Construction des prompts pour le LLM
"""
from typing import Dict, List, Any
from config import AGENT_CONFIG
from llm.utils import format_message_history, format_startups_list_for_llm


def build_system_prompt() -> str:
    """
    Construit le prompt système pour le LLM

    Returns:
        Prompt système
    """
    return AGENT_CONFIG["system_prompt"]


def build_need_analysis_prompt(user_query: str, message_history: List[Dict[str, str]] = None) -> str:
    """
    Construit un prompt pour l'analyse des besoins

    Args:
        user_query: Requête de l'utilisateur
        message_history: Historique des messages (optionnel)

    Returns:
        Prompt pour l'analyse des besoins
    """
    prompt = """
Vous êtes un expert en analyse de besoins d'innovation pour les grands groupes et collectivités.
Votre mission est d'analyser les besoins exprimés par l'utilisateur et de les structurer selon les critères suivants:

1. Domaines technologiques concernés
2. Problématiques principales à résoudre
3. Objectifs visés
4. Contraintes à respecter
5. Mots-clés pertinents pour la recherche

Veuillez fournir une réponse structurée au format JSON suivant:
```json
{
    "domains": ["domaine1", "domaine2", ...],
    "problems": ["problème1", "problème2", ...],
    "objectives": ["objectif1", "objectif2", ...],
    "constraints": ["contrainte1", "contrainte2", ...],
    "keywords": ["mot-clé1", "mot-clé2", ...]
}
```

Assurez-vous que chaque élément est pertinent et clairement défini.
"""

    # Ajout de l'historique des messages si disponible
    if message_history:
        formatted_history = format_message_history(message_history)
        prompt += f"\n\nHistorique de la conversation:\n{formatted_history}"

    # Ajout de la requête utilisateur
    prompt += f"\n\nRequête de l'utilisateur: {user_query}"

    return prompt


def build_startup_matcher_prompt(user_need: str, analyzed_need: Dict[str, Any], startups: List[Dict[str, Any]]) -> str:
    """
    Construit un prompt pour la mise en relation avec des startups

    Args:
        user_need: Besoin exprimé par l'utilisateur
        analyzed_need: Besoin analysé (structure)
        startups: Liste des startups pertinentes

    Returns:
        Prompt pour la mise en relation
    """
    prompt = """
Vous êtes un expert en mise en relation entre des besoins d'innovation et des startups.
Votre mission est d'analyser les startups proposées et de déterminer lesquelles correspondent le mieux au besoin exprimé.

Pour chaque startup, veuillez évaluer:
1. Sa pertinence par rapport au besoin (score de 1 à 10)
2. Les forces qui la rendent adaptée au besoin
3. Les limitations potentielles à considérer
4. Des recommandations pour une collaboration efficace

Veuillez fournir une réponse détaillée et structurée à l'utilisateur, en:
- Résumant d'abord sa demande et les critères principaux identifiés
- Présentant les startups pertinentes par ordre de pertinence décroissante
- Expliquant pourquoi chaque startup répond à ses besoins
- Proposant des conseils pour entrer en contact avec ces startups

Votre réponse doit être informative, précise et orientée vers l'action.
"""

    # Ajout du besoin utilisateur
    prompt += f"\n\nBesoin exprimé par l'utilisateur: {user_need}"

    # Ajout de l'analyse du besoin
    prompt += "\n\nAnalyse structurée du besoin:"
    prompt += f"\n- Domaines technologiques: {', '.join(analyzed_need.get('domains', []))}"
    prompt += f"\n- Problématiques: {', '.join(analyzed_need.get('problems', []))}"
    prompt += f"\n- Objectifs: {', '.join(analyzed_need.get('objectives', []))}"
    prompt += f"\n- Contraintes: {', '.join(analyzed_need.get('constraints', []))}"
    prompt += f"\n- Mots-clés: {', '.join(analyzed_need.get('keywords', []))}"

    # Ajout des startups pertinentes
    prompt += "\n\n" + format_startups_list_for_llm(startups)

    return prompt


def build_combination_prompt(user_need: str, analyzed_need: Dict[str, Any], combinations: List[Dict[str, Any]]) -> str:
    """
    Construit un prompt pour proposer des combinaisons de startups

    Args:
        user_need: Besoin exprimé par l'utilisateur
        analyzed_need: Besoin analysé (structure)
        combinations: Liste des combinaisons de startups

    Returns:
        Prompt pour les combinaisons
    """
    prompt = """
Vous êtes un expert en écosystèmes d'innovation et en synergies entre startups.
Votre mission est d'analyser les combinaisons de startups proposées et d'expliquer comment elles pourraient collaborer pour répondre au besoin exprimé.

Pour chaque combinaison, veuillez:
1. Expliquer la complémentarité entre les startups
2. Décrire comment leurs expertises se combinent pour répondre au besoin
3. Proposer un modèle de collaboration potentiel
4. Identifier les avantages de cette approche combinée

Veuillez fournir une réponse détaillée et structurée à l'utilisateur, en:
- Résumant d'abord sa demande et pourquoi une approche combinée est pertinente
- Présentant les combinaisons les plus prometteuses
- Expliquant comment chaque combinaison répond à l'ensemble du besoin
- Proposant des conseils pour mettre en place ces collaborations

Votre réponse doit mettre en valeur la valeur ajoutée de la combinaison par rapport à une solution unique.
"""

    # Ajout du besoin utilisateur
    prompt += f"\n\nBesoin exprimé par l'utilisateur: {user_need}"

    # Ajout de l'analyse du besoin
    prompt += "\n\nAnalyse structurée du besoin:"
    prompt += f"\n- Domaines technologiques: {', '.join(analyzed_need.get('domains', []))}"
    prompt += f"\n- Problématiques: {', '.join(analyzed_need.get('problems', []))}"
    prompt += f"\n- Objectifs: {', '.join(analyzed_need.get('objectives', []))}"
    prompt += f"\n- Contraintes: {', '.join(analyzed_need.get('constraints', []))}"
    prompt += f"\n- Mots-clés: {', '.join(analyzed_need.get('keywords', []))}"

    # Ajout des combinaisons de startups
    prompt += "\n\nCombinations de startups proposées:\n\n"

    for i, combo in enumerate(combinations, 1):
        prompt += f"## Combinaison {i}:\n\n"

        # Startups dans la combinaison
        startups = combo.get("startups", [])
        prompt += format_startups_list_for_llm(startups)

        # Raison de la combinaison
        if "reason" in combo:
            prompt += f"\nRaison de cette combinaison: {combo['reason']}\n\n"

        prompt += "-" * 50 + "\n\n"

    return prompt