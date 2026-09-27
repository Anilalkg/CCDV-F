# pretty_print_thinking.py

import anthropic
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

system_prompt = "You are a senior software architect."

messages = [
    {
        "role": "user",
        "content": "How should I design a high-throughput, low-latency rate limiting service for an API gateway?"
    }
]

# Enable Extended Thinking via the thinking parameter
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=4096,  # Must be larger than budget_tokens
    thinking={
        "type": "enabled",
        "budget_tokens": 2048  # Token allocation for the model's inner reasoning chain
    },
    system=system_prompt,
    messages=messages
)

print("--- Pretty-Printed response.content Blocks ---\n")

# Convert each content block (ThinkingBlock, TextBlock) to a dict for clean printing
pprint([block.model_dump() for block in response.content], indent=2, width=80)