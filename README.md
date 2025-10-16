# PrajwalGPT - Personal AI Assistant

A privacy-focused, locally-hosted AI assistant that provides personalized responses based on your documents and knowledge. Built with RAG (Retrieval-Augmented Generation) using Ollama, FastAPI, and React.

## 🚀 Features

- **Personal Knowledge Base**: Upload and process your documents for personalized AI responses
- **Local Privacy**: Runs entirely on your machine using Ollama - no data sent to external APIs
- **Modern Stack**: FastAPI backend, React TypeScript frontend, FAISS vector database
- **Real-time Chat**: Interactive web interface with streaming responses
- **Document Ingestion**: Automated processing and embedding of your documents
- **RAG System**: Intelligent retrieval of relevant context for accurate responses

## 🏗️ Architecture

```
.
├── backend/        # FastAPI service with chat and RAG endpoints
├── deployment/     # Docker and orchestration assets  
├── frontend/       # React TypeScript SPA with chat interface
├── ingestion/      # Document processing and vector embedding pipeline
├── shared/         # Configuration and utilities
├── storage/        # Document storage and vector database (auto-created)
└── pyproject.toml  # Python dependencies and configuration
```

## 🛠️ Tech Stack

**Backend:**
- **FastAPI** - High-performance API framework
- **Ollama** - Local LLM inference (llama2, nomic-embed-text)
- **FAISS** - Vector similarity search
- **Pydantic** - Data validation and settings

**Frontend:**
- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Modern UI** - Clean chat interface with status indicators

**AI/ML:**
- **RAG Pipeline** - Document chunking, embedding, and retrieval
- **Local LLMs** - No external API dependencies
- **Vector Store** - Persistent similarity search index

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker** (for Ollama)
- **UV** package manager (recommended)

### 1. Setup Ollama

```bash
# Pull and run Ollama with required models
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec ollama ollama pull llama2
docker exec ollama ollama pull nomic-embed-text
```

### 2. Backend Setup

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Start the backend server
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### 4. Ingest Your Documents

```bash
# Add your documents to storage/documents/
mkdir -p storage/documents
# Copy your .txt, .md, or .pdf files here

# Process documents into vector embeddings
uv run python ingestion/ingest.py
```

### 5. Start Chatting!

Open http://localhost:5173 and start asking questions about your documents!

## 📋 API Endpoints

### Health Checks
- `GET /health` - Basic service health
- `GET /health/ollama` - Ollama connection status  
- `GET /health/rag` - RAG system readiness

### Chat & Generation
- `POST /generate` - Basic text generation
- `POST /chat/rag` - RAG-enhanced chat with document context
- `POST /chat/simple` - Fast chat with predefined context

### Example Usage

```bash
# Test basic generation
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me about Prajwal"}'

# Test RAG chat
curl -X POST "http://localhost:8000/chat/rag" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What projects has Prajwal worked on?"}]}'
```

## 📁 Document Management

### Supported Formats
- **Text files** (.txt, .md)
- **PDF documents** (planned)
- **Code files** (planned)

### Adding Documents

1. Place documents in `storage/documents/`
2. Run ingestion: `uv run python ingestion/ingest.py`
3. Restart backend to load new embeddings

### Example Documents Structure
```
storage/
├── documents/
│   ├── resume.txt
│   ├── projects.md
│   └── skills.txt
└── vector_store/
    ├── faiss_index.bin
    └── metadata.json
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# API Configuration
API_BASE_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000

# Ollama Configuration  
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# RAG Configuration
VECTOR_STORE_PATH=storage/vector_store
DOCUMENTS_PATH=storage/documents
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### Model Configuration

Update models in `shared/constants.json`:

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama2",
    "embedding_model": "nomic-embed-text"
  }
}
```

## 🚀 Development

### Backend Development

```bash
# Run with auto-reload
uv run uvicorn backend.app.main:app --reload

# Run tests
uv run pytest

# Format code
uv run ruff format

# Type check
uv run mypy backend/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check
```

## 🐳 Docker Deployment

```bash
cd deployment
cp ../.env.example ../.env

# Start full stack
docker compose up --build

# Backend only
docker compose up backend

# With custom ports
API_PORT=8080 FRONTEND_PORT=3000 docker compose up
```

## 🔍 Troubleshooting

### Common Issues

**Ollama connection errors:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
docker restart ollama
```

**RAG not working:**
```bash
# Verify documents are processed
ls storage/vector_store/

# Re-run ingestion
uv run python ingestion/ingest.py
```

**Frontend build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Performance Tips

- **Chunk size**: Adjust `CHUNK_SIZE` for your document types
- **Model selection**: Try different Ollama models for speed vs quality
- **Vector dimensions**: Optimize for your hardware capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for local LLM inference
- **FastAPI** for the excellent Python web framework
- **React** and **Vite** for the modern frontend stack
- **FAISS** for efficient vector similarity search
- **cto.new** for initial file structure and UI

---

**Built with ❤️ for personal AI assistance**
