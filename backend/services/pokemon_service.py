"""
Pokémon Service - Handles Pokémon TCG API interactions and data processing.
"""
import os
import json
from typing import Dict, Any, List
from external.pokemon_tcg_api import pokemon_api_client
from backend.models.chat_models import CardInfo


class PokemonService:
    """Service for handling Pokémon TCG API operations."""
    
    def __init__(self):
        """Initialize the Pokémon service."""
        self.api_client = pokemon_api_client
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        self.demo_data = {}
        
        if self.demo_mode:
            self._load_demo_data()
    
    def _load_demo_data(self):
        """Load demo data from JSON file."""
        demo_file = os.getenv("DEMO_DATA_FILE", "demo_data.json")
        
        try:
            # Try multiple possible paths
            possible_paths = [
                demo_file,
                f"/app/{demo_file}",
                f"./backend/{demo_file}",
                f"./{demo_file}"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        self.demo_data = json.load(f)
                    print(f"✓ Demo mode enabled - Loaded data from {path}")
                    print(f"  Available cards: {', '.join(self.demo_data.keys())}")
                    return
            
            print(f"⚠ Demo mode enabled but {demo_file} not found")
            print(f"  Tried paths: {possible_paths}")
        except Exception as e:
            print(f"✗ Error loading demo data: {str(e)}")
    
    def _search_in_demo_data(self, query: str) -> Dict[str, Any]:
        """
        Search for card in demo data based on query.
        
        Args:
            query: The API query string (e.g., "name:Pikachu")
            
        Returns:
            Dict containing the card data or empty response
        """
        # Extract card name from query
        # Common patterns: "name:Pikachu", "name:charizard types:Fire"
        query_lower = query.lower()
        
        # Try to find a matching card
        for card_key, card_data in self.demo_data.items():
            if card_key in query_lower:
                print(f"✓ Demo mode: Found '{card_key}' in local data")
                return card_data
        
        # Check if any card name is in the query
        for card_key in self.demo_data.keys():
            if card_key in query_lower or query_lower in card_key:
                print(f"✓ Demo mode: Matched '{card_key}' from query")
                return self.demo_data[card_key]
        
        print(f"✗ Demo mode: No match found for query '{query}'")
        print(f"  Available: {list(self.demo_data.keys())}")
        return {"data": [], "count": 0}
    
    async def search_cards(self, query: str) -> Dict[str, Any]:
        """
        Search for cards using the provided query.
        In demo mode, uses local JSON file. Otherwise, calls the API.
        
        Args:
            query: The API query string
            
        Returns:
            Dict containing the API response
        """
        if self.demo_mode:
            # Use demo data
            return self._search_in_demo_data(query)
        else:
            # Use real API
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
            has_error = "error" in response
            
            # Debug output
            if has_error:
                print(f"API Test Failed: {response.get('error')} - {response.get('message')}")
            else:
                print("API Test Passed: Successfully retrieved card data")
            
            return not has_error
        except Exception as e:
            print(f"API Test Exception: {str(e)}")
            return False


# Global instance
pokemon_service = PokemonService()