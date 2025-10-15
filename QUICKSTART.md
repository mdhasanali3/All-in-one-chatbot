# Quick Start Guide

Get your AI Voice Knowledge Assistant up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- ElevenLabs API key (for voice synthesis)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd all-in-one-bot

# Copy environment template
cp .env.example .env
```

## Step 2: Configure API Keys

Edit `.env` file and add your API keys:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# Authentication (default works for testing)
ACCESS_KEY=admin_hasan_007_no_exit
```

## Step 3: Start the Application

```bash
# Start all services
docker-compose -f deployment/docker/docker-compose.yml up -d

# Wait for services to be ready (takes ~30 seconds)
docker-compose -f deployment/docker/docker-compose.yml ps
```

## Step 4: Access the Application

Open your browser and navigate to:

**Frontend**: http://localhost:8501

### Login

Enter the access key: `admin_hasan_007_no_exit`

## Step 5: Upload a Document

1. In the sidebar, click "Upload document to knowledge base"
2. Select a PDF, DOCX, Excel, CSV, or TXT file
3. Click "Upload Document"
4. Wait for confirmation message

## Step 6: Ask Questions

In the chat interface:

1. Type your question about the uploaded document
2. Press Enter or click Send
3. The AI will respond using information from your documents

Example questions:
- "What is this document about?"
- "Summarize the main points"
- "What are the key findings?"

## Features to Try

### Voice Interaction

1. Go to the "Voice" tab
2. Upload an audio file OR use the recording feature
3. The system will transcribe and respond

### Conversation Memory

- The system remembers your last 20 conversation turns
- Context is maintained across questions
- Click "Clear Conversation" to start fresh

### View Sources

- Expand the "Sources" section in responses
- See which document chunks were used
- Verify information accuracy

## Additional Services

### API Documentation
http://localhost:8000/docs - Interactive API documentation

### Monitoring Dashboards
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (login: admin/admin)

### Keycloak Admin
http://localhost:8080 (login: admin/admin)

## Stopping the Application

```bash
# Stop all services
docker-compose -f deployment/docker/docker-compose.yml down

# Stop and remove volumes (clears data)
docker-compose -f deployment/docker/docker-compose.yml down -v
```

## Troubleshooting

### Services not starting?

Check logs:
```bash
docker-compose -f deployment/docker/docker-compose.yml logs -f
```

### Can't login?

Verify ACCESS_KEY in `.env` matches: `admin_hasan_007_no_exit`

### Document upload failing?

Ensure the file format is supported: PDF, DOCX, XLSX, CSV, or TXT

### API errors?

1. Check OPENAI_API_KEY is valid
2. Ensure you have API credits
3. Check internet connectivity

## Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Check [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation
- Check API health: http://localhost:8000/health

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │ ← You interact here
│  (Streamlit)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │ ← Authentication & routing
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬────────┐
    ▼         ▼         ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ STT  │ │ RAG  │ │ LLM  │ │ TTS  │
│Service│ │Service│ │Service│ │Service│
└──────┘ └──────┘ └──────┘ └──────┘
```

Enjoy using your AI Voice Knowledge Assistant!
