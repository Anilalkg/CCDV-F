import anthropic
from dotenv import load_dotenv
from rich import print as rprint


# Load ANTHROPIC_API_KEY from your local .env file
load_dotenv()

client = anthropic.Anthropic()

# Multi-turn conversation history using ONLY "user" and "assistant" roles
messages = [
    # Turn 1: User asks a question
    {
        "role": "user",
        "content": "What is the capital of France?"
    },
    # Turn 2: Assistant's prior response stored in history
    {
        "role": "assistant",
        "content": "The capital of France is Paris."
    },
    # Turn 3: User follows up
    {
        "role": "user",
        "content": "What is its population and main famous landmark?"
    }
]

response = client.messages.create(
    # Use valid model identifiers (e.g., claude-3-7-sonnet-latest)
    # model="claude-3-7-sonnet-latest",
    model="claude-sonnet-5",
    thinking={"type": "disabled"},  # Ensures response.content[0] is always a TextBlock
    max_tokens=1024,
    # Standing persona / instructions belong in the top-level 'system' parameter
    system="You are a helpful travel assistant. Keep answers concise.",
    messages=messages
)

print(response.content[0].text)

rprint(response.content)