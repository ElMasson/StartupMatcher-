"""
Fonctions utilitaires pour le RAG
"""
import os
from typing import Dict, List, Any, Union
import json
import pickle
from datetime import datetime


def save_vector_store(vector_store: Any, filename: str = None) -> str:
    """
    Sauvegarde le vector store

    Args:
        vector_store: Vector store à sauvegarder
        filename: Nom du fichier (optionnel)

    Returns:
        Chemin du fichier sauvegardé
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vector_store_{timestamp}.pkl"

    # Création du dossier vector_store s'il n'existe pas
    os.makedirs("vector_store", exist_ok=True)
    filepath = os.path.join("vector_store", filename)

    with open(filepath, "wb") as f:
        pickle.dump(vector_store, f)

    return filepath


def load_vector_store(filepath: str) -> Any:
    """
    Charge un vector store depuis un fichier

    Args:
        filepath: Chemin du fichier à charger

    Returns:
        Vector store chargé
    """
    if not os.path.exists(filepath):
        return None

    with open(filepath, "rb") as f:
        return pickle.load(f)


def get_latest_vector_store() -> Union[str, None]:
    """
    Récupère le vector store le plus récent

    Returns:
        Chemin du fichier ou None si aucun fichier n'existe
    """
    vector_store_dir = "vector_store"
    if not os.path.exists(vector_store_dir):
        return None

    vector_store_files = [f for f in os.listdir(vector_store_dir) if
                          f.startswith("vector_store_") and f.endswith(".pkl")]
    if not vector_store_files:
        return None

    # Tri par date de création
    vector_store_files.sort(key=lambda x: os.path.getctime(os.path.join(vector_store_dir, x)), reverse=True)
    return os.path.join(vector_store_dir, vector_store_files[0])


def convert_startups_to_documents(startups_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convertit les données des startups en documents pour le RAG

    Args:
        startups_data: Données des startups

    Returns:
        Liste des documents
    """
    documents = []

    for startup in startups_data:
        # Création du contenu textuel
        content = f"""
        Nom: {startup.get('name', 'Non spécifié')}

        Description: {startup.get('description', 'Non spécifiée')}

        Tags: {', '.join(startup.get('tags', []))}

        URL: {startup.get('url', 'Non spécifiée')}

        Contact: {startup.get('contact', 'Non spécifié')}

        Domaine d'activité: {startup.get('domain', 'Non spécifié')}

        Localisation: {startup.get('location', 'Non spécifiée')}
        """

        # Création du document
        document = {
            "content": content,
            "metadata": {
                "source": "startup_crawl",
                "startup_id": startup.get("id", startup.get("name", "")),
                "startup_name": startup.get("name", ""),
                "tags": startup.get("tags", []),
                "domain": startup.get("domain", ""),
                "location": startup.get("location", "")
            }
        }

        documents.append(document)

    return documents


def filter_documents_by_query(documents: List[Dict[str, Any]], query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filtre les documents selon des critères de recherche

    Args:
        documents: Liste des documents
        query: Critères de recherche

    Returns:
        Documents filtrés
    """
    filtered_docs = documents

    # Filtrage par tags
    if "tags" in query and query["tags"]:
        filtered_docs = [
            doc for doc in filtered_docs
            if any(tag in doc["metadata"].get("tags", []) for tag in query["tags"])
        ]

    # Filtrage par domaine
    if "domain" in query and query["domain"]:
        filtered_docs = [
            doc for doc in filtered_docs
            if query["domain"] == doc["metadata"].get("domain", "")
        ]

    # Filtrage par localisation
    if "location" in query and query["location"]:
        filtered_docs = [
            doc for doc in filtered_docs
            if query["location"] == doc["metadata"].get("location", "")
        ]

    return filtered_docs