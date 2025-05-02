import json
import os

from anthropic import AnthropicVertex

from coding_agent.config import ANTHROPIC_REGION, ANTHROPIC_PROJECT_ID, \
    ANTHROPIC_MODEL, CACHE_FILE
from coding_agent.logger import setup_logger

# Configure logging
logger = setup_logger("llm_calls")

# Simple cache configuration
cache_file = CACHE_FILE

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt: str, use_cache: bool = True) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")
    
    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")
        
        # Return from cache if exists
        if prompt in cache:
            logger.info(f"Cache hit for prompt: {prompt[:50]}...")
            return cache[prompt]
    
    # Call the LLM if not in cache or cache disabled
    client = AnthropicVertex(
        region=ANTHROPIC_REGION,
        project_id=ANTHROPIC_PROJECT_ID
    )
    response = client.messages.create(
        max_tokens=20000,
        thinking={
            "type": "enabled",
            "budget_tokens": 16000
        },
        messages=[{"role": "user", "content": prompt}],
        model=ANTHROPIC_MODEL
    )
    response_text = response.content[1].text
    
    # Log the response
    logger.info(f"RESPONSE: {response_text}")
    
    # Update cache if enabled
    if use_cache:
        # Load cache again to avoid overwrites
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            except:
                pass
        
        # Add to cache and save
        cache[prompt] = response_text
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache, f)
            logger.info(f"Added to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    return response_text

def clear_cache() -> None:
    """Clear the cache file if it exists."""
    if os.path.exists(cache_file):
        os.remove(cache_file)
        logger.info("Cache cleared")

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    
    # First call - should hit the API
    print("Making first call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
    
    # Second call - should hit cache
    print("\nMaking second call with same prompt...")
    response2 = call_llm(test_prompt, use_cache=True)
    print(f"Response: {response2}")
