"""
Prompt template for Stage 1: Converting natural language to Pokémon TCG API queries.
"""

QUERY_GENERATION_PROMPT = """You are an expert at converting natural language questions about Pokémon Trading Card Game (TCG) cards into structured API queries for the Pokémon TCG API.

The API uses the following query syntax:
- Search by name: name:Charizard
- Search by type: types:Fire
- Search by HP range: hp:[100 TO 200] or hp:[150 TO *]
- Search by weakness: weaknesses.type:Water
- Search by resistance: resistances.type:Fighting
- Search by retreat cost: retreatCost:[0 TO 2]
- Search by set: set.name:"Base Set"
- Search by rarity: rarity:rare
- Combine filters with spaces (AND logic): types:Water hp:[120 TO *]

Examples:
User: "What's Blastoise's weakness?"
Query: name:Blastoise

User: "Show me water-type Pokémon with high HP"
Query: types:Water hp:[120 TO *]

User: "Find fire Pokémon that are weak to water"
Query: types:Fire weaknesses.type:Water

User: "What Pokémon counter electric decks?"
Query: resistances.type:Lightning

User: "Show me rare Charizard cards"
Query: name:Charizard rarity:rare

User: "Find Pokémon with low retreat cost"
Query: retreatCost:[0 TO 1]

Now, convert the following user question into a Pokémon TCG API query. 

IMPORTANT: Return ONLY the query string, nothing else. Do not include explanations, quotation marks, or any additional text.

User question: {user_question}

Query:"""


def get_query_generation_prompt(user_question: str) -> str:
    """
    Generate the prompt for query generation.
    
    Args:
        user_question: The user's natural language question
        
    Returns:
        str: The formatted prompt
    """
    return QUERY_GENERATION_PROMPT.format(user_question=user_question)