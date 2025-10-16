"""RAG (Retrieval-Augmented Generation) system for PrajwalGPT."""

import json
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx

from shared import get_settings


class RAGRetriever:
    """Handles document retrieval and context preparation."""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_store_path = Path(self.settings.vector_store_path)
        self.index_path = self.vector_store_path / "faiss_index.bin"
        self.metadata_path = self.vector_store_path / "metadata.json"
        
        self._index = None
        self._metadata = None
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load FAISS index and metadata."""
        try:
            print(f"Looking for vector store at: {self.vector_store_path}")
            print(f"Index path: {self.index_path}")
            print(f"Metadata path: {self.metadata_path}")
            print(f"Index exists: {self.index_path.exists()}")
            print(f"Metadata exists: {self.metadata_path.exists()}")
            
            if self.index_path.exists() and self.metadata_path.exists():
                self._index = faiss.read_index(str(self.index_path))
                
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self._metadata = json.load(f)
                
                print(f"✅ Loaded vector store with {len(self._metadata)} chunks")
            else:
                print("⚠️ Vector store not found. Run ingestion first.")
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            import traceback
            traceback.print_exc()
    
    async def get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for search query."""
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.settings.ollama_host}/api/embeddings",
                json={
                    "model": self.settings.embedding_model,
                    "prompt": query
                }
            )
            response.raise_for_status()
            return response.json()["embedding"]
    
    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query."""
        if not self._index or not self._metadata:
            return []
        
        try:
            print(f"🔍 Searching for: {query}")
            
            # Get query embedding
            query_embedding = await self.get_query_embedding(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS index
            scores, indices = self._index.search(query_vector, top_k)
            
            # Retrieve relevant chunks
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self._metadata) and idx != -1:  # -1 indicates no more results
                    chunk_data = self._metadata[idx].copy()
                    chunk_data['similarity_score'] = float(score)
                    results.append(chunk_data)
            
            print(f"✅ Found {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def is_available(self) -> bool:
        """Check if RAG system is ready."""
        return self._index is not None and self._metadata is not None
    
    async def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query."""
        if not self.is_available():
            return ""
        
        results = await self.search_documents(query, top_k=5)
        
        if not results:
            return ""
        
        # Build context from top results
        context_parts = []
        current_length = 0
        
        for result in results:
            content = result['content']
            file_name = result['file']
            
            chunk_text = f"From {file_name}:\n{content}\n"
            
            if current_length + len(chunk_text) > max_context_length:
                break
                
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)


# Global RAG retriever instance
rag_retriever = RAGRetriever()