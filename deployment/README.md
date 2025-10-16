# Deployment Assets

The files in this directory provide starting points for running the PrajwalGPT
stack locally with Docker.

## Docker Compose

`docker-compose.yml` builds the backend and frontend services directly from the
source tree.

```bash
cd deployment
cp ../.env.example ../.env  # customise your environment
API_PORT=8000 FRONTEND_PORT=5173 docker compose up --build
```

The compose file mounts the shared configuration module into the backend
container to ensure every service reads from the same defaults and overrides.
You can extend this setup to add persistence layers (for example, a vector store
or document database) as the project evolves.
