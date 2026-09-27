import json
import anthropic
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()
client = anthropic.Anthropic()

response = client.messages.create(
    # model="claude-3-7-sonnet-latest",
    model="claude-sonnet-5",
    max_tokens=50,  # Deliberately low token limit to force truncation
    thinking={"type": "disabled"},  # Disables ThinkingBlock so content[0] is guaranteed to be a TextBlock
    system="You are a helpful assistant that outputs JSON objects.",
    messages=[
        {"role": "user", "content": "Provide a detailed JSON array listing 10 major world cities with populations."}
    ]
)

rprint(response.model_dump())

# 1. DIRECT CHECK: Inspect stop_reason before attempting JSON parsing
if response.stop_reason == "max_tokens":
    print(f"Truncation Warning: Output stopped early due to max_tokens limit!")
    print(f"Raw incomplete output:\n{response.content[0].text}\n")
    # Action: Increase max_tokens or prompt for shorter response instead of parsing broken JSON

elif response.stop_reason == "end_turn":
    # Safe to attempt JSON parsing
    try:
        data = json.loads(response.content[0].text)
        print("Successfully parsed JSON:", data)
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")