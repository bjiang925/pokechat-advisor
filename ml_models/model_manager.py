"""
Model Manager - Singleton pattern for loading and managing the Qwen3-0.6B model.
This ensures the model is loaded only once at startup, saving memory and time.
"""
import os
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class ModelManager:
    """Singleton class to manage the LLM model."""
    
    _instance: Optional['ModelManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the model manager (only once)."""
        if not ModelManager._initialized:
            self.model_name = os.getenv("MODEL_NAME", "Qwen/Qwen3-0.6B")
            self.device_map = os.getenv("DEVICE_MAP", "auto")
            self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))
            
            self.tokenizer: Optional[AutoTokenizer] = None
            self.model: Optional[AutoModelForCausalLM] = None
            
            ModelManager._initialized = True
    
    def load_model(self):
        """Load the model and tokenizer into memory."""
        if self.model is not None:
            print("Model already loaded.")
            return
        
        print(f"Loading model: {self.model_name}...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map=self.device_map
        )
        
        print(f"Model loaded successfully on device: {self.model.device}")
    
    def generate_response(
        self, 
        prompt: str, 
        enable_thinking: bool = True,
        max_new_tokens: Optional[int] = None
    ) -> tuple[str, str]:
        """
        Generate a response from the model.
        
        Args:
            prompt: The user prompt
            enable_thinking: Whether to enable thinking mode
            max_new_tokens: Maximum new tokens to generate
            
        Returns:
            tuple: (thinking_content, content)
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Apply chat template
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking
        )
        
        # Tokenize
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        # Generate
        tokens_to_generate = max_new_tokens or self.max_new_tokens
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=tokens_to_generate
        )
        
        # Extract output
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        
        # Parse thinking content
        try:
            # Find </think> token (151668)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0
        
        thinking_content = self.tokenizer.decode(
            output_ids[:index], 
            skip_special_tokens=True
        ).strip("\n")
        
        content = self.tokenizer.decode(
            output_ids[index:], 
            skip_special_tokens=True
        ).strip("\n")
        
        return thinking_content, content
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None and self.tokenizer is not None


# Global instance
model_manager = ModelManager()