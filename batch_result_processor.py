# filename: batch_result_processor.py

import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = anthropic.Anthropic()

def save_classification(ticket_id: str, label: str):
    """Placeholder function to simulate saving results to database."""
    print(f"Saved label '{label}' for ticket {ticket_id}")

def send_to_retry_queue(failed_items: list):
    """Placeholder function to simulate pushing failed jobs to a retry queue."""
    print(f"Pushed {len(failed_items)} items to retry queue.")

def process_batch_results(batch_id: str):
    # Fetch batch results stream from Anthropic API
    results = client.messages.batches.results(batch_id)

    # Track metrics for logging
    succeeded_count = 0
    failed_requests = []

    # Iterate over the returned batch result items directly
    for result in results:
        # 1. Use custom_id to safely identify the ticket ID (Fixes 3% mismatched labels)
        ticket_id = result.custom_id
        
        # 2. Branch on result.type before accessing .message (Fixes AttributeError crash)
        result_type = result.result.type

        if result_type == "succeeded":
            # Safe to extract message content only when result_type is "succeeded"
            classification_text = result.result.message.content[0].text
            
            # Save classification to the database keyed directly on custom_id
            save_classification(ticket_id, classification_text)
            succeeded_count += 1

        elif result_type in ("errored", "canceled", "expired"):
            # Non-succeeded results do not have a .message attribute.
            # Reading result.result.message here would raise an AttributeError.
            error_details = getattr(result.result, "error", None)
            
            print(f"Ticket {ticket_id} failed with status '{result_type}': {error_details}")
            
            # Route to retry queue or record error status in DB
            failed_requests.append({
                "ticket_id": ticket_id,
                "status": result_type,
                "error": error_details
            })

    print(f"Batch processing complete. Successful: {succeeded_count}, Failed: {len(failed_requests)}")
    
    # Send failed items to retry pipeline
    if failed_requests:
        send_to_retry_queue(failed_requests)

if __name__ == "__main__":
    # Replace with an actual message batch ID from your Anthropic workspace
    TEST_BATCH_ID = "msgbatch_01123456789"  
    
    print(f"Fetching results for batch: {TEST_BATCH_ID}...\n")
    try:
        process_batch_results(TEST_BATCH_ID)
    except Exception as e:
        print(f"Error executing batch processing: {e}")