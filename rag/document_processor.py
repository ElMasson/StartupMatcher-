"""
Implémentation personnalisée d'un processeur de documents
Remplace la dépendance à docling qui n'existe pas
"""
import logging
from typing import Dict, List, Any, Optional
import re
from rag.embedding import generate_embeddings

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentCollection:
    """
    Collection de documents avec leurs chunks et métadonnées
    """

    def __init__(self):
        self.documents = []
        self.chunks = []
        self.metadata = {}

    def add_document(self, document: Dict[str, Any]):
        """
        Ajoute un document à la collection

        Args:
            document: Document à ajouter
        """
        self.documents.append(document)

    def add_chunk(self, chunk: Dict[str, Any]):
        """
        Ajoute un chunk à la collection

        Args:
            chunk: Chunk à ajouter
        """
        self.chunks.append(chunk)


class VectorIndex:
    """
    Index vectoriel pour la recherche sémantique
    """

    def __init__(self, doc_collection: DocumentCollection):
        """
        Initialisation de l'index vectoriel

        Args:
            doc_collection: Collection de documents
        """
        self.doc_collection = doc_collection
        self.embeddings = []

        # Génération des embeddings pour tous les chunks
        self._generate_embeddings()

    def _generate_embeddings(self):
        """
        Génère des embeddings pour tous les chunks
        """
        texts = [chunk["content"] for chunk in self.doc_collection.chunks]
        if not texts:
            return

        raw_embeddings = generate_embeddings(texts)

        # Association des embeddings aux chunks
        for i, embedding in enumerate(raw_embeddings):
            if i < len(self.doc_collection.chunks):
                self.embeddings.append({
                    "chunk_id": i,
                    "embedding": embedding,
                    "metadata": self.doc_collection.chunks[i]["metadata"]
                })

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche les chunks les plus similaires à une requête

        Args:
            query: Requête de recherche
            top_k: Nombre de résultats à retourner

        Returns:
            Liste des chunks les plus similaires
        """
        from rag.embedding import generate_embeddings, rank_documents_by_similarity

        # Génération de l'embedding pour la requête
        query_embeddings = generate_embeddings([query])
        if not query_embeddings:
            return []

        query_embedding = query_embeddings[0]

        # Classement des documents par similarité
        ranked_results = rank_documents_by_similarity(query_embedding, self.embeddings)

        # Récupération des top_k résultats
        top_results = ranked_results[:top_k]

        # Formatage des résultats
        formatted_results = []
        for result in top_results:
            chunk_id = result["chunk_id"]
            if chunk_id < len(self.doc_collection.chunks):
                chunk = self.doc_collection.chunks[chunk_id]
                formatted_results.append({
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "similarity_score": result["similarity_score"]
                })

        return formatted_results


class DocumentProcessor:
    """
    Processeur de documents pour le RAG
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, embedding_model: str = None):
        """
        Initialisation du processeur de documents

        Args:
            chunk_size: Taille des chunks en caractères
            chunk_overlap: Chevauchement entre chunks en caractères
            embedding_model: Modèle d'embedding à utiliser
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model

    def process_documents(self, documents: List[Dict[str, Any]]) -> DocumentCollection:
        """
        Traite une liste de documents

        Args:
            documents: Liste des documents à traiter

        Returns:
            Collection de documents traités
        """
        doc_collection = DocumentCollection()

        for doc in documents:
            # Ajout du document à la collection
            doc_collection.add_document(doc)

            # Chunking du document
            chunks = self._chunk_document(doc)

            # Ajout des chunks à la collection
            for chunk in chunks:
                doc_collection.add_chunk(chunk)

        return doc_collection

    def _chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Découpe un document en chunks

        Args:
            document: Document à découper

        Returns:
            Liste des chunks
        """
        content = document["content"]
        metadata = document.get("metadata", {})

        # Division en paragraphes
        paragraphs = re.split(r'\n\s*\n', content)

        # Création des chunks
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # Si le paragraphe est trop grand, le découper
            if len(paragraph) > self.chunk_size:
                # Découpage en phrases
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)

                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= self.chunk_size:
                        current_chunk += sentence + " "
                    else:
                        # Créer un nouveau chunk avec le contenu actuel
                        if current_chunk:
                            chunks.append({
                                "content": current_chunk.strip(),
                                "metadata": metadata
                            })

                        # Commencer un nouveau chunk avec la phrase actuelle
                        current_chunk = sentence + " "

            # Si le paragraphe entier peut être ajouté au chunk actuel
            elif len(current_chunk) + len(paragraph) <= self.chunk_size:
                current_chunk += paragraph + "\n\n"

            # Sinon, créer un nouveau chunk
            else:
                # Créer un nouveau chunk avec le contenu actuel
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": metadata
                    })

                # Commencer un nouveau chunk avec le paragraphe actuel
                current_chunk = paragraph + "\n\n"

        # Ajouter le dernier chunk s'il n'est pas vide
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": metadata
            })

        return chunks