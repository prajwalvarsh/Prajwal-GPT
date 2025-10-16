"""Minimal FastAPI application bootstrapped for the PrajwalGPT backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

from shared import get_settings
from .ollama_client import ollama_client
from .rag_system import rag_retriever

app = FastAPI(
    title="PrajwalGPT API",
    version="0.1.0",
    summary="Backend service for orchestrating retrieval-augmented generation workflows.",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class GenerateRequest(BaseModel):
    prompt: str


@app.get("/health", tags=["meta"])
def healthcheck() -> dict[str, str]:
    """Simple health endpoint that surfaces the configured model."""

    settings = get_settings()
    return {"status": "ok", "model": settings.ollama_model}


@app.get("/health/ollama", tags=["meta"])
async def ollama_health() -> dict[str, str | bool]:
    """Check if Ollama is running and accessible."""
    
    is_healthy = await ollama_client.health_check()
    return {"ollama_status": "ok" if is_healthy else "unavailable", "healthy": is_healthy}


@app.get("/health/rag", tags=["meta"])
async def rag_health() -> dict[str, str | bool]:
    """Check if RAG system is ready."""
    
    is_ready = rag_retriever.is_available()
    return {"rag_status": "ready" if is_ready else "not_ready", "ready": is_ready}


@app.post("/chat/simple", tags=["llm"])
async def chat_simple_with_context(request: ChatRequest) -> Dict[str, Any]:
    """Simple chat with predefined context about Prajwal."""
    
    try:
        # Predefined context about Prajwal based on the documents
        prajwal_context = """
        Prajwal is a passionate developer working with Natural Language Processing and AI systems.

        Skills and Interests:
        - Programming Languages: Python, JavaScript, TypeScript
        - AI/ML Technologies: Large Language Models (LLMs), RAG, Vector databases, Ollama
        - Backend: FastAPI, async programming, database design
        - Frontend: React, TypeScript, Vite, responsive design
        - Tools: VS Code, Git, Docker, UV package manager

        Current Projects:
        - PrajwalGPT: A personal RAG-based AI assistant using Ollama, FastAPI, React
        - Focus on privacy-focused local LLM processing
        - Building efficient RAG workflows and personalized AI systems
        """

        # Get the latest user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        latest_query = user_messages[-1].content

        # Build enhanced prompt with context - use generate format instead of chat
        enhanced_prompt = f"""You are PrajwalGPT, an AI assistant that knows about Prajwal. 

CONTEXT ABOUT PRAJWAL:
{prajwal_context}

INSTRUCTIONS:
- Answer questions about Prajwal based on the context provided
- Be helpful and informative when discussing Prajwal's work and skills
- If asked about topics not related to Prajwal, politely redirect to discussing Prajwal
- Keep responses concise but informative

USER QUESTION: {latest_query}

RESPONSE:"""

        response = await ollama_client.generate(enhanced_prompt)
        return response
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simple chat failed: {str(e)}")


@app.post("/chat/rag", tags=["llm"])
async def chat_with_rag(request: ChatRequest) -> Dict[str, Any]:
    """Chat with RAG - uses your documents as context."""
    
    try:
        # Get the latest user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        latest_query = user_messages[-1].content
        
        # Get relevant context from documents
        context = await rag_retriever.get_context_for_query(latest_query)
        
        # Build enhanced prompt
        if context:
            system_prompt = f"""You are PrajwalGPT, an AI assistant that knows about Prajwal based on the provided documents. 

IMPORTANT INSTRUCTIONS:
- Only answer questions about Prajwal based on the provided context
- If the question is not about Prajwal or if you don't have relevant information in the context, politely say you can only discuss Prajwal based on the available documents
- Be helpful and informative when answering about Prajwal
- Always reference the documents when providing information

CONTEXT FROM PRAJWAL'S DOCUMENTS:
{context}

Please answer the user's question based on this context."""

            enhanced_messages = [
                {"role": "system", "content": system_prompt}
            ] + [{"role": msg.role, "content": msg.content} for msg in request.messages]
        else:
            # No context found
            fallback_prompt = """You are PrajwalGPT, an AI assistant that knows about Prajwal. However, I don't have any relevant documents loaded about Prajwal yet. 

Please let the user know that:
1. You're designed to answer questions about Prajwal based on his documents
2. No relevant documents are currently available
3. They should add documents about Prajwal to the storage/documents/ folder and run the ingestion process"""

            enhanced_messages = [
                {"role": "system", "content": fallback_prompt}
            ] + [{"role": msg.role, "content": msg.content} for msg in request.messages]

        response = await ollama_client.chat(enhanced_messages)
        return response
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Chat failed: {str(e)}")


@app.post("/generate/rag", tags=["llm"])
async def generate_with_rag(request: GenerateRequest) -> Dict[str, Any]:
    """Generate text with RAG - uses your documents as context."""
    
    try:
        # Get relevant context
        context = await rag_retriever.get_context_for_query(request.prompt)
        
        # Build enhanced prompt
        if context:
            enhanced_prompt = f"""You are PrajwalGPT, an AI assistant that knows about Prajwal based on the provided documents.

IMPORTANT: Only answer questions about Prajwal based on the provided context. If the question is not about Prajwal, politely redirect to topics about Prajwal.

CONTEXT FROM PRAJWAL'S DOCUMENTS:
{context}

USER QUESTION: {request.prompt}

Please answer based on the context above."""
        else:
            enhanced_prompt = f"""You are PrajwalGPT, but I don't have any documents about Prajwal loaded yet. Please let the user know they should add documents about Prajwal to the storage/documents/ folder and run the ingestion process.

USER QUESTION: {request.prompt}"""

        response = await ollama_client.generate(enhanced_prompt)
        return response
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Generation failed: {str(e)}")


@app.get("/search", tags=["rag"])
async def search_documents(q: str, limit: int = 5) -> Dict[str, Any]:
    """Search through your documents."""
    
    try:
        results = await rag_retriever.search_documents(q, top_k=limit)
        return {
            "query": q,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/chat", tags=["llm"])
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Chat with the LLM using conversation history."""
    
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        response = await ollama_client.chat(messages)
        return response
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/generate", tags=["llm"])
async def generate(request: GenerateRequest) -> Dict[str, Any]:
    """Generate text from a single prompt."""
    
    try:
        response = await ollama_client.generate(request.prompt)
        return response
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/models", tags=["llm"])
async def list_models() -> Dict[str, Any]:
    """List available models in Ollama."""
    
    try:
        response = await ollama_client.list_models()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@app.get("/config", tags=["meta"])
def read_config() -> dict[str, str | int]:
    """Expose a subset of shared configuration for debugging purposes."""

    settings = get_settings()
    return {
        "ollama_host": settings.ollama_host,
        "ollama_model": settings.ollama_model,
        "vector_store_path": settings.vector_store_path,
        "api_base_url": settings.api_base_url,
        "api_port": settings.api_port,
    }
