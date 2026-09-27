import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

weather_tool = {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

messages = [{"role": "user", "content": "What is the weather in Chicago?"}]

# Initialize tracking accumulators
current_tool_id = None
current_tool_name = None
json_accumulator = ""

# Stream the response
with client.messages.stream(
    model="claude-sonnet-5",
    max_tokens=1024,
    thinking={"type": "disabled"},
    tools=[weather_tool],
    messages=messages
) as stream:
    for event in stream:
        # 1. TOOL START: Capture the tool ID and tool Name
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                current_tool_id = event.content_block.id
                current_tool_name = event.content_block.name
                json_accumulator = ""  # Reset accumulator
                print(f"\n[Tool Use Detected] Name: {current_tool_name} | ID: {current_tool_id}")

        # 2. TOOL DELTA: Append partial JSON chunks
        elif event.type == "content_block_delta":
            if event.delta.type == "input_json_delta":
                partial_chunk = event.delta.partial_json
                json_accumulator += partial_chunk
                print(f"Received JSON chunk: {partial_chunk}")
                # NOTE: Attempting json.loads(json_accumulator) HERE will fail with JSONDecodeError!

        # 3. TOOL STOP: The complete JSON string is now ready to parse safely
        elif event.type == "content_block_stop":
            if current_tool_id:
                try:
                    tool_args = json.loads(json_accumulator)
                    print(f"\n[Tool Block Complete] Parsed Arguments: {tool_args}")
                except json.JSONDecodeError as e:
                    print(f"JSON Parsing Error: {e}")