# optimized_prompt_caching.py

import datetime
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. STATIC PRODUCT MANUAL (~30,000 tokens)
# Loaded once in memory across application requests
LARGE_PRODUCT_MANUAL = (
    "Product Manual & Architecture Reference Guide v4.2...\n"
    + ("Section Details and Technical Specifications... " * 2500)
)

# 2. STATIC TOOL DEFINITIONS
TOOLS = [
    {
        "name": "lookup_support_ticket",
        "description": "Looks up support history for an account.",
        "input_schema": {
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"]
        }
    }
]

def query_product_assistant(
    user_question: str,
    user_tier: str,
    account_id: str
):
    # =========================================================================
    # OPTIMIZED STRUCTURE: Static content blocks first, dynamic content last
    # =========================================================================
    system_blocks = [
        # Static Block 1: System Instructions
        {
            "type": "text",
            "text": "You are an enterprise technical support assistant. Answer user questions strictly using the provided product manual."
        },
        # Static Block 2: 30,000-Token Product Manual with Breakpoint
        {
            "type": "text",
            "text": LARGE_PRODUCT_MANUAL,
            # Single breakpoint immediately following the last static element
            "cache_control": {"type": "ephemeral"}
        }
    ]

    # Dynamic elements are placed in the user turn message AFTER the static prefix
    timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    user_content = [
        {
            "type": "text",
            # Dynamic context (~30 tokens) placed below the cache breakpoint
            "text": f"[Request Context | Time: {timestamp_str} | Account Tier: {user_tier} | Account ID: {account_id}]\n\n"
                    f"User Question: {user_question}"
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        system=system_blocks,
        tools=TOOLS,
        messages=[{"role": "user", "content": user_content}]
    )

    # Output Token Accounting
    print("--- Token Usage Metrics ---")
    print(f"Uncached Input Tokens (Dynamic): {response.usage.input_tokens}")
    print(f"Cache Write Tokens (Turn 1):      {response.usage.cache_creation_input_tokens}")
    print(f"Cache Read Tokens (Hits):         {response.usage.cache_read_input_tokens}")
    
    return response.content[0].text


if __name__ == "__main__":
    # Request 1: Creates the cache entry for the 30k manual
    print("=== Execution 1 ===")
    query_product_assistant(
        user_question="How do I reset the admin password?",
        user_tier="Enterprise",
        account_id="ACC-9912"
    )

    # Request 2: Hits the warm cache despite different timestamp/user tier
    print("\n=== Execution 2 (10 seconds later, different user context) ===")
    query_product_assistant(
        user_question="What is the maximum file upload size?",
        user_tier="Standard",
        account_id="ACC-4410"
    )