import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

MODEL_NAME = "claude-sonnet-5"

# Standard Sonnet Pricing (per 1M tokens)
INPUT_PRICE_PER_M = 3.00
OUTPUT_PRICE_PER_M = 15.00  # 5x multiplier over input cost

prompt_input = "Analyze the key benefits of moving from a monolithic architecture to microservices."

# Scenario A: Unconstrained Output (Verbose)
response_verbose = client.messages.create(
    model=MODEL_NAME,
    max_tokens=2048,
    messages=[
        {"role": "user", "content": prompt_input}
    ]
)

# Scenario B: Constrained Output (Strict Length / Format Constraints)
response_constrained = client.messages.create(
    model=MODEL_NAME,
    max_tokens=2048,
    messages=[
        {
            "role": "user", 
            "content": f"{prompt_input}\n\nConstraint: Provide answer in exactly 3 bullet points, maximum 15 words per bullet point."
        }
    ]
)

def calculate_cost(usage):
    input_cost = (usage.input_tokens / 1_000_000) * INPUT_PRICE_PER_M
    output_cost = (usage.output_tokens / 1_000_000) * OUTPUT_PRICE_PER_M
    return input_cost, output_cost, input_cost + output_cost

# Extract text outputs
verbose_text = next(b.text for b in response_verbose.content if b.type == "text")
constrained_text = next(b.text for b in response_constrained.content if b.type == "text")

# Cost Comparisons
v_in, v_out, v_total = calculate_cost(response_verbose.usage)
c_in, c_out, c_total = calculate_cost(response_constrained.usage)

print("=" * 60)
print("SCENARIO A: UNCONSTRAINED (VERBOSE OUTPUT)")
print("=" * 60)
print(f"MODEL RESPONSE:\n{verbose_text}\n")
print(f"Output Tokens: {response_verbose.usage.output_tokens}")
print(f"Output Cost:   ${v_out:.6f}")
print(f"Total Cost:    ${v_total:.6f}\n")

print("=" * 60)
print("SCENARIO B: CONSTRAINED OUTPUT")
print("=" * 60)
print(f"MODEL RESPONSE:\n{constrained_text}\n")
print(f"Output Tokens: {response_constrained.usage.output_tokens}")
print(f"Output Cost:   ${c_out:.6f}")
print(f"Total Cost:    ${c_total:.6f}\n")

savings_pct = ((v_total - c_total) / v_total) * 100
print("=" * 60)
print(f"TOTAL COST SAVINGS: {savings_pct:.2f}%")
print("=" * 60)