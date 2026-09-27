
# multi_turn_conversation.py

import anthropic
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
client = anthropic.Anthropic()

def run_multi_turn_chat():
    # Rule 1: System prompt is passed at the top-level, NOT inside messages[]
    system_prompt = "You are a concise enterprise software architecture assistant."

    # Rule 2: Conversation MUST start with a 'user' role
    # Rule 3: Roles MUST strictly alternate (user -> assistant -> user)
    messages = [
        {
            "role": "user",
            "content": "Hi, I am planning a microservices architecture for an e-commerce platform."
        }
    ]

    print("--- Turn 1: User ---")
    print(messages[-1]["content"])

    # First API Call
    response_1 = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        system=system_prompt,
        messages=messages
    )


    print("--- Raw Pretty-Printed response_1.content ---")
    # Convert Pydantic content block objects into dictionaries for clean formatting
    pprint([block.model_dump() for block in response_1.content], indent=2, width=80)

    return

    # Extract assistant output safely
    assistant_reply_1 = "".join(
        block.text for block in response_1.content if block.type == "text"
    )

    print("\n--- Turn 1: Assistant ---")
    print(assistant_reply_1)

    # Rule 4: Append assistant response to preserve strict role alternation
    messages.append({
        "role": "assistant",
        "content": assistant_reply_1
    })

    # Append next user turn
    messages.append({
        "role": "user",
        "content": "What database pattern should I use for managing user orders?"
    })

    print("\n--- Turn 2: User ---")
    print(messages[-1]["content"])

    # Second API Call with full, correctly-ordered multi-turn context
    response_2 = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        system=system_prompt,
        messages=messages
    )

    assistant_reply_2 = "".join(
        block.text for block in response_2.content if block.type == "text"
    )

    print("\n--- Turn 2: Assistant ---")
    print(assistant_reply_2)


if __name__ == "__main__":
    run_multi_turn_chat()