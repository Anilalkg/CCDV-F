# filename: invoice_extractor.py

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# 1. Define the tool schema for recording invoice details
INVOICE_TOOL = {
    "name": "record_invoice",
    "description": "Extract and record structured invoice data from messy or handwritten documents.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "vendor_name": {"type": "string"},
            "total_amount": {"type": "number"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "amount": {"type": "number"}
                    },
                    "required": ["description", "amount"]
                }
            }
        },
        "required": ["invoice_number", "vendor_name", "total_amount"]
    }
}

def extract_invoice_data(invoice_text: str):
    # System prompt explicitly instructs Claude to use the tool
    system_prompt = (
        "You are an expert invoice extraction assistant. "
        "Analyze the provided invoice image/text thoroughly using your reasoning capabilities, "
        "and ALWAYS output your final structured output by calling the `record_invoice` tool."
    )

    # 2. Execute API Call combining Extended Thinking with tool_choice={"type": "auto"}
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=10000,  # Ensure high max_tokens budget when thinking is enabled
        thinking={
            "type": "adaptive"
            # "budget_tokens": 8000
        },
        system=system_prompt,
        tools=[INVOICE_TOOL],
        # FIX: Extended thinking requires tool_choice to be "auto" or "none" (not forced "tool")
        tool_choice={"type": "auto"},  
        messages=[
            {
                "role": "user",
                "content": f"Extract the details from this invoice document:\n\n{invoice_text}"
            }
        ]
    )

    # 3. Inspect thinking blocks and tool calls
    for block in response.content:
        if block.type == "thinking":
            print(f"[EXTENDED THINKING REASONING]\n{block.thinking[:200]}...\n")
        elif block.type == "tool_use":
            print(f"[TOOL CALLED]: {block.name}")
            print(f"[STRUCTURED PAYLOAD]: {block.input}")

if __name__ == "__main__":
    sample_invoice = """
    HANDWRITTEN INVOICE #99201
    Vendor: Acme Supplies Co.
    Items:
    - 2x Desk Chairs: $150.00
    - Delivery Fee: $25.00
    Total Due: $175.00
    """
    
    extract_invoice_data(sample_invoice)