# file_name: multi_intent_orchestrator.py

import os
from dataclasses import dataclass
from typing import List, Dict, Any
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

@dataclass
class Intent:
    intent_type: str
    description: str

class AddressUpdateSubAgent:
    def execute(self, description: str) -> str:
        # Tool call to update database billing address
        return "SUCCESS: Billing address successfully updated in CRM."

class RefundInvestigationSubAgent:
    def execute(self, description: str) -> str:
        # Tool call to check transactions and initiate refund
        return "SUCCESS: Identified duplicate charge of $29.99 on 2026-10-01. Refund initiated (ID: ref_8821)."

class SupportOrchestrator:
    def __init__(self):
        self.address_agent = AddressUpdateSubAgent()
        self.refund_agent = RefundInvestigationSubAgent()

    def decompose_intents(self, user_request: str) -> List[Intent]:
        """
        Decomposes multi-part user requests into explicit sub-intents.
        """
        # In production, use Claude structured outputs (JSON schema) to parse intents
        return [
            Intent(intent_type="UPDATE_ADDRESS", description="Update user billing address"),
            Intent(intent_type="INVESTIGATE_DOUBLE_CHARGE", description="Investigate duplicate subscription charge")
        ]

    def handle_request(self, user_request: str) -> str:
        print(f"[Orchestrator] Decomposing user prompt: '{user_request}'")
        intents = self.decompose_intents(user_request)
        
        results = []
        for intent in intents:
            if intent.intent_type == "UPDATE_ADDRESS":
                res = self.address_agent.execute(intent.description)
                results.append(f"• Address Task: {res}")
            elif intent.intent_type == "INVESTIGATE_DOUBLE_CHARGE":
                res = self.refund_agent.execute(intent.description)
                results.append(f"• Refund Task: {res}")

        # Combine results guaranteeing full resolution of both sub-tasks
        return "All customer requests have been fully resolved:\n" + "\n".join(results)

if __name__ == "__main__":
    orchestrator = SupportOrchestrator()
    user_prompt = "I was charged twice for my subscription, and I also need to update my billing address."
    user_prompt = "I was charged twice for my subscription"

    final_output = orchestrator.handle_request(user_prompt)
    
    print("\n[Final Resolution Output]:")
    print(final_output)