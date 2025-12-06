"""
Pokémon TCG API Client - Handles all interactions with the Pokémon TCG API.
"""
import os
from typing import Optional, Dict, Any
import httpx
from httpx import AsyncClient


class PokemonTCGAPIClient:
    """Client for interacting with the Pokémon TCG API."""
    
    def __init__(self):
        """Initialize the API client."""
        self.base_url = os.getenv("POKEMON_TCG_API_URL", "https://api.pokemontcg.io/v2")
        self.api_key = os.getenv("POKEMON_TCG_API_KEY", "")
        
        # Debug: Print API key status (first 4 chars only for security)
        if self.api_key and len(self.api_key) > 4:
            print(f"API Key loaded: {self.api_key[:4]}...")
        else:
            print("WARNING: No API key loaded. Rate limits will apply.")
        
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key to headers if available
        if self.api_key and self.api_key != "your_api_key_here":
            self.headers["X-Api-Key"] = self.api_key
            print("API Key added to headers")
    
    async def search_cards(
        self, 
        query: str, 
        page_size: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for cards using a query string.
        
        Args:
            query: The search query (e.g., "name:Charizard types:Fire")
            page_size: Number of results per page
            page: Page number
            
        Returns:
            Dict containing the API response with card data
        """
        endpoint = f"{self.base_url}/cards"
        
        params = {
            "q": query,
            "pageSize": page_size,
            "page": page
        }
        
        print(f"Calling API: {endpoint}")
        print(f"Query: {query}")
        print(f"Headers: {self.headers}")
        
        try:
            async with AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params=params
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                data = response.json()
                print(f"Response data keys: {data.keys() if data else 'None'}")
                return data
        
        except httpx.HTTPStatusError as e:
            error_detail = {
                "error": f"HTTP error occurred: {e.response.status_code}",
                "message": str(e),
                "response_text": e.response.text[:500]
            }
            print(f"HTTPStatusError: {error_detail}")
            return error_detail
        except httpx.RequestError as e:
            error_detail = {
                "error": "Request error occurred",
                "message": str(e),
                "type": type(e).__name__
            }
            print(f"RequestError: {error_detail}")
            return error_detail
        except Exception as e:
            error_detail = {
                "error": "Unexpected error occurred",
                "message": str(e),
                "type": type(e).__name__
            }
            print(f"Exception: {error_detail}")
            return error_detail
    
    async def get_card_by_id(self, card_id: str) -> Dict[str, Any]:
        """
        Get a specific card by its ID.
        
        Args:
            card_id: The unique card ID
            
        Returns:
            Dict containing the card data
        """
        endpoint = f"{self.base_url}/cards/{card_id}"
        
        try:
            async with AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error occurred: {e.response.status_code}",
                "message": str(e)
            }
        except httpx.RequestError as e:
            return {
                "error": "Request error occurred",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Unexpected error occurred",
                "message": str(e)
            }
    
    def format_cards_for_llm(self, api_response: Dict[str, Any]) -> str:
        """
        Format the API response into a readable string for the LLM.
        
        Args:
            api_response: The raw API response
            
        Returns:
            Formatted string containing card information
        """
        if "error" in api_response:
            return f"Error: {api_response.get('message', 'Unknown error')}"
        
        if "data" not in api_response or not api_response["data"]:
            return "No cards found matching the query."
        
        cards = api_response["data"]
        formatted_cards = []
        
        for card in cards[:5]:  # Limit to top 5 results
            card_info = {
                "name": card.get("name", "Unknown"),
                "id": card.get("id", "Unknown"),
                "supertype": card.get("supertype", "Unknown"),
                "subtypes": ", ".join(card.get("subtypes", [])),
                "hp": card.get("hp", "N/A"),
                "types": ", ".join(card.get("types", [])),
                "weaknesses": [
                    f"{w.get('type', 'Unknown')} ({w.get('value', 'N/A')})" 
                    for w in card.get("weaknesses", [])
                ],
                "resistances": [
                    f"{r.get('type', 'Unknown')} ({r.get('value', 'N/A')})" 
                    for r in card.get("resistances", [])
                ],
                "retreat_cost": len(card.get("retreatCost", [])),
                "set": card.get("set", {}).get("name", "Unknown"),
                "rarity": card.get("rarity", "Unknown"),
                "image_url": card.get("images", {}).get("small", ""),
                "abilities": [
                    f"{a.get('name', 'Unknown')}: {a.get('text', 'No description')}"
                    for a in card.get("abilities", [])
                ],
                "attacks": [
                    f"{a.get('name', 'Unknown')} ({', '.join(a.get('cost', []))}): {a.get('damage', '0')} - {a.get('text', 'No description')}"
                    for a in card.get("attacks", [])
                ]
            }
            
            formatted = f"""
Card: {card_info['name']}
ID: {card_info['id']}
Type: {card_info['supertype']} - {card_info['subtypes']}
HP: {card_info['hp']}
Types: {card_info['types']}
Weaknesses: {', '.join(card_info['weaknesses']) if card_info['weaknesses'] else 'None'}
Resistances: {', '.join(card_info['resistances']) if card_info['resistances'] else 'None'}
Retreat Cost: {card_info['retreat_cost']}
Set: {card_info['set']}
Rarity: {card_info['rarity']}
Image URL: {card_info['image_url']}
Abilities: {'; '.join(card_info['abilities']) if card_info['abilities'] else 'None'}
Attacks: {'; '.join(card_info['attacks']) if card_info['attacks'] else 'None'}
"""
            formatted_cards.append(formatted.strip())
        
        return "\n\n---\n\n".join(formatted_cards)


# Global instance
pokemon_api_client = PokemonTCGAPIClient()