# cacheable_prompt_structure.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Static System Prompt (Placed first to enable prefix caching)
SYSTEM_PROMPT = [
    {
        "type": "text",
        "text": "You are a professional contract analysis assistant. Always adhere strictly to the provided document.",
        "cache_control": {"type": "ephemeral"}  # First cache breakpoint
    }
]

# 2. Static Tool Definitions (Placed in system/tools layer)
TOOLS = [
    {
        "name": "flag_risk_clause",
        "description": "Flags a high-risk clause for human legal review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {"type": "string"},
                "risk_reason": {"type": "string"}
            },
            "required": ["section", "risk_reason"]
        }
    }
]

# Simulated 30k token static reference document
STATIC_REFERENCE_DOC = "<document>\n[30,000 tokens of contract context here]\n</document>"

def query_contract_with_cache(user_query: str):
    """
    Places bulky reference document BEFORE the variable user query 
    to optimize both attention quality and cache hit rates.
    """
    messages = [
        {
            "role": "user",
            "content": [
                # Bulky reference document comes FIRST (Cacheable prefix)
                {
                    "type": "text",
                    "text": STATIC_REFERENCE_DOC,
                    "cache_control": {"type": "ephemeral"}  # Second cache breakpoint
                },
                # Variable user request comes LAST (Optimal attention & adherence)
                {
                    "type": "text",
                    "text": f"Instruction: {user_query}"
                }
            ]
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages
    )

    # Safely extract text blocks while handling potential thinking blocks
    response_text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    # Output cache performance metrics
    usage = response.usage
    print(f"Cache Creation Tokens: {getattr(usage, 'cache_creation_input_tokens', 0)}")
    print(f"Cache Read Tokens:     {getattr(usage, 'cache_read_input_tokens', 0)}")
    print(f"Response:\n{response_text}")

if __name__ == "__main__":
    query_contract_with_cache("Extract all indemnity obligations and liabilities.")