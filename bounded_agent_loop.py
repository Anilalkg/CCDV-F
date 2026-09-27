# bounded_agent_loop.py

import json
import time
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Sample search tool that returns ambiguous/partial results
tools = [
    {
        "name": "search_database",
        "description": "Searches for records.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
]

def mock_search(query: str) -> str:
    # Simulates an unhelpful result that causes an un-bounded agent to re-query indefinitely
    return json.dumps({"result": "No exact match found. Try a broader search terms."})


# =====================================================================
# AGENT LOOP WITH EXPLICIT TERMINATION BOUNDS
# =====================================================================
def run_bounded_agent(
    user_prompt: str,
    max_turns: int = 4,              # Turn Bound
    max_total_tokens: int = 5000,    # Token Budget Bound
    max_execution_seconds: float = 15.0 # Time Bound
):
    messages = [{"role": "user", "content": user_prompt}]
    
    cumulative_tokens_used = 0
    start_time = time.time()

    print(f"🚀 Starting agent run with bounds: Max Turns={max_turns}, Max Tokens={max_total_tokens}, Max Time={max_execution_seconds}s")

    turn = 0
    while True:
        turn += 1
        elapsed_time = time.time() - start_time

        # -------------------------------------------------------------
        # TERMINATION CHECK 1: Max Execution Time Exceeded
        # -------------------------------------------------------------
        if elapsed_time > max_execution_seconds:
            print(f"\n⛔ TERMINATED: Timeout limit reached ({elapsed_time:.1f}s > {max_execution_seconds}s). Halting loop.")[cite: 5]
            break

        # -------------------------------------------------------------
        # TERMINATION CHECK 2: Max Turn Limit Reached
        # -------------------------------------------------------------
        if turn > max_turns:
            print(f"\n⛔ TERMINATED: Maximum turn limit ({max_turns}) reached without completion. Halting loop.")[cite: 5]
            break

        print(f"\n--- Turn {turn} (Elapsed: {elapsed_time:.1f}s | Cumulative Tokens: {cumulative_tokens_used}) ---")

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=512,
            tools=tools,
            messages=messages
        )

        # Track usage
        turn_tokens = response.usage.input_tokens + response.usage.output_tokens
        cumulative_tokens_used += turn_tokens
        print(f"Turn Tokens: {turn_tokens} | Total Tokens Billed: {cumulative_tokens_used}")

        # -------------------------------------------------------------
        # TERMINATION CHECK 3: Cumulative Token Budget Exceeded
        # -------------------------------------------------------------
        if cumulative_tokens_used >= max_total_tokens:
            print(f"\n⛔ TERMINATED: Token budget exhausted ({cumulative_tokens_used} >= {max_total_tokens}). Halting loop.")[cite: 5]
            break

        messages.append({"role": "assistant", "content": response.content})

        # Process natural completion vs tool call
        if response.stop_reason == "end_turn":
            print("\n✅ Task completed naturally:")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_output = mock_search(block.input.get("query", ""))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_output
                    })
            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    # Ambiguous prompt designed to trigger endless search queries
    ambiguous_query = "Find the file about the project. If not found, keep searching with different variations."
    run_bounded_agent(ambiguous_query)