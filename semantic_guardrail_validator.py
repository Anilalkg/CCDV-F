# semantic_guardrail_validator.py

import json
import anthropic
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# ---------------------------------------------------------------------
# 1. DEFINITIONS & SCHEMAS
# ---------------------------------------------------------------------
VALID_CATEGORIES = ["TECHNICAL_SUPPORT", "BILLING_INQUIRY", "GENERAL_INFO"]

class ClassificationResult(BaseModel):
    category: str
    confidence: float
    reasoning: str

# ---------------------------------------------------------------------
# 2. SEMANTIC GUARDRAIL / DISCRIMINATOR CONTROL
# ---------------------------------------------------------------------
def validate_semantic_coherence(input_text: str, category: str) -> tuple[bool, str]:
    """
    Semantic Guardrail Control:
    Inspects whether the assigned category semantically contradicts the input text.
    """
    input_lower = input_text.lower()

    # Rule 1: Technical support keywords vs Billing misclassification
    tech_keywords = ["crash", "bug", "error", "404", "exception", "stacktrace", "cannot log in"]
    if category == "BILLING_INQUIRY" and any(kw in input_lower for kw in tech_keywords):
        return False, f"Semantic Contradiction: Input describes a technical error but was classified as '{category}'."

    # Rule 2: Billing keywords vs Tech support misclassification
    billing_keywords = ["invoice", "credit card", "charge", "refund", "subscription", "payment"]
    if category == "TECHNICAL_SUPPORT" and any(kw in input_lower for kw in billing_keywords):
        return False, f"Semantic Contradiction: Input describes payment/billing but was classified as '{category}'."

    return True, "Valid"


# ---------------------------------------------------------------------
# 3. PIPELINE WITH INTEGRATED GUARDRAIL
# ---------------------------------------------------------------------
def process_classification(user_input: str, mock_hallucinated_response: dict = None):
    print(f"\n--- Processing Input: '{user_input}' ---")

    # Step 1: Simulate API Execution or Call Model
    if mock_hallucinated_response:
        # Simulates a 200 OK response returning valid JSON that carries a semantic contradiction
        raw_json_str = json.dumps(mock_hallucinated_response)
    else:
        # Standard API Call with Structured Output Prompt
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=256,
            system="Classify the input into one of: TECHNICAL_SUPPORT, BILLING_INQUIRY, GENERAL_INFO. Return JSON only.",
            messages=[{"role": "user", "content": user_input}]
        )
        raw_json_str = response.content[0].text

    # Step 2: Schema Validation (Passes successfully despite semantic contradiction!)
    try:
        parsed_data = ClassificationResult.model_validate_json(raw_json_str)
        print(f"✅ Schema Validation: PASSED (Category: '{parsed_data.category}')")
    except ValidationError as e:
        print(f"❌ Schema Validation: FAILED - {e}")
        return

    # Step 3: REQUIRED CONTROL - Semantic Guardrail Inspection
    is_valid, failure_reason = validate_semantic_coherence(user_input, parsed_data.category)

    if not is_valid:
        print(f"🚨 SEMANTIC GUARDRAIL CATCH: {failure_reason}")
        print("Action Triggered: Routing to secondary discriminator model / Human-in-the-Loop review.")
    else:
        print(f"✅ Semantic Guardrail: PASSED. Proceeding with downstream routing.")


if __name__ == "__main__":
    # Test Case 1: Silent Failure / Contradiction Scenario
    # Input is explicitly a technical crash, but model outputs BILLING_INQUIRY with valid JSON.
    mock_contradictory_payload = {
        "category": "BILLING_INQUIRY",
        "confidence": 0.98,
        "reasoning": "The user mentioned an application issue."
    }

    process_classification(
        user_input="My application throws a 500 NullPointerException every time I click submit.",
        mock_hallucinated_response=mock_contradictory_payload
    )

    # Test Case 2: Coherent / Valid Scenario
    mock_valid_payload = {
        "category": "TECHNICAL_SUPPORT",
        "confidence": 0.95,
        "reasoning": "User is experiencing login errors."
    }

    process_classification(
        user_input="I cannot log into my account due to an error code 404.",
        mock_hallucinated_response=mock_valid_payload
    )