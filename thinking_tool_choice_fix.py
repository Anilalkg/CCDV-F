"""
thinking_tool_choice_fix.py

CCDV-F exam concept: extended thinking + tool_choice compatibility.

RULE: When thinking is on, tool_choice may only be {"type": "auto"} or
      {"type": "none"}. "any" and {"type": "tool", ...} force a tool call,
      and the API rejects them:
      "Thinking may not be enabled when tool_choice forces tool use."

Correct answer to the question: A. Change tool_choice from "any" to "auto".

Model note: newer models reject thinking={"type": "enabled", "budget_tokens": N}
and require thinking={"type": "adaptive"} plus output_config={"effort": ...}.
Older models use the "enabled" + budget_tokens form. This script supports both.
"""

import os
import anthropic

from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

# Set USE_ADAPTIVE=0 for older models that still take "enabled" + budget_tokens
USE_ADAPTIVE = os.environ.get("USE_ADAPTIVE", "1") == "1"

TOOLS = [{
    "name": "get_weather",
    "description": "Get the current weather for a city. Use only when the user "
                   "asks about current weather conditions.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name, e.g. Baltimore"}},
        "required": ["city"],
    },
}]


def thinking_kwargs():
    """Return the thinking settings for the model generation in use."""
    if USE_ADAPTIVE:
        return {
            "thinking": {"type": "adaptive"},
            # extra_body keeps this working even if your SDK version doesn't
            # know the output_config parameter yet
            "extra_body": {"output_config": {"effort": "medium"}},
        }
    return {"thinking": {"type": "enabled", "budget_tokens": 2048}}  # needs max_tokens > 2048


def broken_request():
    """Thinking + tool_choice 'any' -> 400, whichever thinking form is used."""
    try:
        client.messages.create(
            model=MODEL, max_tokens=4096, tools=TOOLS,
            tool_choice={"type": "any"},        # NOT allowed with thinking
            messages=[{"role": "user", "content": "What's the weather in Baltimore?"}],
            **thinking_kwargs(),
        )
        print("BROKEN: unexpectedly accepted")
    except anthropic.BadRequestError as e:
        print("BROKEN (tool_choice=any):", e.message)


def fixed_request(question: str):
    """Option A: keep thinking, use tool_choice 'auto'. Claude decides."""
    try:
        resp = client.messages.create(
            model=MODEL, max_tokens=4096, tools=TOOLS,
            tool_choice={"type": "auto"},       # allowed with thinking
            messages=[{"role": "user", "content": question}],
            **thinking_kwargs(),
        )
    except anthropic.BadRequestError as e:
        print("  REQUEST REJECTED:", e.message)
        return

    print("  block types:", [b.type for b in resp.content])   # debug aid
    # Select blocks by TYPE, never by position: thinking blocks come first.
    for block in resp.content:
        if block.type == "thinking":
            summary = (block.thinking or "(thinking summarized/omitted)")[:80]
            print("  [thinking]", summary.replace("\n", " "), "...")
        elif block.type == "redacted_thinking":
            print("  [redacted_thinking]")
        elif block.type == "tool_use":
            print("  [tool_use]", block.name, block.input)
        elif block.type == "text":
            print("  [text]", block.text[:120])
    print("  stop_reason:", resp.stop_reason)   # "tool_use" or "end_turn"


if __name__ == "__main__":
    print(f"model={MODEL}  adaptive={USE_ADAPTIVE}\n")
    broken_request()

    print("\nFIXED, question that needs the tool:")
    fixed_request("What's the weather in Baltimore right now?")   # expect tool_use

    print("\nFIXED, question that does not need the tool:")
    fixed_request("Explain what a cold front is in one sentence.")  # expect end_turn
