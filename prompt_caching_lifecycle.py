# prompt_caching_lifecycle.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. STATIC PREFIX (> 1,024 tokens)
# System prompt + shared reference document that stays static across turns
STATIC_REFERENCE_DOC = [
    {
        "type": "text",
        "text": "Enterprise Policy Guidelines & Reference Documentation...\n" + ("Section Text... " * 300),
        # Single cache_control breakpoint immediately after the static reference document
        "cache_control": {"type": "ephemeral"}
    }
]

def demonstrate_cache_lifecycle():
    # =====================================================================
    # TURN 1: FIRST REQUEST (Writes prefix to cache)
    # Expected: cache_creation_input_tokens > 0 | cache_read_input_tokens = 0
    # =====================================================================
    response_1 = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        system=STATIC_REFERENCE_DOC,
        messages=[{"role": "user", "content": "Turn 1: What are the primary rules?"}]
    )

    print("=== Request 1 (Cache Creation / Write) ===")
    print(f"Uncached Input Tokens:         {response_1.usage.input_tokens}")
    print(f"Cache Creation Tokens (Write): {response_1.usage.cache_creation_input_tokens}")  # > 1024
    print(f"Cache Read Tokens (Hit):       {response_1.usage.cache_read_input_tokens}")      # 0
    print("Assessment: NOT a bug! The first request incurs a cache write fee to create the entry.\n")

    # =====================================================================
    # TURN 2: SECOND REQUEST (Reads from the warm cache)
    # Expected: cache_creation_input_tokens = 0 | cache_read_input_tokens > 0
    # =====================================================================
    response_2 = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        system=STATIC_REFERENCE_DOC,  # Same identical prefix up to cache_control breakpoint
        messages=[{"role": "user", "content": "Turn 2: Summarize section 3."}]  # Dynamic turn
    )

    print("=== Request 2 (Cache Read / Hit) ===")
    print(f"Uncached Input Tokens (Turn 2 Msg): {response_2.usage.input_tokens}")
    print(f"Cache Creation Tokens (Write):      {response_2.usage.cache_creation_input_tokens}")  # 0
    print(f"Cache Read Tokens (Hit):            {response_2.usage.cache_read_input_tokens}")      # > 1024


if __name__ == "__main__":
    demonstrate_cache_lifecycle()