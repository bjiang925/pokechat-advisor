"""
Chat Routes - API endpoints for chat functionality.
"""
from fastapi import APIRouter, HTTPException
from backend.models.chat_models import ChatRequest, ChatResponse
from backend.services.llm_service import llm_service
from backend.services.pokemon_service import pokemon_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user questions.
    
    Flow:
    1. User question → LLM generates API query (Stage 1)
    2. API query → Pokémon TCG API returns card data
    3. Card data → LLM generates natural language answer (Stage 2)
    4. Return answer with card information
    """
    try:
        # Stage 1: Generate API query from user question
        api_query = await llm_service.generate_api_query(request.message)
        
        print(f"User Question: {request.message}")
        print(f"Generated API Query: {api_query}")
        
        # Fetch card data from Pokémon TCG API
        api_response_raw = await pokemon_service.search_cards(api_query)
        api_response_formatted = pokemon_service.api_client.format_cards_for_llm(
            api_response_raw
        )
        
        print(f"API Response: {api_response_formatted[:200]}...")  # Log first 200 chars
        
        # Check if API returned no results
        if "No cards found" in api_response_formatted or "Error:" in api_response_formatted:
            return ChatResponse(
                response="I couldn't find any cards matching your question. Could you please rephrase your question or provide more details? For example, you could specify a card name, type, or other characteristics.",
                cards=[],
                query_used=api_query
            )
        
        # Stage 2: Generate natural language answer
        answer = await llm_service.generate_answer(
            user_question=request.message,
            api_response=api_response_formatted,
            conversation_history=request.conversation_history
        )
        
        # Extract structured card information
        cards = pokemon_service.extract_card_info(api_response_raw)
        
        return ChatResponse(
            response=answer,
            cards=cards,
            query_used=api_query
        )
    
    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the API is working."""
    return {
        "status": "ok",
        "message": "Chat API is working!"
    }