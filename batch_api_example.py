import time
import anthropic
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()
client = anthropic.Anthropic()

# 1. PREPARE THE BATCH REQUESTS
# Each item in the batch requires a unique 'custom_id' to match results later.
batch_requests = [
    {
        "custom_id": f"request-doc-{i}",
        "params": {
            "model": "claude-sonnet-5",
            "max_tokens": 512,
            "thinking": {"type": "disabled"},
            "messages": [
                {
                    "role": "user",
                    "content": f"Summarize document batch item #{i}: High-volume async processing is cost-effective."
                }
            ]
        }
    }
    for i in range(1, 4)  # Example batch of 3 requests
]

# 2. CREATE THE MESSAGE BATCH
print("--- Creating Message Batch (50% Discount) ---")
message_batch = client.messages.batches.create(requests=batch_requests)
batch_id = message_batch.id
print(f"Batch Created Successfully. ID: {batch_id}")
print(f"Initial Processing Status: {message_batch.processing_status}\n")

# 3. POLL FOR BATCH COMPLETION
# Batches process asynchronously. Poll processing_status until "ended".
while message_batch.processing_status == "in_progress":
    print("Batch processing in progress... checking again in 5 seconds.")
    time.sleep(5)
    message_batch = client.messages.batches.retrieve(batch_id)

print(f"\nFinal Batch Status: {message_batch.processing_status}")

# 4. RETRIEVE BATCH RESULTS
print("--- Retrieving Batch Results ---")
for result in client.messages.batches.results(batch_id):
    custom_id = result.custom_id
    result_type = result.result.type  # 'succeeded', 'errored', etc.

    if result_type == "succeeded":
        message = result.result.message
        # Extract response text
        response_text = message.content[0].text if message.content else ""
        rprint({
            "custom_id": custom_id,
            "status": "succeeded",
            "response": response_text.strip(),
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        })
    else:
        print(f"Request {custom_id} failed with error: {result.result.error}")