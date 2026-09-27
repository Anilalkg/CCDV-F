import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Tool definition for reading server log files
tools = [
    {
        "name": "read_log_chunk",
        "description": "Reads a chunk of the server log file by offset.",
        "input_schema": {
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "description": "Line offset to read from"}
            },
            "required": ["offset"]
        }
    }
]

def mock_read_log_chunk(offset: int) -> str:
    """Mock log file that always returns benign logs without an error code."""
    return f"Line {offset}: [INFO] System health check status OK - 200 OK"

def run_unbounded_agent_demo():
    # Flawed prompt with no explicit step limit or exit condition for missing data
    messages = [
        {
            "role": "user",
            "content": "Find the exact line where 'CRITICAL_FAIL' occurred in the server logs. Keep searching line by line until you find it."
        }
    ]

    print("--- Starting Agent Run (Unbounded Design) ---")
    
    # DANGER: Infinite while loop with no iteration limit or exit guard
    step = 0
    while True:
        step += 1
        print(f"\n[Agent Turn {step}] Requesting action from Claude...")

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # Check if model wants to call a tool
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        
        if not tool_use_blocks:
            print("Agent stopped calling tools.")
            print(f"Final Answer: {response.content[0].text}")
            break

        # Append assistant response to message history
        messages.append({"role": "assistant", "content": response.content})

        # Process tool calls
        tool_results = []
        for tool_call in tool_use_blocks:
            print(f"-> Agent invoked tool '{tool_call.name}' with args: {tool_call.input}")
            
            # Simulated tool execution
            result_text = mock_read_log_chunk(tool_call.input.get("offset", 0))
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result_text
            })

        # Append tool output back to conversation context
        messages.append({"role": "user", "content": tool_results})

        # Failure condition: The loop will run infinitely because 'CRITICAL_FAIL' 
        # never appears, and there is no maximum iteration cap (max_iterations).


if __name__ == "__main__":
    # Demonstration capped at concept level
    run_unbounded_agent_demo()