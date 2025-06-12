import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_dynamic_recommendations(json_data):
    prompt = f"""
You are a senior risk consultant. You will receive a list of risk incidents related to JPMorgan Chase.

Each item includes:
- title
- date
- source
- summary
- risk_category
- impact_level
- sentiment

Group them by risk_category and for each category, generate:
1. A short summary of key issues.
2. 3 recommended actions to mitigate the risks.
3. A strategic comment on the risk evolution.

Return a JSON like:
{{
  "Liquidity & capital structure": {{
    "summary": "...",
    "actions": ["...", "...", "..."],
    "comment": "..."
  }},
  ...
}}
Here is the input data:

{json.dumps(json_data, indent=2)}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    text = response.text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
