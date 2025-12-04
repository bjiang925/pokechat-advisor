"""
LLM Service - Orchestrates both Stage 1 and Stage 2 LLM operations.
"""
from typing import Tuple, List
from ml_models.model_manager import model_manager
from ml_models.prompts.query_generation import get_query_generation_prompt
from ml_models.prompts.answer_generation import get_answer_generation_prompt
from backend.models.chat_models import Message


class LLMService:
    """Service for handling LLM operations."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.model_manager = model_manager
    
    async def generate_api_query(self, user_question: str) -> str:
        """
        Stage 1: Convert natural language question to API query.
        
        Args:
            user_question: The user's natural language question
            
        Returns:
            str: The generated API query string
        """
        # Generate the prompt
        prompt = get_query_generation_prompt(user_question)
        
        # Get response from model (disable thinking for faster query generation)
        _, query = self.model_manager.generate_response(
            prompt=prompt,
            enable_thinking=False,
            max_new_tokens=100
        )
        
        # Clean up the query (remove extra whitespace, newlines)
        query = query.strip().replace("\n", " ")
        
        return query
    
    async def generate_answer(
        self,
        user_question: str,
        api_response: str,
        conversation_history: List[Message] = None
    ) -> str:
        """
        Stage 2: Convert API JSON response to natural language answer.
        
        Args:
            user_question: The user's question
            api_response: The formatted API response
            conversation_history: Optional conversation history
            
        Returns:
            str: The generated natural language answer
        """
        # Format conversation history if provided
        history_text = None
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
        
        # Generate the prompt
        prompt = get_answer_generation_prompt(
            user_question=user_question,
            api_response=api_response,
            conversation_history=history_text
        )
        
        # Get response from model
        _, answer = self.model_manager.generate_response(
            prompt=prompt,
            enable_thinking=True,
            max_new_tokens=512
        )
        
        return answer.strip()
    
    def _format_conversation_history(self, history: List[Message]) -> str:
        """
        Format conversation history for the prompt.
        
        Args:
            history: List of Message objects
            
        Returns:
            str: Formatted conversation history
        """
        if not history:
            return ""
        
        formatted = []
        for msg in history[-6:]:  # Use last 6 messages for context
            role = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        
        return "\n".join(formatted)
    
    def is_model_ready(self) -> bool:
        """
        Check if the model is loaded and ready.
        
        Returns:
            bool: True if model is ready
        """
        return self.model_manager.is_loaded()


# Global instance
llm_service = LLMService()