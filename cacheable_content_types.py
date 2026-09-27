# Updated cacheable_content_types.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. TOOL CACHING
cached_tools = [
    {
        "name": "query_database",
        "description": "Executes SQL queries against the knowledge base.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        },
        "cache_control": {"type": "ephemeral"}
    }
]

# 2. MESSAGE HISTORY CACHING (Text, Multi-modal, and Tool Execution History)
cached_messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Analyze the following system architectural log report and run database check:\n" + ("Log entry data line... " * 300)
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_01A2B3C4",
                "name": "query_database",
                "input": {"query": "SELECT status FROM server_logs;"}
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "toolu_01A2B3C4",
                "content": "Status: Healthy. Active sessions: 42.",
                # Breakpoint attached to tool_result block in message history
                "cache_control": {"type": "ephemeral"}
            }
        ]
    },
    {
        "role": "user",
        "content": "What is the status report based on the logs and database query result?"
    }
]

def demonstrate_cacheable_types():
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        tools=cached_tools,
        messages=cached_messages
    )

    print("=== Prompt Caching Execution Metrics ===")
    print(f"Uncached Tokens: {response.usage.input_tokens}")
    print(f"Cache Write:    {response.usage.cache_creation_input_tokens}")
    print(f"Cache Read:     {response.usage.cache_read_input_tokens}")

if __name__ == "__main__":
    demonstrate_cacheable_types()