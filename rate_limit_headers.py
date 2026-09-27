import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Access raw response to retrieve HTTP headers
raw_response = client.messages.with_raw_response.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Ping API for rate limit inspection."}
    ]
)

# Extract response headers
headers = raw_response.headers

print("--- Rate Limit Headroom ---")
print(f"Requests Remaining: {headers.get('anthropic-ratelimit-requests-remaining')} / {headers.get('anthropic-ratelimit-requests-limit')}")
print(f"Tokens Remaining:   {headers.get('anthropic-ratelimit-tokens-remaining')} / {headers.get('anthropic-ratelimit-tokens-limit')}")
print(f"Request Reset Time: {headers.get('anthropic-ratelimit-requests-reset')}")
print(f"Token Reset Time:   {headers.get('anthropic-ratelimit-tokens-reset')}")

# Access parsed response content
parsed_message = raw_response.parse()