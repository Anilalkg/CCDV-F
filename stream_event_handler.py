# filename: stream_event_handler.py

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def handle_document_generation_stream(prompt: str):
    # Track final state variables
    stop_reason = None
    output_tokens = 0

    # Execute raw streaming request
    with client.messages.create(
        model="claude-sonnet-5",  # Configured to claude-sonnet-5
        max_tokens=100,  # Small token limit to test max_tokens cutoff
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ) as stream:
        for event in stream:
            # 1. Text deltas are emitted in content_block_delta events
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    # Stream text chunk to console / browser connection
                    print(event.delta.text, end="", flush=True)

            # 2. CCDV-F Core Topic: message_delta contains stop_reason and output token usage
            elif event.type == "message_delta":
                # Extract why generation stopped ("end_turn", "max_tokens", "stop_sequence")
                stop_reason = event.delta.stop_reason
                
                # event.usage contains the cumulative output token count
                if hasattr(event, "usage") and event.usage:
                    output_tokens = event.usage.output_tokens

    print("\n" + "=" * 50)
    print("Stream Completed.")
    print(f"[BILLING LOG] Cumulative Output Tokens: {output_tokens}")

    # 3. Handle UI trigger based on stop_reason
    if stop_reason == "max_tokens":
        print("[UI STATE] Response truncated by max_tokens -> Displaying 'Continue generating' button.")
    else:
        print(f"[UI STATE] Generation finished naturally with stop_reason: '{stop_reason}'.")

if __name__ == "__main__":
    prompt_text = "Draft a comprehensive 1,000-word software architecture specification for a microservices platform."
    handle_document_generation_stream(prompt_text)