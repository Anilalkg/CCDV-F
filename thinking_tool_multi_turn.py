import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

weather_tool = {
    "name": "get_weather",
    "description": "Get real-time weather parameters for a given location.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

# 1. TURN 1: Initial User Prompt
messages = [
    {
        "role": "user",
        "content": "What is the weather in Chicago right now?"
    }
]

print("--- Turn 1: Sending request with Adaptive Thinking enabled ---")

# Execute Turn 1 using model="claude-sonnet-5"
response_1 = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    tools=[weather_tool],
    messages=messages
)

# Inspect blocks returned in Turn 1
for block in response_1.content:
    if block.type == "thinking":
        print(f"\n[Turn 1 - Thinking Block]\n{block.thinking}")
    elif block.type == "tool_use":
        print(f"\n[Turn 1 - Tool Use Block]\nID: {block.id} | Tool: {block.name} | Input: {block.input}")

# ✅ CRITICAL RULE: Append the entire response.content block list back to history.
# This preserves thinking, redacted_thinking, and tool_use blocks intact.
messages.append({
    "role": "assistant",
    "content": response_1.content
})

# 2. TURN 2: Process Tool Result
tool_block = next((b for b in response_1.content if b.type == "tool_use"), None)

if tool_block:
    # Simulated execution response from external API
    mock_weather_data = json.dumps({
        "location": "Chicago, IL",
        "temperature": "68F",
        "condition": "Partly Cloudy",
        "humidity": "55%"
    })

    # Append tool execution result in user turn
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_block.id,  # Must match assistant tool_use id exactly
                "content": mock_weather_data
            }
        ]
    })

    print("\n--- Turn 2: Sending tool_result back with original thinking blocks preserved ---")

    # Execute Turn 2: Adaptive thinking remains enabled across turns
    response_2 = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[weather_tool],
        messages=messages
    )

    # Inspect final answer
    for block in response_2.content:
        if block.type == "thinking":
            print(f"\n[Turn 2 - Thinking Block]\n{block.thinking}")
        elif block.type == "text":
            print(f"\n[Turn 2 - Final Assistant Response]\n{block.text}")