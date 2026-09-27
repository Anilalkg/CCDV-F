# prompt_caching_1hr_ttl.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Prepare a 40,000-token static document
LARGE_DOCUMENT_CONTEXT = (
    "Enterprise Compliance, Regulatory Framework, and Risk Governance Guidelines...\n"
    * 3000  # ~40k tokens
)

def execute_hourly_cached_request():
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": LARGE_DOCUMENT_CONTEXT,
                # =========================================================
                # OPTION 1: 1-Hour TTL Configuration
                # Billed at 2.0x base input price on initial cache write.
                # Entries survive 20-minute idle gaps throughout the workday.
                # =========================================================
                "cache_control": {
                    "type": "ephemeral",
                    "ttl": "1h"  # Overrides default 5-minute TTL to 1 hour
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": "Summarize section 4 regarding compliance audits."
            }
        ]
    )

    print("--- Usage Summary ---")
    print(f"Input Tokens (Uncached):        {response.usage.input_tokens}")
    print(f"Cache Creation Tokens (Write):  {response.usage.cache_creation_input_tokens}")
    print(f"Cache Read Tokens (Hit):        {response.usage.cache_read_input_tokens}")

if __name__ == "__main__":
    execute_hourly_cached_request()