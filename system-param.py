import anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY from local .env file
load_dotenv()

client = anthropic.Anthropic()

response = client.messages.create(
    # model="claude-3-7-sonnet-latest",
    model="claude-sonnet-5",

    max_tokens=1024,
    
    # CORRECT: Pass persona and standing instructions as the top-level system parameter
    system="""
    You are a Senior Python Security Auditor.
    - Keep responses concise and focused strictly on vulnerability remediation.
    - Always wrap code fixes in clean Markdown code blocks.
    """,
    
    # The messages array ONLY accepts "user" and "assistant" roles
    messages=[
        {
            "role": "user", 
            "content": "How do I fix SQL injection in my Python sqlite3 query?"
        }
    ]
)

print(response.content[0].text)