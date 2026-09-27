import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Define JSON Schema via Tool Definition
extract_schema = {
    "name": "output_extracted_entities",
    "description": "Output extracted entities directly in structured schema.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "role": {"type": "string"}
        },
        "required": ["name", "role"]
    }
}

try:
    response = client.messages.create(
        # model="claude-3-7-sonnet-latest",
        model= "claude-sonnet-5",
        max_tokens=1024,
        tools=[extract_schema],
        # FORCED TOOL CHOICE: Forces Claude to execute this specific schema directly
        tool_choice={"type": "tool", "name": "output_extracted_entities"},
        messages=[
            {
                "role": "user",
                "content": "Extract name and role from: 'Alice Smith joined as Chief Architect.'"
            }
        ]
    )

    # Extract tool input directly (already parsed as a Python dict!)
    tool_block = next(b for b in response.content if b.type == "tool_use")
    extracted_data = tool_block.input

    print(json.dumps(extracted_data, indent=2))

except anthropic.APIError as e:
    print(f"API Error: {e}")