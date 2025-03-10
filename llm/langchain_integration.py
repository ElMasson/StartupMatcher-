"""
Intégration de LangChain avec Mistral pour CrewAI
"""
import os
import logging
from typing import Dict, Any
from langchain.llms import Mistral as LangChainMistralLLM
from langchain.chat_models import ChatMistralAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from config import LLM_CONFIG, AGENT_CONFIG

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_mistral_llm():
    """
    Initialise et retourne une instance du modèle Mistral via LangChain

    Returns:
        Instance LangChain du modèle Mistral
    """
    model_name = LLM_CONFIG.get("model", "mistral-large-latest")
    temperature = LLM_CONFIG.get("temperature", 0.2)

    try:
        # Mise à jour pour utiliser la nouvelle version de l'API Mistral
        llm = ChatMistralAI(
            model=model_name,
            temperature=temperature,
            mistral_api_key=os.getenv("MISTRAL_API_KEY")
        )
        return llm
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du modèle Mistral: {e}")
        raise

def create_langchain_agent(tools, system_prompt=None):
    """
    Crée un agent LangChain avec le modèle Mistral

    Args:
        tools: Outils à mettre à disposition de l'agent
        system_prompt: Prompt système personnalisé (optionnel)

    Returns:
        Agent LangChain configuré
    """
    llm = get_mistral_llm()

    if not system_prompt:
        system_prompt = AGENT_CONFIG.get("system_prompt", "")

    # Création du prompt
    prompt = PromptTemplate.from_template(
        system_prompt + """
        
        Vous avez accès aux outils suivants:
        {tools}
        
        Pour utiliser un outil, veuillez utiliser le format suivant:
        ```
        Action: nom_de_l_outil
        Action Input: input_de_l_outil
        Observation: résultat_de_l_outil
        ```
        
        Question de l'utilisateur: {input}
        
        {agent_scratchpad}
        """
    )

    # Création de l'agent
    agent = create_react_agent(llm, tools, prompt)

    # Création de la mémoire
    memory = ConversationBufferMemory(return_messages=True)

    # Création de l'exécuteur d'agent
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=AGENT_CONFIG.get("verbose", True),
        handle_parsing_errors=True
    )

    return agent_executor