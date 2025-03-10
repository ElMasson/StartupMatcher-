"""
Gestion des agents CrewAI
"""
import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from config import AGENT_CONFIG
from llm.mistral_handler import get_llm_config
from rag.retrieval import retrieve_startups_by_need, combine_startups_for_need
from agent.utils import extract_intent, parse_message_content, format_agent_response
from agent.utils import create_startup_summary

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration du LLM
llm_config = get_llm_config()


# Définition des outils pour les agents
@tool
def search_startups(query: str) -> str:
    """
    Recherche des startups qui correspondent à un besoin spécifique.

    Args:
        query: Description du besoin (ex: 'solutions de gestion des déchets')

    Returns:
        Liste des startups pertinentes au format JSON
    """
    logger.info(f"Recherche de startups pour: {query}")
    startups = retrieve_startups_by_need(query, top_k=5)

    if not startups:
        return "Aucune startup trouvée pour cette recherche."

    formatted_results = []
    for s in startups:
        formatted_results.append({
            "id": s.get("id", s.get("name", "")),
            "name": s.get("name", ""),
            "summary": create_startup_summary(s),
            "tags": s.get("tags", []),
            "domain": s.get("domain", ""),
            "location": s.get("location", "")
        })

    import json
    return json.dumps(formatted_results, ensure_ascii=False)


@tool
def find_startup_combinations(query: str) -> str:
    """
    Trouve des combinaisons de startups complémentaires pour un besoin complexe.

    Args:
        query: Description du besoin complexe

    Returns:
        Combinaisons de startups au format JSON
    """
    logger.info(f"Recherche de combinaisons de startups pour: {query}")
    combinations = combine_startups_for_need(query, top_k=3)

    if not combinations:
        return "Aucune combinaison pertinente trouvée."

    formatted_results = []
    for combo in combinations:
        startups = []
        for s in combo.get("startups", []):
            startups.append({
                "id": s.get("id", s.get("name", "")),
                "name": s.get("name", ""),
                "summary": create_startup_summary(s),
                "tags": s.get("tags", []),
                "domain": s.get("domain", "")
            })

        formatted_results.append({
            "reason": combo.get("reason", ""),
            "startups": startups
        })

    import json
    return json.dumps(formatted_results, ensure_ascii=False)


@tool
def analyze_user_need(request: str) -> str:
    """
    Analyse le besoin utilisateur pour extraire les informations clés.

    Args:
        request: Demande de l'utilisateur

    Returns:
        Analyse structurée du besoin au format JSON
    """
    logger.info(f"Analyse du besoin: {request}")
    # Extraction de l'intention
    intent = extract_intent(request)

    # Analyse du message pour extraire des filtres
    cleaned_message, filters = parse_message_content(request)

    analysis = {
        "intent": intent,
        "message": cleaned_message,
        "domains": [],
        "problems": [],
        "objectives": [],
        "keywords": []
    }

    if filters:
        analysis["filters"] = filters

    # Extraction des domaines, problèmes, objectifs et mots-clés
    # Remarque: dans un système complet, cela pourrait être fait par un LLM
    keywords = [word for word in cleaned_message.lower().split() if len(word) > 3]
    analysis["keywords"] = keywords[:5]  # Limiter à 5 mots-clés

    import json
    return json.dumps(analysis, ensure_ascii=False)


# Définition des agents
def create_need_analyst_agent() -> Agent:
    """
    Crée un agent analyste de besoins

    Returns:
        Agent CrewAI
    """
    return Agent(
        role="Analyste de besoins",
        goal="Analyser et comprendre précisément les besoins exprimés par les utilisateurs",
        backstory="""
        Vous êtes un expert en analyse de besoins avec une grande expérience dans le domaine 
        de l'innovation et des startups. Votre mission est de comprendre ce que recherchent 
        réellement les utilisateurs, même lorsque leurs demandes sont vagues ou imprécises.
        """,
        verbose=AGENT_CONFIG.get("verbose", True),
        allow_delegation=AGENT_CONFIG.get("allow_delegation", True),
        tools=[analyze_user_need]
    )


def create_startup_finder_agent() -> Agent:
    """
    Crée un agent de recherche de startups

    Returns:
        Agent CrewAI
    """
    return Agent(
        role="Expert en startups innovantes",
        goal="Trouver les startups qui correspondent le mieux aux besoins des utilisateurs",
        backstory="""
        Vous êtes un expert du monde des startups et de l'innovation. Vous connaissez parfaitement 
        l'écosystème des startups à La Réunion et vous savez identifier celles qui correspondent 
        le mieux à un besoin spécifique. Votre expertise vous permet de faire des recommandations 
        pertinentes et personnalisées.
        """,
        verbose=AGENT_CONFIG.get("verbose", True),
        allow_delegation=AGENT_CONFIG.get("allow_delegation", True),
        tools=[search_startups]
    )


def create_solution_architect_agent() -> Agent:
    """
    Crée un agent architecte de solutions

    Returns:
        Agent CrewAI
    """
    return Agent(
        role="Architecte de solutions innovantes",
        goal="Concevoir des solutions complètes en combinant les expertises de différentes startups",
        backstory="""
        Vous êtes un expert en ingénierie de solutions innovantes. Votre force est de comprendre 
        les problèmes complexes et de concevoir des solutions qui combinent les expertises de 
        différentes startups pour créer des synergies. Vous savez identifier les complémentarités 
        entre startups et proposer des combinaisons pertinentes.
        """,
        verbose=AGENT_CONFIG.get("verbose", True),
        allow_delegation=AGENT_CONFIG.get("allow_delegation", True),
        tools=[find_startup_combinations]
    )


def create_crew() -> Crew:
    """
    Crée l'équipe d'agents

    Returns:
        Équipe CrewAI
    """
    # Création des agents
    need_analyst = create_need_analyst_agent()
    startup_finder = create_startup_finder_agent()
    solution_architect = create_solution_architect_agent()

    # Création de l'équipe
    crew = Crew(
        agents=[need_analyst, startup_finder, solution_architect],
        tasks=[],  # Les tâches seront ajoutées dynamiquement
        verbose=AGENT_CONFIG.get("verbose", True),
        process=Process.sequential,  # Les tâches sont exécutées séquentiellement
    )

    return crew


def process_user_request(user_message: str, message_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Traite une requête utilisateur avec la crew d'agents

    Args:
        user_message: Message de l'utilisateur
        message_history: Historique des messages

    Returns:
        Réponse formatée
    """
    logger.info(f"Traitement de la requête: {user_message}")

    # Création des agents
    need_analyst = create_need_analyst_agent()
    startup_finder = create_startup_finder_agent()
    solution_architect = create_solution_architect_agent()

    # Tâche d'analyse du besoin
    analyze_task = Task(
        description=f"Analyser la requête suivante: {user_message}",
        expected_output="Une analyse détaillée du besoin exprimé par l'utilisateur",
        agent=need_analyst
    )

    # Exécution de la tâche d'analyse
    crew = Crew(
        agents=[need_analyst],
        tasks=[analyze_task],
        verbose=AGENT_CONFIG.get("verbose", True)
    )

    analysis_result = crew.kickoff()
    logger.info(f"Résultat de l'analyse: {analysis_result}")

    # Extraction de l'intention à partir de l'analyse
    import json
    try:
        analysis = json.loads(analysis_result)
        intent = analysis.get("intent", "search")
    except:
        intent = extract_intent(user_message)

    # Traitement selon l'intention identifiée
    if intent == "combine":
        # Recherche de combinaisons de startups
        combination_task = Task(
            description=f"Trouver des combinaisons de startups pour répondre au besoin suivant: {user_message}",
            expected_output="Des combinaisons pertinentes de startups avec explications",
            agent=solution_architect
        )

        crew = Crew(
            agents=[solution_architect],
            tasks=[combination_task],
            verbose=AGENT_CONFIG.get("verbose", True)
        )

        result = crew.kickoff()

        try:
            # Tentative de parser le résultat comme JSON
            combinations = json.loads(result)
            return format_agent_response(
                f"Voici les combinaisons de startups que je vous propose pour répondre à votre besoin :\n\n{result}",
                combinations
            )
        except:
            # Si ce n'est pas du JSON valide, on retourne le texte brut
            return format_agent_response(result)

    else:  # Par défaut, recherche de startups
        # Recherche de startups
        search_task = Task(
            description=f"Trouver les startups les plus pertinentes pour le besoin suivant: {user_message}",
            expected_output="Une liste des startups les plus adaptées avec explications",
            agent=startup_finder
        )

        crew = Crew(
            agents=[startup_finder],
            tasks=[search_task],
            verbose=AGENT_CONFIG.get("verbose", True)
        )

        result = crew.kickoff()

        try:
            # Tentative de parser le résultat comme JSON
            startups = json.loads(result)
            return format_agent_response(
                f"Voici les startups qui correspondent à votre besoin :\n\n{result}",
                startups
            )
        except:
            # Si ce n'est pas du JSON valide, on retourne le texte brut
            return format_agent_response(result)