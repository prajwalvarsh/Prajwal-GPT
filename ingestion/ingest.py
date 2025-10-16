"""Bootstrap script for ingesting knowledge sources into the vector store."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Iterable, List, Dict, Any
import httpx
import faiss
import numpy as np

from shared import get_settings


class DocumentProcessor:
    """Handles document processing and vector storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_store_path = Path(self.settings.vector_store_path)
        self.documents_path = Path("storage/documents")
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings from Ollama embedding model."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.settings.ollama_host}/api/embeddings",
                json={
                    "model": self.settings.embedding_model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()["embedding"]
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:break_point + 1]
                    end = break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
        return [chunk for chunk in chunks if chunk]
    
    def load_document(self, file_path: Path) -> str:
        """Load document content based on file type."""
        try:
            if file_path.suffix.lower() == '.pdf':
                # For PDF support, you'd need PyPDF2 or similar
                # For now, just return a placeholder
                return f"PDF document: {file_path.name}\n[PDF content would be extracted here]"
            else:
                # Handle text files (txt, md, etc.)
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return ""


def discover_documents(source_directory: Path) -> Iterable[Path]:
    """Yield documents from the given directory that should be ingested."""
    for path in source_directory.glob("**/*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".pdf", ".py", ".json"}:
            yield path


async def main() -> None:
    """Process documents and create vector embeddings."""
    processor = DocumentProcessor()
    settings = get_settings()
    
    print("🚀 Starting document ingestion...")
    print(f"📁 Documents directory: {processor.documents_path}")
    print(f"🗄️ Vector store: {processor.vector_store_path}")
    print(f"🤖 Ollama host: {settings.ollama_host}")
    print(f"📊 Embedding model: {settings.embedding_model}")
    
    # Collect all documents
    documents = list(discover_documents(processor.documents_path))
    
    if not documents:
        print("❌ No documents found in storage/documents/")
        print("📝 Add your documents (.txt, .md, .pdf, .py, .json) to storage/documents/ directory")
        return
    
    print(f"📄 Found {len(documents)} documents to process")
    
    # Storage for embeddings and metadata
    all_embeddings = []
    all_metadata = []
    
    for doc_path in documents:
        print(f"📖 Processing: {doc_path.name}")
        
        # Load document content
        content = processor.load_document(doc_path)
        if not content:
            continue
            
        # Split into chunks
        chunks = processor.chunk_text(content)
        print(f"  ✂️ Split into {len(chunks)} chunks")
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            try:
                # Get embeddings
                embedding = await processor.get_embeddings(chunk)
                
                # Store embedding and metadata
                all_embeddings.append(embedding)
                all_metadata.append({
                    "file": str(doc_path.name),
                    "chunk_id": i,
                    "content": chunk,
                    "file_path": str(doc_path)
                })
                
                print(f"  ✅ Processed chunk {i+1}/{len(chunks)}")
                
            except Exception as e:
                print(f"  ❌ Error processing chunk {i}: {e}")
    
    if not all_embeddings:
        print("❌ No embeddings generated")
        return
    
    # Create FAISS index
    print("🔧 Creating FAISS vector index...")
    embeddings_array = np.array(all_embeddings, dtype=np.float32)
    
    # Create index
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
    index.add(embeddings_array)
    
    # Save index and metadata
    index_path = processor.vector_store_path / "faiss_index.bin"
    metadata_path = processor.vector_store_path / "metadata.json"
    
    faiss.write_index(index, str(index_path))
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Vector store created successfully!")
    print(f"📊 Indexed {len(all_embeddings)} chunks from {len(documents)} documents")
    print(f"💾 Saved to: {processor.vector_store_path}")


if __name__ == "__main__":
    asyncio.run(main())
