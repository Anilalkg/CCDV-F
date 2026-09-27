# validation_retry_loop.py

import json
import anthropic
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Define the target schema
class EnterpriseUser(BaseModel):
    user_id: int
    email: str
    roles: list[str]

def generate_validated_user(max_retries: int = 3) -> EnterpriseUser:
    messages = [
        {
            "role": "user",
            "content": "Extract user info from this text into JSON: 'ID 104, email alex@company.com, admin and dev roles'"
        }
    ]

    for attempt in range(max_retries):
        # Step 1: Generate
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=256,
            messages=messages
        )
        raw_text = response.content[0].text

        try:
            # Step 2: Validate against schema
            data = json.loads(raw_text)
            validated_user = EnterpriseUser(**data)
            print(f"✅ Success on attempt {attempt + 1}!")
            return validated_user

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"⚠️ Validation failed on attempt {attempt + 1}: {e}")
            
            # Step 3: Append assistant's invalid output + user error feedback for re-prompting
            messages.append({"role": "assistant", "content": raw_text})
            messages.append({
                "role": "user",
                "content": f"Your previous JSON output was invalid. Validation error:\n{e}\n\nPlease re-generate ONLY valid JSON matching the schema."
            })

    raise RuntimeError("Failed to generate valid output after maximum retries.")

if __name__ == "__main__":
    user = generate_validated_user()
    print("Validated Result:", user)