# PokéChat Advisor - Complete Setup Guide

This guide will walk you through setting up the PokéChat Advisor project from scratch.

## 📋 Prerequisites

### Required
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git**
- **Pokémon TCG API Key** - Get one free at https://dev.pokemontcg.io/
- **4GB RAM minimum** (8GB recommended)
- **5GB disk space** (for model and dependencies)

### Optional
- **NVIDIA GPU** with CUDA support for faster inference
- **NVIDIA Container Toolkit** for GPU support in Docker

## 🔨 Step-by-Step Setup

### Step 1: Create Project Directory Structure

```bash
mkdir pokechat-advisor
cd pokechat-advisor
```

Create all necessary directories:

```bash
mkdir -p frontend/components
mkdir -p backend/routes backend/services backend/models
mkdir -p ml_models/prompts
mkdir -p external
mkdir -p shared
mkdir -p tests
mkdir -p docs
```

### Step 2: Create Empty `__init__.py` Files

```bash
# Frontend
touch frontend/__init__.py
touch frontend/components/__init__.py

# Backend
touch backend/__init__.py
touch backend/routes/__init__.py
touch backend/services/__init__.py
touch backend/models/__init__.py

# ML Models
touch ml_models/__init__.py
touch ml_models/prompts/__init__.py

# External
touch external/__init__.py

# Shared
touch shared/__init__.py

# Tests
touch tests/__init__.py
```

### Step 3: Copy All Artifact Files

Copy all the artifact files I created into their respective directories:

1. **Root directory:**
   - `requirements.txt`
   - `.env.example`
   - `docker-compose.yml`
   - `Dockerfile.backend`
   - `Dockerfile.frontend`
   - `.gitignore`
   - `README.md`
   - `SETUP_GUIDE.md` (this file)

2. **Backend files:**
   - `backend/main.py`
   - `backend/routes/chat.py`
   - `backend/services/llm_service.py`
   - `backend/services/pokemon_service.py`
   - `backend/models/chat_models.py`

3. **Frontend files:**
   - `frontend/app.py`

4. **ML Models:**
   - `ml_models/model_manager.py`
   - `ml_models/prompts/query_generation.py`
   - `ml_models/prompts/answer_generation.py`

5. **External:**
   - `external/pokemon_tcg_api.py`

6. **Tests:**
   - `tests/test_integration.py`

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```bash
# Required: Get your API key from https://dev.pokemontcg.io/
POKEMON_TCG_API_KEY=your_actual_api_key_here

# The rest can use defaults
POKEMON_TCG_API_URL=https://api.pokemontcg.io/v2
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8501
BACKEND_API_URL=http://backend:8000
MODEL_NAME=Qwen/Qwen3-0.6B
MAX_NEW_TOKENS=512
DEVICE_MAP=auto
MAX_CONVERSATION_HISTORY=10
SESSION_TIMEOUT_MINUTES=30
```

### Step 5: Verify File Structure

Your directory should look like this:

```
pokechat-advisor/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── SETUP_GUIDE.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── frontend/
│   ├── __init__.py
│   ├── app.py
│   └── components/
│       └── __init__.py
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   └── pokemon_service.py
│   └── models/
│       ├── __init__.py
│       └── chat_models.py
├── ml_models/
│   ├── __init__.py
│   ├── model_manager.py
│   └── prompts/
│       ├── __init__.py
│       ├── query_generation.py
│       └── answer_generation.py
├── external/
│   ├── __init__.py
│   └── pokemon_tcg_api.py
├── shared/
│   └── __init__.py
└── tests/
    ├── __init__.py
    └── test_integration.py
```

### Step 6: Build and Run

```bash
# Build and start containers
docker-compose up --build
```

**First run will take 5-10 minutes** to:
- Download base Docker images
- Install Python dependencies
- Download Qwen3-0.6B model (~2GB)

### Step 7: Verify Everything Works

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "api_accessible": true
   }
   ```

2. **Access Frontend:**
   - Open browser: http://localhost:8501
   - You should see the PokéChat Advisor interface

3. **Test the Chat:**
   - Ask: "What's Pikachu's type?"
   - You should get a response with card information

## 🐛 Troubleshooting

### Issue: "Model not loaded"

**Problem:** Backend shows `model_loaded: false`

**Solutions:**
```bash
# Check backend logs
docker-compose logs backend

# Look for model loading errors
# Common causes:
# - Not enough RAM (need 4GB+)
# - Disk space full
# - Network issues downloading model
```

### Issue: "API not accessible"

**Problem:** Backend shows `api_accessible: false`

**Solutions:**
```bash
# 1. Check if your API key is set correctly
cat .env | grep POKEMON_TCG_API_KEY

# 2. Test API directly
curl -H "X-Api-Key: YOUR_KEY" https://api.pokemontcg.io/v2/cards?q=name:Pikachu

# 3. Check if you've hit rate limits (60 requests/hour without key)
```

### Issue: Backend won't start

**Solutions:**
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port 8000 already in use
sudo lsof -i :8000  # Find what's using the port

# 2. Restart from scratch
docker-compose down -v
docker-compose up --build
```

### Issue: Frontend can't connect to backend

**Solutions:**
```bash
# 1. Check if both containers are running
docker-compose ps

# 2. Check backend is accessible from frontend container
docker-compose exec frontend curl http://backend:8000/health

# 3. Check environment variable
docker-compose exec frontend env | grep BACKEND_API_URL
```

### Issue: Slow responses

**Solutions:**
- **Use GPU:** If you have NVIDIA GPU, install nvidia-container-toolkit
- **Reduce token limit:** Lower `MAX_NEW_TOKENS` in `.env`
- **Use smaller examples:** Complex queries take longer

## 🧪 Running Tests

```bash
# Run all tests
docker-compose exec backend pytest tests/ -v

# Run specific test
docker-compose exec backend pytest tests/test_integration.py::test_health_endpoint -v
```

## 🔄 Development Workflow

### Making Changes

1. **Backend changes:**
   ```bash
   # Edit files in backend/
   # No need to rebuild, changes are mounted as volumes
   docker-compose restart backend
   ```

2. **Frontend changes:**
   ```bash
   # Edit files in frontend/
   # Streamlit auto-reloads
   # Just refresh the browser
   ```

3. **Prompt changes:**
   ```bash
   # Edit ml_models/prompts/*.py
   docker-compose restart backend
   ```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears model cache)
docker-compose down -v
```

## 🚀 Production Deployment Notes

For production deployment, consider:

1. **Security:**
   - Change `allow_origins=["*"]` in `backend/main.py` to specific domains
   - Use HTTPS
   - Store API keys securely (not in .env)

2. **Performance:**
   - Use GPU instances
   - Consider model quantization
   - Implement caching for common queries

3. **Scaling:**
   - Use separate containers for model serving
   - Implement load balancing
   - Add Redis for session management

4. **Monitoring:**
   - Add logging infrastructure
   - Monitor model performance
   - Track API usage

## 📚 Next Steps

- Read the [README.md](README.md) for usage examples
- Check the API docs at http://localhost:8000/docs
- Modify prompts in `ml_models/prompts/` to customize behavior
- Add more features to the frontend

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify your setup matches this guide
3. Ensure your API key is valid
4. Try rebuilding: `docker-compose up --build --force-recreate`

## ✅ Success Checklist

- [ ] All directories created
- [ ] All files copied to correct locations
- [ ] `.env` file configured with valid API key
- [ ] Docker and Docker Compose installed
- [ ] `docker-compose up --build` runs without errors
- [ ] Backend health check returns "healthy"
- [ ] Frontend loads at http://localhost:8501
- [ ] Can ask questions and get responses
- [ ] Card images display correctly

If all items are checked, you're ready to use PokéChat Advisor! 🎉