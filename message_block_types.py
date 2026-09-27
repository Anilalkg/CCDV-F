import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Define a tool for the assistant to request
weather_tool = {
    "name": "get_weather",
    "description": "Fetch current weather parameters for a given location.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

# 1. TURN 1: User sends text query
conversation_history = [
    {
        "role": "user",
        # User Content Types: 'text', 'image', 'document'
        "content": [
            {
                "type": "text",
                "text": "Check the weather in Chicago, and format your output clearly."
            }
        ]
    }
]

print("--- Requesting Turn 1 (Assistant Output) ---")

# Execute initial message call
response_1 = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=2048,
    tools=[weather_tool],
    messages=conversation_history
)

# 2. APPEND ASSISTANT TURN TO HISTORY
# Assistant Content Types: 'text', 'thinking', 'redacted_thinking', 'tool_use'
# Append the exact list of content blocks emitted by the model
conversation_history.append({
    "role": "assistant",
    "content": response_1.content
})

# Inspect generated assistant blocks
tool_use_id = None
tool_name = None
tool_args = None

for block in response_1.content:
    if block.type == "thinking":
        print(f"[Assistant Block: thinking]\n{block.thinking}\n")
    elif block.type == "text":
        print(f"[Assistant Block: text]\n{block.text}\n")
    elif block.type == "tool_use":
        tool_use_id = block.id
        tool_name = block.name
        tool_args = block.input
        print(f"[Assistant Block: tool_use]\nID: {tool_use_id}\nName: {tool_name}\nArgs: {tool_args}\n")

# 3. TURN 2: User provides tool execution output
# User Content Type: 'tool_result' (MUST match tool_use_id from previous assistant turn)
if tool_use_id:
    # Simulated execution result from tool
    mock_tool_output = json.dumps({"temperature": "68F", "condition": "Partly Cloudy"})

    conversation_history.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,  # Strict byte-for-byte match
                "content": mock_tool_output,
                "is_error": False
            }
        ]
    })

    print("--- Requesting Turn 2 (Final Answer after Tool Execution) ---")
    
    response_2 = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=[weather_tool],
        messages=conversation_history
    )

    # Extract final text block
    for block in response_2.content:
        if block.type == "text":
            print(f"[Final Assistant Response]\n{block.text}")