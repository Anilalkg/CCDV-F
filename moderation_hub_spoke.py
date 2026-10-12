# file_name: moderation_hub_spoke.py

import os
from typing import Dict, Any, List
from dataclasses import dataclass
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file (expects ANTHROPIC_API_KEY)
load_dotenv()

# Initialize the client using the environment variable key
client = anthropic.Anthropic()


@dataclass
class AnalysisResult:
    spoke_name: str
    flagged: bool
    confidence: float
    category: str


# --- RESTRICTED SUB-AGENTS (SPOKES) ---

class ImageAnalyzerSpoke:
    """
    Spoke agent restricted purely to image analysis.
    Does NOT have access to post removal or policy enforcement tools.
    """
    def analyze_image(self, image_url: str) -> AnalysisResult:
        # Example call using Claude API with image input if needed
        # Uses os.getenv("ANTHROPIC_API_KEY") automatically loaded by load_dotenv()
        return AnalysisResult(
            spoke_name="image_analyzer",
            flagged=True,
            confidence=0.95,
            category="NSFW_CONTENT"
        )


class TextClassifierSpoke:
    """Spoke agent restricted strictly to text analysis."""
    def analyze_text(self, text: str) -> AnalysisResult:
        return AnalysisResult(
            spoke_name="text_classifier",
            flagged=False,
            confidence=0.10,
            category="NONE"
        )


# --- ACTION TOOLS (EXECUTED ONLY BY HUB / COORDINATOR) ---

def remove_post(post_id: str, reason: str) -> str:
    """Action Tool: Centrally managed side-effect tool to remove a post."""
    return f"SUCCESS: Post '{post_id}' deleted from platform. Reason: {reason}"


# --- COORDINATOR (HUB) ---

class ModerationCoordinatorHub:
    """
    Central Hub Orchestrator.
    Controls workflow routing, aggregates spoke findings, and executes policy actions.
    """
    def __init__(self):
        self.image_spoke = ImageAnalyzerSpoke()
        self.text_spoke = TextClassifierSpoke()

    def process_post(self, post_id: str, text: str, image_url: str) -> str:
        print(f"[Hub] Processing Post ID: {post_id}...")

        # 1. Distribute tasks to isolated spokes
        image_finding = self.image_spoke.analyze_image(image_url)
        text_finding = self.text_spoke.analyze_text(text)

        print(f"[Hub] Image Analysis Result: {image_finding}")
        print(f"[Hub] Text Analysis Result: {text_finding}")

        # 2. Collect findings centrally
        findings: List[AnalysisResult] = [image_finding, text_finding]

        # 3. Enforce policy decisions centrally
        return self._evaluate_and_enforce_policy(post_id, findings)

    def _evaluate_and_enforce_policy(self, post_id: str, findings: List[AnalysisResult]) -> str:
        for finding in findings:
            if finding.flagged and finding.confidence > 0.8:
                reason = f"Flagged by {finding.spoke_name} ({finding.category}, confidence: {finding.confidence})"
                return remove_post(post_id, reason=reason)

        return f"SUCCESS: Post '{post_id}' approved and published."


if __name__ == "__main__":
    hub = ModerationCoordinatorHub()
    
    result = hub.process_post(
        post_id="post_9901",
        text="Sample post content",
        image_url="https://example.com/sample.jpg"
    )
    
    print("[Final Result]:", result)