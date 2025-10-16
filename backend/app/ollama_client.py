"""Ollama client for PrajwalGPT backend."""

import httpx
from typing import Dict, Any, List
from shared import get_settings


class OllamaClient:
    """Simple client for interacting with Ollama API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.ollama_host
        self.model = self.settings.ollama_model
        self.embedding_model = self.settings.embedding_model
    
    async def generate(self, prompt: str, stream: bool = False) -> Dict[str, Any]:
        """Generate text using the configured model."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Chat using the configured model."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False  # Disable streaming for simpler response
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def embed(self, text: str) -> Dict[str, Any]:
        """Generate embeddings using the configured embedding model."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False


# Global instance
ollama_client = OllamaClient()