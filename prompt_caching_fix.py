# filename: prompt_caching_fix.py

from datetime import datetime, timezone
import uuid
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# Simulated 60,000-token policy manual
POLICY_MANUAL = "Policy Manual Content... " * 5000  

def ask_policy_assistant(user_question: str, session_id: str) -> str:
    system_prompt = [
        {
            "type": "text",
            "text": POLICY_MANUAL,
            "cache_control": {"type": "ephemeral"}  # Static prefix cached
        }
    ]

    utc_timestamp = datetime.now(timezone.utc).isoformat()
    
    messages = [
        {
            "role": "user",
            "content": (
                f"[Context Metadata]\n"
                f"Current UTC time: {utc_timestamp}\n"
                f"Session ID: {session_id}\n\n"
                f"Question: {user_question}"
            )
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    )

    # Telemetry logging to prove cache hits vs creation
    usage = response.usage
    cache_created = getattr(usage, "cache_creation_input_tokens", 0)
    cache_read = getattr(usage, "cache_read_input_tokens", 0)
    
    print(f"Cache Creation Tokens: {cache_created}")
    print(f"Cache Read Tokens:     {cache_read}")

    # FIX: Safely extract text from text blocks, ignoring ThinkingBlocks
    text_outputs = []
    for block in response.content:
        if block.type == "text":
            text_outputs.append(block.text)
            
    return "\n".join(text_outputs)

if __name__ == "__main__":
    test_session = str(uuid.uuid4())
    
    print("--- Request 1 (Cache Write Expected) ---")
    answer1 = ask_policy_assistant("What is the reimbursement limit?", session_id=test_session)
    print(f"Response: {answer1[:100]}...\n")
    
    print("--- Request 2 (Cache Read Expected) ---")
    answer2 = ask_policy_assistant("What is the remote work policy?", session_id=test_session)
    print(f"Response: {answer2[:100]}...\n")