# promptsw_xml_tag.py

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Sample contracts to compare
contract_v1 = "Section 4.1: Either party may terminate with 30 days written notice."
contract_v2 = "Section 8.2: Termination requires 60 days written notice and a $5,000 fee."

prompt = f"""You are a legal document analyst. Compare the termination clauses provided in the two contracts below.

<contract_v1>
{contract_v1}
</contract_v1>

<contract_v2>
{contract_v2}
</contract_v2>

<instructions>
1. Identify the notice period for each contract.
2. Highlight any financial penalties for termination.
3. Place your step-by-step reasoning inside <reasoning> tags.
4. Place your concise final comparison summary inside <summary> tags.
</instructions>"""

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=2048,
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": prompt}]
)

# Robust extraction handling both ThinkingBlock and TextBlock
response_text = "".join(
    block.text for block in response.content if block.type == "text"
)

print("--- Output Text ---")
print(response_text)