"""
Fonction de récupération des documents pertinents
"""
import logging
from typing import Dict, List, Any, Union
from rag.document_processor import VectorIndex
from rag.docling_handler import search_similar_documents
from rag.utils import filter_documents_by_query, get_latest_vector_store, load_vector_store
from rag.embedding import generate_embeddings, rank_documents_by_similarity
from crawler.startup_crawler import get_startup_data

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_vector_index() -> Union[VectorIndex, None]:
    """
    Récupère l'index vectoriel le plus récent

    Returns:
        Index vectoriel ou None si aucun index n'existe
    """
    latest_vector_store = get_latest_vector_store()
    if latest_vector_store is None:
        return None

    return load_vector_store(latest_vector_store)

def retrieve_documents(query: str, filters: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Récupère les documents pertinents pour une requête

    Args:
        query: Requête de recherche
        filters: Filtres à appliquer (optionnel)
        top_k: Nombre de résultats à retourner

    Returns:
        Liste des documents pertinents
    """
    # Récupération de l'index vectoriel
    index = get_vector_index()

    # Si l'index n'existe pas, on retourne une liste vide
    if index is None:
        logger.warning("Aucun index vectoriel trouvé")
        return []

    # Recherche de documents similaires
    similar_docs = search_similar_documents(index, query, top_k=top_k*2)  # On récupère plus de documents pour pouvoir filtrer

    # Application des filtres si nécessaire
    if filters:
        similar_docs = filter_documents_by_query(similar_docs, filters)

    # Limitation du nombre de résultats
    return similar_docs[:top_k]

def retrieve_startups_by_need(user_need: str, filters: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Récupère les startups pertinentes pour un besoin utilisateur

    Args:
        user_need: Description du besoin utilisateur
        filters: Filtres à appliquer (optionnel)
        top_k: Nombre de startups à retourner

    Returns:
        Liste des startups pertinentes
    """
    # Pour simplifier et éviter les problèmes avec docling/VectorIndex,
    # on utilise ici une approche plus directe
    all_startups = get_startup_data()

    # Si aucun besoin n'est spécifié, retourner simplement les X premières startups
    if not user_need:
        return all_startups[:top_k]

    # Création d'une recherche simple par mots-clés
    keywords = user_need.lower().split()

    # Calcul des scores pour chaque startup
    scored_startups = []
    for startup in all_startups:
        score = 0

        # Recherche dans le nom (plus de poids)
        name = startup.get("name", "").lower()
        for keyword in keywords:
            if keyword in name:
                score += 3

        # Recherche dans la description
        description = startup.get("description", "").lower()
        for keyword in keywords:
            if keyword in description:
                score += 2

        # Recherche dans les tags
        tags = [tag.lower() for tag in startup.get("tags", [])]
        for keyword in keywords:
            for tag in tags:
                if keyword in tag:
                    score += 2

        # Recherche dans le domaine
        domain = startup.get("domain", "").lower()
        for keyword in keywords:
            if keyword in domain:
                score += 1

        # Ajout de la startup avec son score
        scored_startups.append((startup, score))

    # Tri par score décroissant
    sorted_startups = sorted(scored_startups, key=lambda x: x[1], reverse=True)

    # Récupération des startups avec le meilleur score
    filtered_startups = [startup for startup, score in sorted_startups if score > 0]

    # Si aucune startup trouvée, retourner quelques startups aléatoires
    if not filtered_startups:
        import random
        random.shuffle(all_startups)
        return all_startups[:top_k]

    # Application des filtres supplémentaires si nécessaire
    if filters:
        if "tags" in filters and filters["tags"]:
            filtered_startups = [
                startup for startup in filtered_startups
                if any(tag in startup.get("tags", []) for tag in filters["tags"])
            ]

        if "domain" in filters and filters["domain"]:
            filtered_startups = [
                startup for startup in filtered_startups
                if filters["domain"] == startup.get("domain", "")
            ]

        if "location" in filters and filters["location"]:
            filtered_startups = [
                startup for startup in filtered_startups
                if filters["location"] == startup.get("location", "")
            ]

    # Limitation du nombre de résultats
    return filtered_startups[:top_k]

def combine_startups_for_need(user_need: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Propose des combinaisons de startups pour répondre à un besoin complexe

    Args:
        user_need: Description du besoin utilisateur
        top_k: Nombre de combinaisons à proposer

    Returns:
        Liste des combinaisons proposées
    """
    # Récupération d'un ensemble plus large de startups pertinentes
    relevant_startups = retrieve_startups_by_need(user_need, top_k=10)

    # Pour l'instant, une implémentation simple qui propose des paires de startups
    # Dans une version plus avancée, on pourrait utiliser un LLM pour créer des combinaisons plus pertinentes
    combinations = []

    for i in range(min(len(relevant_startups), 4)):
        for j in range(i + 1, min(len(relevant_startups), 5)):
            startup1 = relevant_startups[i]
            startup2 = relevant_startups[j]

            # Vérification de la complémentarité (domaines différents)
            domain1 = startup1.get('domain', '')
            domain2 = startup2.get('domain', '')

            if domain1 != domain2:
                combination = {
                    "startups": [startup1, startup2],
                    "reason": f"Combinaison de '{startup1.get('name', '')}' ({domain1}) et '{startup2.get('name', '')}' ({domain2}) pour répondre au besoin: {user_need[:100]}..."
                }

                combinations.append(combination)

    # Limitation du nombre de résultats
    return combinations[:top_k]