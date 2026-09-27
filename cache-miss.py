from datetime import datetime, timezone
import anthropic
from dotenv import load_dotenv
from rich import print as rprint

# 1. ALWAYS load dotenv BEFORE instantiating the Anthropic client
load_dotenv()

# Instantiates client using os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic()

# Large static context (~20k tokens in production)
STATIC_SYSTEM_PROMPT = """You are the Lead Support Assistant for ACME Cloud Services.
Refer to the following standard operating procedures (SOP) for all answers:
[1. AUTHENTICATION TROUBLESHOOTING...]
[2. RATE LIMIT HANDLING...]
[3. ESCALATION PATHWAYS...]"""

# Dynamic timestamp generated per execution
dynamic_timestamp = f"Current time: {datetime.now(timezone.utc).isoformat()}"

try:
    # ❌ INCORRECT PATTERN: Mutating timestamp inside the system block invalidates the cache
    response = client.messages.create(
        # Note: Swap to a live active model (e.g., claude-3-7-sonnet-latest) for local testing
        model="claude-sonnet-5",
        max_tokens=1024,
        thinking={"type": "disabled"},
        system=[
            {
                "type": "text",
                "text": f"{STATIC_SYSTEM_PROMPT}\n\nSystem Context: {dynamic_timestamp}",
                # BUSTED: The dynamic_timestamp mutates the text sequence, causing 0 cache hits!
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[
            {"role": "user", "content": "How do I troubleshoot a 401 Unauthorized error?"}
        ]
    )

    rprint({
        "input_tokens": response.usage.input_tokens,
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0)
    })

except anthropic.NotFoundError:
    print("\n[SDK Verified] Authentication succeeded! (Failed as expected on model name 'claude-sonnet-5')")
except Exception as e:
    print(f"Execution Error: {e}")