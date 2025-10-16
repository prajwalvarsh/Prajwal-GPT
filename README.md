# PrajwalGPT Monorepo

This repository provides the foundational monorepo layout, shared configuration,
and tooling required to build the PrajwalGPT retrieval-augmented generation
(RAG) system.

## Directory layout

```
.
├── backend/        # FastAPI service and API entrypoint
├── deployment/     # Docker and orchestration assets
├── frontend/       # Vite + React single-page application
├── ingestion/      # Document ingestion and indexing jobs
├── shared/         # Cross-service configuration defaults and helpers
├── .env.example    # Sample environment variables consumed everywhere
├── pyproject.toml  # Python tooling, dependency, and lint configuration
└── requirements.txt
```

## Shared configuration

All runtime configuration is centralised in `shared/`. The `constants.json`
file lists the canonical defaults for model selection, vector store locations,
and API endpoints. `shared.config.Settings` loads `.env` overrides and exposes
a single cached settings instance that is consumed by both the backend service
and ingestion scripts.

TypeScript projects use the same defaults via the `@shared` Vite alias, ensuring
that every piece of the stack references the same defaults without hand-written
duplicates.

To customise values, copy the provided example file and adjust as needed:

```bash
cp .env.example .env
```

## Tooling

### Python

- Python 3.11+ (managed via `pyproject.toml`)
- FastAPI + Uvicorn for the API surface
- Ruff, Black, and MyPy are preconfigured for linting, formatting, and static
  typing

Install dependencies for backend and ingestion work with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn backend.app.main:app --reload
```

### Frontend

The frontend is a Vite-based React application colocated under
`frontend/`.

```bash
cd frontend
npm install
npm run dev
```

The application consumes the shared configuration via the
`@shared/constants.json` alias. Update `VITE_API_BASE_URL` inside `.env` (or a
frontend-specific `.env.local`) to point at the running backend service.

### Deployment

`deployment/docker-compose.yml` demonstrates how the backend and frontend can be
composed. Build and run the stack with:

```bash
cd deployment
cp ../.env.example ../.env
API_PORT=8000 FRONTEND_PORT=5173 docker compose up --build
```

Persisted vector store data is mounted into `storage/` at the project root. This
folder is ignored by Git by default.

## Next steps

With the shared scaffolding in place you can:

1. Flesh out backend routes for chat inference and document retrieval.
2. Implement ingestion pipelines that transform raw data into embeddings.
3. Expand the frontend UI to capture prompts and display context-rich answers.

This structure keeps configuration, dependencies, and tooling consistent as the
PrajwalGPT platform grows.
