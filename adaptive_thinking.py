import anthropic
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()
client = anthropic.Anthropic()

# Complex multi-step reasoning problem
complex_prompt = (
    "A logistics network has 3 hubs (A, B, C). Hub A can ship up to 500 units/day to B, "
    "and B can ship up to 300 units/day to C. However, route A->B loses 5% of goods in transit, "
    "and route B->C loses 10%. If Hub C demands exactly 225 delivered units per day, "
    "what is the exact integer minimum units Hub A must ship out daily to meet this demand, "
    "and what is the exact total loss across both segments?"
)

# Call API using adaptive thinking and explicit effort bounds
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    # Enable Adaptive Thinking
    thinking={
        "type": "adaptive"
    },
    # Control cost/time predictability using effort level ('low', 'medium', 'high')
    output_config={
        "effort": "high"
    },
    messages=[
        {"role": "user", "content": complex_prompt}
    ]
)

# Process and separate Thinking block from Text block
print("=" * 60)
print("EXTENDED THINKING PROCESS (Reasoning Blocks)")
print("=" * 60)

rprint(response.content)

for block in response.content:
    if block.type == "thinking":
        print(block.thinking)
    elif block.type == "text":
        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)
        print(block.text)

# Token consumption breakdown
print("\n" + "=" * 60)
print("USAGE METRICS")
print("=" * 60)
print(f"Input Tokens:  {response.usage.input_tokens}")
print(f"Output Tokens: {response.usage.output_tokens}")