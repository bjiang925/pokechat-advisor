"""
FastAPI Backend - Main application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ml_models.model_manager import model_manager
from backend.routes.chat import router as chat_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Load the model
    print("Starting up PokéChat Advisor Backend...")
    print("Loading Qwen3-0.6B model...")
    model_manager.load_model()
    print("Model loaded successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down PokéChat Advisor Backend...")


# Create FastAPI app
app = FastAPI(
    title="PokéChat Advisor API",
    description="AI-powered Pokémon TCG knowledge assistant backend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PokéChat Advisor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from backend.services.llm_service import llm_service
    from backend.services.pokemon_service import pokemon_service
    
    model_loaded = llm_service.is_model_ready()
    api_accessible = await pokemon_service.test_api_connection()
    
    return {
        "status": "healthy" if model_loaded and api_accessible else "degraded",
        "model_loaded": model_loaded,
        "api_accessible": api_accessible
    }