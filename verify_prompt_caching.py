# verify_prompt_caching.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Construct a large static context block (Exceeding 1,024 tokens)
# A typical English word is ~1.3 tokens. ~800 words easily satisfies >1024 tokens.
large_documentation_block = """
Enterprise Architecture Guidelines for Cloud Migration and Service Mesh Deployment:
""" + ("This section covers mandatory security boundaries, TLS termination, and mTLS protocols. " * 80)

def test_prompt_cache():
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": large_documentation_block,
                # Explicitly set cache control breakpoint
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[
            {
                "role": "user",
                "content": "Summarize the TLS requirements mentioned in the architecture guide."
            }
        ]
    )

    print("--- Usage Statistics ---")
    print(f"Input Tokens:                  {response.usage.input_tokens}")
    print(f"Cache Creation Input Tokens:   {response.usage.cache_creation_input_tokens}")
    print(f"Cache Read Input Tokens:       {response.usage.cache_read_input_tokens}")

if __name__ == "__main__":
    test_prompt_cache()