# multi_turn_chat_caching.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

SYSTEM_PROMPT = [
    {
        "type": "text",
        "text": "You are a customer support agent.",
        "cache_control": {"type": "ephemeral"}
    }
]

def add_cache_control_to_last_message(messages: list) -> list:
    updated_messages = []
    
    for i, msg in enumerate(messages):
        content = msg["content"]
        if isinstance(content, str):
            content_blocks = [{"type": "text", "text": content}]
        else:
            content_blocks = [dict(b) for b in content]

        # Place cache_control breakpoint on the VERY LAST message in history
        if i == len(messages) - 1:
            content_blocks[-1]["cache_control"] = {"type": "ephemeral"}
        else:
            content_blocks[-1].pop("cache_control", None)

        updated_messages.append({"role": msg["role"], "content": content_blocks})

    return updated_messages


def run_multi_turn_chat_simulation():
    messages_history = []
    
    user_turns = [
        "Turn 1: Hello, I need help troubleshooting my network setup.",
        "Turn 2: The indicator light on the router is flashing red.",
        "Turn 3: I tried restarting it, but it stays red. What next?"
    ]

    for turn_num, user_input in enumerate(user_turns, start=1):
        print(f"\n--- Chat Turn {turn_num} ---")

        prepared_messages = add_cache_control_to_last_message(messages_history)
        prepared_messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_input}]
        })

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=prepared_messages
        )

        # SAFE BLOCK HANDLING: Safely extract text across ThinkingBlock and TextBlock instances
        assistant_reply = ""
        for block in response.content:
            if block.type == "text":
                assistant_reply += block.text
            elif block.type == "thinking":
                print(f"💭 [Thought Process Length: {len(block.thinking)} chars]")

        # Update persistent history for subsequent turns
        messages_history.append({"role": "user", "content": user_input})
        messages_history.append({"role": "assistant", "content": assistant_reply})

        print(f"Assistant: {assistant_reply}")
        print(f"Uncached Tokens (New Turn): {response.usage.input_tokens}")
        print(f"Cache Write Tokens:          {response.usage.cache_creation_input_tokens}")
        print(f"Cache Read Tokens (Hits):    {response.usage.cache_read_input_tokens}")


if __name__ == "__main__":
    run_multi_turn_chat_simulation()