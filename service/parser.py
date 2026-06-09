import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from service.retry import with_retry

load_dotenv()

client = OpenAI(
    base_url=f"{os.getenv('AZURE_FOUNDRY_ENDPOINT').rstrip('/')}/openai/v1/",
    api_key=os.getenv("AZURE_FOUNDRY_API_KEY")
)

DEPLOYMENT = os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4.1-mini")

@with_retry(max_attempts=3, delay=2.0, backoff=2.0)
def call_parser_llm(client, deployment, prompt):
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,  # reduced from 2000
        temperature=0
    )
    return response.choices[0].message.content.strip()

def parse_to_structured(raw_text: str, model_class, context: str = "") -> dict:
    """
    Takes raw LLM output and converts it to a structured JSON
    matching the given Pydantic model class.
    """
    schema = model_class.model_json_schema()

    prompt = f"""You are a precise data extractor.

Convert the following analysis text into a valid JSON object that exactly matches the provided schema.

SCHEMA:
{json.dumps(schema, indent=2)}

ANALYSIS TEXT TO CONVERT:
{raw_text}

{f"ADDITIONAL CONTEXT: {context}" if context else ""}

Rules:
- Return ONLY valid JSON, no markdown, no explanation, no code blocks
- Every required field must be present
- Lists must be actual JSON arrays
- Strings must be actual JSON strings
- fit_score must be an integer between 1 and 10
- eligibility_verdict must be one of: Yes, Likely, Uncertain, Unlikely
- decision must be one of: PURSUE, PURSUE WITH CAUTION, DO NOT PURSUE
- overall_risk_level must be one of: Low, Medium, High
- confidence_level must be one of: High, Medium, Low
- If information is missing, use empty list [] or empty string ""
"""

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0
    )

    raw = call_parser_llm(client, DEPLOYMENT, prompt)
    # raw = response.choices[0].message.content.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)