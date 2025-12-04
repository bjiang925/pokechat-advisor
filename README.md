# PokéChat Advisor

An AI-powered conversational assistant for the Pokémon Trading Card Game (TCG). Ask questions about cards in natural language and get accurate, helpful responses backed by real-time API data.

## 🎯 Features

- **Natural Language Understanding**: Ask questions conversationally
- **Real-time Data**: Queries the official Pokémon TCG API
- **Two-Stage LLM Reasoning**: 
  - Stage 1: Natural language → API query
  - Stage 2: JSON data → Natural language answer
- **Interactive Chat Interface**: Built with Streamlit
- **Card Visualization**: Display card images and detailed stats
- **Context-Aware**: Supports follow-up questions

## 🏗️ Architecture

```
User (Streamlit) ←→ FastAPI Backend ←→ Qwen3-0.6B LLM
                          ↓
                   Pokémon TCG API
```

**Frontend**: Streamlit interactive chat interface  
**Backend**: FastAPI REST API with LLM orchestration  
**AI Model**: Qwen3-0.6B for query generation and answer synthesis  
**Data Source**: Pokémon TCG API (https://pokemontcg.io)

## 📋 Prerequisites

- Docker and Docker Compose
- Pokémon TCG API Key (get one at https://dev.pokemontcg.io)
- NVIDIA GPU (optional but recommended for faster inference)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pokechat-advisor
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Pokémon TCG API key:

```
POKEMON_TCG_API_KEY=your_api_key_here
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build both frontend and backend containers
- Download the Qwen3-0.6B model (~2GB)
- Start the FastAPI backend on port 8000
- Start the Streamlit frontend on port 8501

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💬 Example Questions

Try asking:
- "What's Charizard's weakness?"
- "Show me water-type Pokémon with high HP"
- "Compare Blastoise and Venusaur"
- "What Pokémon counter electric decks?"
- "Find rare cards from the Base Set"
- "What does Gardevoir EX's ability do?"

## 📁 Project Structure

```
pokechat-advisor/
├── frontend/               # Streamlit UI
│   ├── app.py             # Main frontend application
│   └── components/        # UI components
├── backend/               # FastAPI backend
│   ├── main.py           # FastAPI app entry point
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   └── models/           # Pydantic models
├── ml_models/            # ML model management
│   ├── model_manager.py  # Model loader (singleton)
│   └── prompts/          # LLM prompt templates
├── external/             # External API clients
│   └── pokemon_tcg_api.py
├── docker-compose.yml    # Container orchestration
└── requirements.txt      # Python dependencies
```

## 🔧 Development

### Running Without Docker

**Backend:**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

**Frontend:**
```bash
streamlit run frontend/app.py
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POKEMON_TCG_API_KEY` | Your Pokémon TCG API key | Required |
| `BACKEND_API_URL` | Backend API URL | http://localhost:8000 |
| `MODEL_NAME` | Hugging Face model identifier | Qwen/Qwen3-0.6B |
| `MAX_NEW_TOKENS` | Max tokens for generation | 512 |

## 🧪 Testing

```bash
pytest tests/
```

## 📝 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Main Endpoint: `/api/chat`

**Request:**
```json
{
  "message": "What's Blastoise's weakness?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Blastoise is a Water-type Pokémon...",
  "cards": [
    {
      "name": "Blastoise",
      "hp": "140",
      "types": ["Water"],
      "weaknesses": ["Lightning"],
      ...
    }
  ],
  "query_used": "name:Blastoise"
}
```

## 🐛 Troubleshooting

**Model Loading Issues:**
- Ensure you have enough disk space (~2GB for model)
- Check Docker container logs: `docker-compose logs backend`

**API Connection Errors:**
- Verify your API key is correct in `.env`
- Check the Pokémon TCG API status

**Performance Issues:**
- Use GPU acceleration if available
- Reduce `MAX_NEW_TOKENS` for faster responses

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational purposes. Pokémon and Pokémon TCG are trademarks of Nintendo, Creatures Inc., and GAME FREAK inc.

## 🙏 Acknowledgments

- [Pokémon TCG API](https://pokemontcg.io)
- [Qwen Models](https://huggingface.co/Qwen)
- [Streamlit](https://streamlit.io)
- [FastAPI](https://fastapi.tiangolo.com)