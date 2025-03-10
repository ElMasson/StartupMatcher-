"""
Gestion de la préparation des documents
"""
import logging
from typing import Dict, List, Any
from config import DOCLING_CONFIG
from rag.utils import convert_startups_to_documents
from rag.document_processor import DocumentProcessor, DocumentCollection, VectorIndex

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def configure_docling(config: Dict = None) -> DocumentProcessor:
    """
    Configure le processeur de documents

    Args:
        config: Configuration personnalisée (optionnel)

    Returns:
        Instance configurée du processeur
    """
    if config is None:
        config = DOCLING_CONFIG

    processor = DocumentProcessor(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        embedding_model=config["embedding_model"]
    )

    return processor

def process_startups_data(startups_data: List[Dict[str, Any]]) -> DocumentCollection:
    """
    Traite les données des startups

    Args:
        startups_data: Données des startups

    Returns:
        Collection de documents traités
    """
    # Conversion des données en documents
    documents = convert_startups_to_documents(startups_data)

    # Configuration du processeur
    processor = configure_docling()

    # Traitement des documents
    logger.info(f"Traitement de {len(documents)} documents...")
    doc_collection = processor.process_documents(documents)

    logger.info(f"Traitement terminé, {len(doc_collection.chunks)} chunks créés")
    return doc_collection

def create_vector_index(doc_collection: DocumentCollection) -> VectorIndex:
    """
    Crée un index vectoriel à partir d'une collection de documents

    Args:
        doc_collection: Collection de documents

    Returns:
        Index vectoriel
    """
    logger.info("Création de l'index vectoriel...")
    index = VectorIndex(doc_collection)
    logger.info("Index vectoriel créé")

    return index

def search_similar_documents(index: VectorIndex, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Recherche des documents similaires à une requête

    Args:
        index: Index vectoriel
        query: Requête de recherche
        top_k: Nombre de résultats à retourner

    Returns:
        Liste des documents similaires
    """
    logger.info(f"Recherche de documents similaires à '{query}'...")
    results = index.search(query, top_k=top_k)

    return results