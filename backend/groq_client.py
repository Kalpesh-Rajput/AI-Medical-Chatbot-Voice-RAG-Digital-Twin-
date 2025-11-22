import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file!")

client = Groq(api_key=GROQ_API_KEY)

# Choose a fast Groq model
GROQ_MODEL = "llama-3.1-8b-instant"


def groq_generate(prompt, max_tokens=300, temperature=0.2):
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Access message content correctly (attribute, not dict)
        return response.choices[0].message.content

    except Exception as e:
        return f"[Groq Error]: {str(e)}"
