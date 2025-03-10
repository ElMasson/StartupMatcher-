"""
Gestion des embeddings avec Mistral
"""
from mistralai import Mistral
import numpy as np
from typing import List, Dict, Any, Union
import os
import logging
from config import DOCLING_CONFIG

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration du client Mistral avec la nouvelle API
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def get_embedding_model() -> str:
    """
    Récupère le modèle d'embedding à utiliser

    Returns:
        Nom du modèle
    """
    return DOCLING_CONFIG["embedding_model"]

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Génère des embeddings pour une liste de textes avec Mistral

    Args:
        texts: Liste des textes

    Returns:
        Liste des embeddings
    """
    model = "mistral-embed"  # Modèle d'embedding Mistral
    logger.info(f"Génération d'embeddings avec le modèle {model} pour {len(texts)} textes...")

    try:
        # Traitement par lots de 10 textes pour éviter les timeout
        batch_size = 10
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]

            # Utilisation de la nouvelle API pour les embeddings
            response = client.embeddings.create(
                model=model,
                input=batch_texts
            )

            # Extraction des embeddings (vérifiez la structure de réponse exacte)
            batch_embeddings = [data.embedding for data in response.data]
            all_embeddings.extend(batch_embeddings)

            logger.info(f"Lot {i // batch_size + 1}: Génération d'embeddings réussie pour {len(batch_embeddings)} textes")

        logger.info(f"Génération d'embeddings terminée pour {len(all_embeddings)} textes au total")
        return all_embeddings

    except Exception as e:
        logger.error(f"Erreur lors de la génération d'embeddings avec Mistral: {e}")
        # Retourner une liste vide en cas d'erreur
        return []

def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calcule la similarité cosinus entre deux embeddings

    Args:
        embedding1: Premier embedding
        embedding2: Deuxième embedding

    Returns:
        Score de similarité cosinus
    """
    # Conversion en arrays numpy
    v1 = np.array(embedding1)
    v2 = np.array(embedding2)

    # Calcul de la similarité cosinus
    similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    return float(similarity)

def rank_documents_by_similarity(query_embedding: List[float],
                                doc_embeddings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classe des documents par similarité avec une requête

    Args:
        query_embedding: Embedding de la requête
        doc_embeddings: Liste des embeddings de documents avec métadonnées

    Returns:
        Documents classés par similarité décroissante
    """
    # Calcul des scores de similarité
    for doc in doc_embeddings:
        doc["similarity_score"] = cosine_similarity(query_embedding, doc["embedding"])

    # Tri par score décroissant
    sorted_docs = sorted(doc_embeddings, key=lambda x: x["similarity_score"], reverse=True)

    return sorted_docs