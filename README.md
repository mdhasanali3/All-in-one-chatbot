# AI Voice Knowledge Assistant

A comprehensive AI-powered voice assistant with document knowledge base, supporting real-time conversations with authentication and memory.

## Features

- **Document Knowledge Base**: Upload and query PDF, DOCX, Excel, CSV, and TXT files
- **Voice Interaction**: Speech-to-text and text-to-speech capabilities
- **Conversational AI**: Context-aware conversations with 20-turn memory
- **Secure Authentication**: Keycloak + JWT with custom access key validation
- **Real-time Streaming**: WebRTC for low-latency audio streaming
- **Scalable Architecture**: Microservices with gRPC communication
- **Production Ready**: Docker + Kubernetes deployment with monitoring

## Tech Stack

| Component | Technology |
|-----------|-----------|
| STT | OpenAI Whisper |
| LLM | GPT-4o-mini |
| TTS | ElevenLabs |
| RAG | LangChain + FAISS |
| Backend | FastAPI + gRPC |
| Auth | Keycloak + JWT |
| Frontend | Streamlit |
| Deployment | Docker + Kubernetes + AWS SageMaker |
| Monitoring | Prometheus + Grafana + CloudWatch |

## Project Structure

```
ai-voice-knowledge-assistant/
├── frontend/              # Streamlit UI
├── backend/
│   ├── gateway/          # FastAPI gateway + auth middleware
│   ├── auth_service/     # Keycloak integration
│   ├── stt_service/      # Whisper STT
│   ├── rag_service/      # LangChain + FAISS
│   ├── llm_service/      # GPT-4o-mini
│   ├── tts_service/      # ElevenLabs TTS
│   └── shared/           # Common utilities
├── deployment/           # Docker, K8s, monitoring configs
├── data/                 # Knowledge base storage
└── tests/                # Test suites
```

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Keycloak instance
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd all-in-one-bot
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r frontend/requirements.txt
```

4. Run with Docker Compose
```bash
docker-compose up -d
```

5. Access the application
- Frontend: http://localhost:8501
- API Gateway: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Authentication

Default access key: `admin_hasan_007_no_exit`

Users must authenticate with this key to access the system.

## Development

### Running Individual Services

```bash
# Gateway
cd backend/gateway && uvicorn main:app --reload

# Frontend
cd frontend && streamlit run app.py
```

### Running Tests

```bash
pytest tests/
```

## Deployment

See `deployment/k8s/` for Kubernetes manifests and deployment instructions.

## Monitoring

Access Prometheus at port 9090 and Grafana at port 3000 for system metrics and dashboards.

## License

MIT License
