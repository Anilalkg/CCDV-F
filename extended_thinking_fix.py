# filename: extended_thinking_fix.py

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def render_ui(message: str):
    """Simulates UI rendering layer."""
    print(f"\n[UI RENDERED OUTPUT]:\n{message}")

def safe_render_response(resp):
    """Evaluates Option A principles:
    1. Filters content blocks by type == 'text' rather than assuming position index [0].
    2. Checks stop_reason to handle max_tokens truncation correctly.
    """
    # Check stop_reason to detect output truncation (max_tokens hit)
    if resp.stop_reason == "max_tokens":
        print("⚠️ WARNING: Response was truncated because max_tokens budget was reached.")

    # Filter by block.type == "text" (Do NOT assume index [0])
    text_blocks = [block.text for block in resp.content if block.type == "text"]

    if text_blocks:
        # Join all valid text blocks and render to UI
        final_answer = "\n".join(text_blocks)
        render_ui(final_answer)
    else:
        # Handle edge case where thinking consumed entire budget before text generation
        render_ui("[No text generated. Thinking budget exceeded max_tokens limit.]")

def run_extended_thinking_demo():
    print("--- Sending Request with Extended Thinking Enabled ---")
    
    # Adaptive thinking schema (budget_tokens removed completely)
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        messages=[
            {"role": "user", "content": "How many 'r's are in the word 'strawberry'?"}
        ]
    )

    print(f"Total Content Blocks Received: {len(resp.content)}")
    for idx, block in enumerate(resp.content):
        print(f"  - Block [{idx}] Type: '{block.type}'")

    # Pass API response payload to the safe handler
    safe_render_response(resp)

if __name__ == "__main__":
    run_extended_thinking_demo()