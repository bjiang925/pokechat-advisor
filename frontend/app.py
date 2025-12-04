"""
Streamlit Frontend - Main application interface for PokéChat Advisor.
"""
import streamlit as st
import requests
import os
from typing import List, Dict, Any

# Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="PokéChat Advisor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .card-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .card-image {
        max-width: 200px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-label {
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []


def send_message_to_backend(message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Send a message to the backend API.
    
    Args:
        message: The user's message
        history: Conversation history
        
    Returns:
        Dict containing the API response
    """
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/api/chat",
            json={
                "message": message,
                "conversation_history": history
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None


def display_card(card: Dict[str, Any]):
    """Display a single card with its information."""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if card.get("image_url"):
            st.image(card["image_url"], use_container_width=True)
    
    with col2:
        st.markdown(f"### {card['name']}")
        
        if card.get("hp"):
            st.markdown(f"**HP:** {card['hp']}")
        
        if card.get("types"):
            st.markdown(f"**Type(s):** {', '.join(card['types'])}")
        
        if card.get("weaknesses"):
            st.markdown(f"**Weaknesses:** {', '.join(card['weaknesses'])}")
        
        if card.get("resistances"):
            st.markdown(f"**Resistances:** {', '.join(card['resistances'])}")
        
        if card.get("retreat_cost") is not None:
            st.markdown(f"**Retreat Cost:** {card['retreat_cost']}")
        
        if card.get("set_name"):
            st.markdown(f"**Set:** {card['set_name']}")
        
        if card.get("rarity"):
            st.markdown(f"**Rarity:** {card['rarity']}")
        
        # Show abilities
        if card.get("abilities"):
            with st.expander("Abilities"):
                for ability in card["abilities"]:
                    st.markdown(f"- {ability}")
        
        # Show attacks
        if card.get("attacks"):
            with st.expander("Attacks"):
                for attack in card["attacks"]:
                    st.markdown(f"- {attack}")


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.title("⚡ PokéChat Advisor")
    st.markdown("*Your AI-powered Pokémon TCG assistant*")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        PokéChat Advisor helps you explore Pokémon Trading Card Game cards through natural conversation.
        
        **Try asking:**
        - "What's Charizard's weakness?"
        - "Show me water-type Pokémon with high HP"
        - "Compare Blastoise and Venusaur"
        - "What Pokémon counter electric decks?"
        """)
        
        st.markdown("---")
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Status**")
        
        # Check backend health
        try:
            health = requests.get(f"{BACKEND_API_URL}/health", timeout=5)
            if health.status_code == 200:
                health_data = health.json()
                st.success("✅ Backend Connected")
                st.info(f"Model: {'Loaded' if health_data.get('model_loaded') else 'Not Loaded'}")
                st.info(f"API: {'Accessible' if health_data.get('api_accessible') else 'Not Accessible'}")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Offline")
    
    # Chat interface
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display cards if present
            if message["role"] == "assistant" and "cards" in message:
                if message["cards"]:
                    st.markdown("---")
                    for card in message["cards"]:
                        display_card(card)
    
    # Chat input
    if prompt := st.chat_input("Ask me about Pokémon cards..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message_to_backend(
                    message=prompt,
                    history=st.session_state.conversation_history
                )
                
                if response:
                    # Display response
                    st.markdown(response["response"])
                    
                    # Display cards
                    if response.get("cards"):
                        st.markdown("---")
                        for card in response["cards"]:
                            display_card(card)
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": prompt
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response["response"]
                    })
                    
                    # Add to messages with cards
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "cards": response.get("cards", [])
                    })
                else:
                    error_msg = "Sorry, I encountered an error. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


if __name__ == "__main__":
    main()