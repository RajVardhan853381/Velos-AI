"""
Velos - Resume Vector Store
Implements RAG (Retrieval Augmented Generation) for contextual memory.

Uses ChromaDB for vector storage and sentence-transformers for embeddings.
This allows agents to query specific parts of resumes without hallucination.

Built for ZYND AIckathon 2025
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any

# Vector Database
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ chromadb not installed. Vector store disabled.")

# Embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Embeddings disabled.")

# Text Splitting
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    SPLITTER_AVAILABLE = True
except ImportError:
    SPLITTER_AVAILABLE = False
    print("⚠️ langchain-text-splitters not installed. Using basic splitting.")


class ResumeVectorStore:
    """
    Vector database for storing and retrieving resume chunks.
    
    Implements RAG pattern:
    1. Chunk resume into small pieces (500 chars, 50 overlap)
    2. Convert chunks to embeddings using sentence-transformers
    3. Store in ChromaDB with candidate_id metadata
    4. Retrieve relevant chunks based on semantic similarity
    """
    
    # Configuration
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, CPU-friendly model
    COLLECTION_NAME = "candidate_resumes"
    TOP_K_RESULTS = 3
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data.
                              Defaults to ./chroma_db in project root.
        """
        self.is_available = CHROMA_AVAILABLE and EMBEDDINGS_AVAILABLE
        
        if not self.is_available:
            print("⚠️ Vector store not fully available. Some features disabled.")
            self.client = None
            self.collection = None
            self.embedding_model = None
            self.text_splitter = None
            return
        
        # Set up persistence directory
        if persist_directory is None:
            persist_directory = str(Path(__file__).parent.parent / "chroma_db")
        
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Disable ChromaDB telemetry completely (prevents hang on init)
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_TELEMETRY"] = "False"
        
        # Initialize ChromaDB client with persistence
        print(f"📦 Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "TrustFlow candidate resume chunks"}
        )
        print(f"✅ ChromaDB collection '{self.COLLECTION_NAME}' ready")
        
        # Load embedding model
        print(f"🧠 Loading embedding model: {self.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(self.EMBEDDING_MODEL)
        print("✅ Embedding model loaded")
        
        # Initialize text splitter
        if SPLITTER_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=self.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", ". ", ", ", " ", ""]
            )
        else:
            self.text_splitter = None
    
    def _generate_chunk_id(self, candidate_id: str, chunk_index: int, chunk_text: str) -> str:
        """Generate a unique ID for each chunk."""
        content_hash = hashlib.sha256(chunk_text.encode()).hexdigest()[:8]
        return f"{candidate_id}_chunk_{chunk_index}_{content_hash}"
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks using RecursiveCharacterTextSplitter.
        Falls back to basic splitting if langchain not available.
        """
        if self.text_splitter:
            return self.text_splitter.split_text(text)
        else:
            # Basic fallback: split by paragraphs, then by size
            chunks = []
            paragraphs = text.split("\n\n")
            
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < self.CHUNK_SIZE:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks if chunks else [text]
    
    def add_resume(self, candidate_id: str, resume_text: str) -> Dict[str, Any]:
        """
        Add a resume to the vector store.
        
        Chunks the resume, generates embeddings, and stores with metadata.
        
        Args:
            candidate_id: Unique identifier for the candidate
            resume_text: Full resume text
            
        Returns:
            Dict with storage statistics
        """
        if not self.is_available:
            return {"success": False, "error": "Vector store not available"}
        
        if not resume_text or len(resume_text.strip()) < 10:
            return {"success": False, "error": "Resume text too short"}
        
        # First, remove any existing chunks for this candidate (update scenario)
        self.delete_candidate(candidate_id)
        
        # Split resume into chunks
        chunks = self._split_text(resume_text)
        
        if not chunks:
            return {"success": False, "error": "No chunks generated"}
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(candidate_id, i, chunk)
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "candidate_id": candidate_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "char_count": len(chunk)
            })
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return {
            "success": True,
            "candidate_id": candidate_id,
            "chunks_stored": len(chunks),
            "total_characters": len(resume_text),
            "avg_chunk_size": sum(len(c) for c in chunks) // len(chunks)
        }
    
    def get_context(self, query: str, candidate_id: str, 
                    n_results: int = None) -> str:
        """
        Retrieve relevant resume chunks for a specific query and candidate.
        
        This is the core RAG retrieval function that agents use to get
        context without loading the entire resume.
        
        Args:
            query: The question or topic to search for
            candidate_id: The candidate to search within (security filter)
            n_results: Number of chunks to return (default: TOP_K_RESULTS)
            
        Returns:
            Combined text of the most relevant chunks
        """
        if not self.is_available:
            return ""
        
        if n_results is None:
            n_results = self.TOP_K_RESULTS
        
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Query with candidate_id filter for security
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"candidate_id": candidate_id},
            include=["documents", "metadatas", "distances"]
        )
        
        # Extract and combine documents
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            # Join with double newline for readability
            return "\n\n".join(documents)
        
        return ""
    
    def get_context_with_scores(self, query: str, candidate_id: str,
                                 n_results: int = None) -> List[Dict]:
        """
        Retrieve relevant chunks with similarity scores.
        
        Returns detailed information about each retrieved chunk.
        """
        if not self.is_available:
            return []
        
        if n_results is None:
            n_results = self.TOP_K_RESULTS
        
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"candidate_id": candidate_id},
            include=["documents", "metadatas", "distances"]
        )
        
        chunks_with_scores = []
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                chunks_with_scores.append({
                    "text": doc,
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {}
                })
        
        return chunks_with_scores
    
    def delete_candidate(self, candidate_id: str) -> bool:
        """
        Delete all chunks for a specific candidate.
        
        Args:
            candidate_id: The candidate to remove
            
        Returns:
            True if deletion was successful
        """
        if not self.is_available:
            return False
        
        try:
            # Get all chunk IDs for this candidate
            results = self.collection.get(
                where={"candidate_id": candidate_id},
                include=[]
            )
            
            if results and results.get("ids"):
                self.collection.delete(ids=results["ids"])
                return True
            return True  # Nothing to delete is still success
            
        except Exception as e:
            print(f"Error deleting candidate {candidate_id}: {e}")
            return False
    
    def get_candidate_chunks(self, candidate_id: str) -> List[str]:
        """
        Get all stored chunks for a candidate.
        
        Useful for debugging or reviewing stored data.
        """
        if not self.is_available:
            return []
        
        results = self.collection.get(
            where={"candidate_id": candidate_id},
            include=["documents", "metadatas"]
        )
        
        if results and results.get("documents"):
            # Sort by chunk_index
            chunks_with_meta = list(zip(
                results["documents"],
                results["metadatas"]
            ))
            chunks_with_meta.sort(key=lambda x: x[1].get("chunk_index", 0))
            return [c[0] for c in chunks_with_meta]
        
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.is_available:
            return {"available": False}
        
        try:
            count = self.collection.count()
            return {
                "available": True,
                "collection_name": self.COLLECTION_NAME,
                "total_chunks": count,
                "embedding_model": self.EMBEDDING_MODEL,
                "chunk_size": self.CHUNK_SIZE,
                "chunk_overlap": self.CHUNK_OVERLAP,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {"available": True, "error": str(e)}
    
    def search_all(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search across ALL candidates (for admin/debug purposes only).
        
        WARNING: This bypasses the candidate_id security filter.
        Only use for debugging or admin dashboards.
        """
        if not self.is_available:
            return []
        
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        all_results = []
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                all_results.append({
                    "text": doc[:200] + "..." if len(doc) > 200 else doc,
                    "candidate_id": results["metadatas"][0][i].get("candidate_id"),
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })
        
        return all_results
    
    def clear_all(self) -> bool:
        """
        Clear all data from the vector store.
        
        WARNING: This deletes everything. Use with caution.
        """
        if not self.is_available:
            return False
        
        try:
            # Delete and recreate collection
            self.client.delete_collection(self.COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=self.COLLECTION_NAME,
                metadata={"description": "Velos candidate resume chunks"}
            )
            return True
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            return False


# Singleton instance for easy import
_vector_store_instance: Optional[ResumeVectorStore] = None

def get_vector_store() -> ResumeVectorStore:
    """Get or create the singleton vector store instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ResumeVectorStore()
    return _vector_store_instance


# Quick test
if __name__ == "__main__":
    print("🧪 Testing ResumeVectorStore...")
    
    store = ResumeVectorStore()
    print(f"\n📊 Stats: {store.get_stats()}")
    
    # Test with sample resume
    test_resume = """
    John Smith
    Senior Software Engineer
    
    EXPERIENCE:
    I have 5 years of experience in Python and built a Django app for e-commerce.
    Led a team of 4 developers to create a microservices architecture.
    Implemented machine learning models using TensorFlow and PyTorch.
    
    SKILLS:
    - Python, JavaScript, Go
    - Django, FastAPI, React
    - TensorFlow, PyTorch, scikit-learn
    - AWS, Docker, Kubernetes
    
    EDUCATION:
    MS Computer Science, Stanford University, 2018
    """
    
    # Add resume
    result = store.add_resume("test_user_1", test_resume)
    print(f"\n📝 Add result: {result}")
    
    # Search for Django
    context = store.get_context("Django experience", "test_user_1")
    print(f"\n🔍 Search 'Django' for test_user_1:")
    print(f"   Found: {context[:200]}..." if context else "   No results")
    
    # Search for wrong user (should return nothing)
    context_wrong = store.get_context("Django", "wrong_user")
    print(f"\n🔒 Search 'Django' for wrong_user:")
    print(f"   Found: {context_wrong}" if context_wrong else "   No results (correct - security working!)")
    
    print("\n✅ Vector store test complete!")
