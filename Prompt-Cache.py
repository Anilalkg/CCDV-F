import anthropic
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()
client = anthropic.Anthropic()

LARGE_SYSTEM_PROMPT = """
You are the Technical Support Assistant for ACME Cloud Services.
Refer to the following standard operating procedures (SOP) for all answers:

1. AUTHENTICATION TROUBLESHOOTING:
   - Verify token expiration before resetting credentials.
   - For 401 Unauthorized, check header authorization format.
   - For 403 Forbidden, check IAM role policies.

2. RATE LIMIT HANDLING:
   - For 429 Too Many Requests, implement exponential backoff with jitter.
"""

def make_cached_request(user_query: str, ttl: str = "5m"):
    return client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        thinking={"type": "disabled"},
        system=[
            {
                "type": "text",
                "text": LARGE_SYSTEM_PROMPT,
                "cache_control": {
                    "type": "ephemeral",
                    "ttl": ttl  # Options: "5m" or "1h"
                }
            }
        ],
        messages=[
            {"role": "user", "content": user_query}
        ]
    )

# Turn 1: Cache Write
res1 = make_cached_request("How do I handle a 429 error?")
rprint({
    "input_tokens": res1.usage.input_tokens,
    "cache_creation_input_tokens": getattr(res1.usage, "cache_creation_input_tokens", 0),
    "cache_read_input_tokens": getattr(res1.usage, "cache_read_input_tokens", 0)
})

# Turn 2: Cache Read
res2 = make_cached_request("What should I check for a 401 error?")
rprint({
    "input_tokens": res2.usage.input_tokens,
    "cache_creation_input_tokens": getattr(res2.usage, "cache_creation_input_tokens", 0),
    "cache_read_input_tokens": getattr(res2.usage, "cache_read_input_tokens", 0)
})