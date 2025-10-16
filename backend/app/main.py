"""Minimal FastAPI application bootstrapped for the PrajwalGPT backend."""

from fastapi import FastAPI

from shared import get_settings

app = FastAPI(
    title="PrajwalGPT API",
    version="0.1.0",
    summary="Backend service for orchestrating retrieval-augmented generation workflows.",
)


@app.get("/health", tags=["meta"])
def healthcheck() -> dict[str, str]:
    """Simple health endpoint that surfaces the configured model."""

    settings = get_settings()
    return {"status": "ok", "model": settings.ollama_model}


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
