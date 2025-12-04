"""
Pokémon Service - Handles Pokémon TCG API interactions and data processing.
"""
from typing import Dict, Any, List
from external.pokemon_tcg_api import pokemon_api_client
from backend.models.chat_models import CardInfo


class PokemonService:
    """Service for handling Pokémon TCG API operations."""
    
    def __init__(self):
        """Initialize the Pokémon service."""
        self.api_client = pokemon_api_client
    
    async def search_cards(self, query: str) -> Dict[str, Any]:
        """
        Search for cards using the provided query.
        
        Args:
            query: The API query string
            
        Returns:
            Dict containing the API response
        """
        return await self.api_client.search_cards(query)
    
    async def get_formatted_card_data(self, query: str) -> str:
        """
        Search for cards and return formatted data for LLM.
        
        Args:
            query: The API query string
            
        Returns:
            str: Formatted card data
        """
        response = await self.search_cards(query)
        return self.api_client.format_cards_for_llm(response)
    
    def extract_card_info(self, api_response: Dict[str, Any]) -> List[CardInfo]:
        """
        Extract structured card information from API response.
        
        Args:
            api_response: The raw API response
            
        Returns:
            List of CardInfo objects
        """
        if "error" in api_response or "data" not in api_response:
            return []
        
        cards = []
        for card_data in api_response.get("data", [])[:5]:  # Limit to 5 cards
            card_info = CardInfo(
                name=card_data.get("name", "Unknown"),
                id=card_data.get("id", "Unknown"),
                hp=card_data.get("hp"),
                types=card_data.get("types", []),
                weaknesses=[
                    f"{w.get('type', 'Unknown')} ({w.get('value', 'N/A')})"
                    for w in card_data.get("weaknesses", [])
                ],
                resistances=[
                    f"{r.get('type', 'Unknown')} ({r.get('value', 'N/A')})"
                    for r in card_data.get("resistances", [])
                ],
                retreat_cost=len(card_data.get("retreatCost", [])),
                image_url=card_data.get("images", {}).get("small"),
                abilities=[
                    f"{a.get('name', 'Unknown')}: {a.get('text', 'No description')}"
                    for a in card_data.get("abilities", [])
                ],
                attacks=[
                    f"{a.get('name', 'Unknown')} - {a.get('damage', '0')} damage"
                    for a in card_data.get("attacks", [])
                ],
                set_name=card_data.get("set", {}).get("name"),
                rarity=card_data.get("rarity")
            )
            cards.append(card_info)
        
        return cards
    
    async def test_api_connection(self) -> bool:
        """
        Test if the Pokémon TCG API is accessible.
        
        Returns:
            bool: True if API is accessible
        """
        try:
            response = await self.api_client.search_cards("name:Pikachu", page_size=1)
            return "error" not in response
        except Exception:
            return False


# Global instance
pokemon_service = PokemonService()