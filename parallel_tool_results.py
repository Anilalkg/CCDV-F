import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

weather_tool = {
    "name": "get_weather",
    "description": "Get real-time weather details for a specific location.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

# 1. Base User Prompt triggering multiple tool calls
messages = [
    {
        "role": "user",
        "content": "What is the weather in Chicago and Boston right now?"
    }
]

# 2. DEFINE response_1: Execute initial call to get assistant output
response_1 = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=2048,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    tools=[weather_tool],
    messages=messages
)

# 3. Append assistant response to history
messages.append({
    "role": "assistant",
    "content": response_1.content
})

# 4. Extract all requested tool_use blocks from response_1
tool_calls = [b for b in response_1.content if b.type == "tool_use"]

# 5. Build tool_result blocks for ALL calls returned in turn 1
tool_results = []
for tool_call in tool_calls:
    location = tool_call.input.get("location", "Unknown")
    
    # Mock data execution
    mock_data = json.dumps({
        "location": location,
        "temp": "70F",
        "condition": "Clear"
    })
    
    tool_results.append({
        "type": "tool_result",
        "tool_use_id": tool_call.id,  # Byte-for-byte matching ID
        "content": mock_data,
        "is_error": False
    })

# 6. Append all tool results in a SINGLE user turn
messages.append({
    "role": "user",
    "content": tool_results
})

# 7. Request Turn 2 for final synthesis
response_2 = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=2048,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    tools=[weather_tool],
    messages=messages
)

for block in response_2.content:
    if block.type == "text":
        print(f"\nFinal Answer:\n{block.text}")