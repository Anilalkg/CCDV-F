# structured_output_schema.py

import anthropic
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Define your target schema using Pydantic
class IncidentReport(BaseModel):
    severity: str = Field(description="Incident severity level: LOW, MEDIUM, HIGH, CRITICAL")
    affected_services: list[str] = Field(description="List of impacted system service names")
    root_cause_summary: str = Field(description="Concise description of the primary failure cause")

# 2. Extract the JSON schema for the tool definition
schema = IncidentReport.model_json_schema()

# 3. Define the extraction tool
EXTRACTION_TOOL = {
    "name": "record_incident_report",
    "description": "Records a structured incident report from raw system logs.",
    "input_schema": schema
}

def extract_structured_data(log_text: str) -> IncidentReport:
    """
    Forces Claude to use the specified tool, ensuring guaranteed schema compliance.
    """
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=[EXTRACTION_TOOL],
        # Force the model to invoke this exact tool
        tool_choice={"type": "tool", "name": "record_incident_report"},
        messages=[
            {
                "role": "user",
                "content": f"Parse the following outage log:\n\n{log_text}"
            }
        ]
    )

    # Search for the forced tool execution block
    tool_use_block = next(
        block for block in response.content if block.type == "tool_use"
    )

    # Validate and instantiate response into a typed Pydantic object
    validated_output = IncidentReport(**tool_use_block.input)
    return validated_output


if __name__ == "__main__":
    sample_log = """
    [2026-09-18 14:22:01] ALERT: Database connection pool exhausted on DB-Primary.
    Payments API and Checkout Microservice returning HTTP 500 errors.
    Engineers identified a missing index on the transactions table causing query backpressure.
    """

    report = extract_structured_data(sample_log)
    print("--- Validated Schema Output ---")
    print(f"Severity:       {report.severity}")
    print(f"Services:       {', '.join(report.affected_services)}")
    print(f"Root Cause:     {report.root_cause_summary}")