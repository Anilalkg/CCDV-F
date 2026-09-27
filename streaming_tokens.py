# streaming_tokens.py

import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def stream_claude_response(prompt: str):
    print("Claude: ", end="", flush=True)

    # =====================================================================
    # STREAMING INTEGRATION: Enables Server-Sent Events (SSE)
    # =====================================================================
    # Using client.messages.stream() sets "stream": true under the hood
    # and opens an SSE stream to consume text delta events token by token.
    with client.messages.stream(
        model="claude-sonnet-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        
        # Iterate over text deltas as Server-Sent Events arrive from the API
        for text_delta in stream.text_stream:
            # Print each token chunk immediately without adding newlines
            sys.stdout.write(text_delta)
            sys.stdout.flush()

    print("\n")

if __name__ == "__main__":
    stream_claude_response("Write a brief 3-sentence explanation of Server-Sent Events (SSE).")