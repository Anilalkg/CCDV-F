# filename: streaming_tool_use_fix.py

import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# Sample mock tool definition
TOOLS = [
    {
        "name": "get_stock_price",
        "description": "Get current stock price for a given ticker symbol.",
        "input_schema": {
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"]
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict):
    """Executes tool safely after complete JSON object assembly."""
    print(f"\n✅ [EXECUTING TOOL]: '{tool_name}' with full input parameters: {tool_input}")

def handle_tool_use_stream_option_b():
    """Demonstrates Option B:
    1. Tracks and concatenates partial_json fragments by content block index.
    2. Parses full JSON string and executes tool strictly on content_block_stop.
    """
    # Dictionary to buffer partial JSON strings by content block index
    # Format: { index: {"name": str, "tool_id": str, "json_buffer": str} }
    tool_block_buffers = {}

    print("--- Starting Messages Streaming Request ---")
    
    stream = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        tools=TOOLS,
        messages=[{"role": "user", "content": "What is the stock price of AAPL?"}],
        stream=True
    )

    for event in stream:
        # Event 1: New content block starts (Identify if it's a tool_use block)
        if event.type == "content_block_start":
            block = event.content_block
            if block.type == "tool_use":
                tool_block_buffers[event.index] = {
                    "name": block.name,
                    "id": block.id,
                    "json_buffer": ""
                }
                print(f"[EVENT] content_block_start (Index {event.index}): Initialized tool '{block.name}'")

        # Event 2: JSON Delta Fragment arrives
        elif event.type == "content_block_delta":
            if event.delta.type == "input_json_delta":
                fragment = event.delta.partial_json
                # Concatenate partial string fragment into index buffer
                tool_block_buffers[event.index]["json_buffer"] += fragment
                print(f"  └─ Accumulating fragment into index {event.index}: {repr(fragment)}")

        # Event 3: Content Block Stop (Triggers full JSON parsing & execution)
        elif event.type == "content_block_stop":
            idx = event.index
            if idx in tool_block_buffers:
                tool_info = tool_block_buffers[idx]
                full_json_str = tool_info["json_buffer"]
                
                print(f"[EVENT] content_block_stop (Index {idx}): Block finished streaming.")
                print(f"  └─ Full Concatenated JSON Payload: {full_json_str}")
                
                # Parse complete accumulated JSON payload safely
                try:
                    parsed_input = json.loads(full_json_str) if full_json_str else {}
                    execute_tool(tool_info["name"], parsed_input)
                except json.JSONDecodeError as err:
                    print(f"❌ Failed to parse JSON on index {idx}: {err}")

if __name__ == "__main__":
    handle_tool_use_stream_option_b()