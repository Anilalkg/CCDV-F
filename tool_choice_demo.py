# tool_choice_demo.py

import anthropic
import json
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Define extraction tool schema
ORDER_EXTRACTION_TOOL = {
    "name": "extract_order_details",
    "description": "Extracts structured order details from customer support messages.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "issue_type": {"type": "string", "enum": ["refund", "cancellation", "delay"]},
            "urgency": {"type": "string", "enum": ["low", "medium", "high"]}
        },
        "required": ["order_id", "issue_type", "urgency"]
    }
}

def parse_support_ticket(user_message: str):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        tools=[ORDER_EXTRACTION_TOOL],
        # FORCING THE SPECIFIC TOOL EXECUTION
        tool_choice={"type": "tool", "name": "extract_order_details"},
        messages=[{"role": "user", "content": user_message}]
    )

    # Extract the forced tool invocation input directly
    tool_use_block = next(
        block for block in response.content if block.type == "tool_use"
    )
    
    return tool_use_block.input


if __name__ == "__main__":
    ticket = "Hi, my order #ORD-8821 is delayed by three days! I need this resolved urgently."
    
    extracted_data = parse_support_ticket(ticket)
    print("--- Forced Tool Call Arguments ---")
    print(json.dumps(extracted_data, indent=2))