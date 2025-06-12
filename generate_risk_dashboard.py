import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# === 1. Configuration ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === 2. Charger les données JSON ===
with open("jpmorganchase_financial_risk.json", "r", encoding="utf-8") as f:
    financial_data = json.load(f)

with open("jpmorganchase_risk_analysis.json", "r", encoding="utf-8") as f:
    news_data = json.load(f)

# === 3. Construire les textes résumés ===
def build_summary_text(data, is_financial):
    output = ""
    for art in data:
        output += f"- Title: {art.get('title')}\n"
        output += f"  Date: {art.get('date')}\n"
        output += f"  Source: {art.get('source')}\n"
        output += f"  Summary: {art.get('summary')}\n"
        output += f"  Risk Category: {art.get('risk_category')}\n"
        if is_financial:
            output += f"  Financial Metric: {art.get('financial_metric', 'N/A')}\n"
            output += f"  Sentiment: {art.get('sentiment', 'N/A')}\n"
            output += f"  Impact Level: {art.get('impact_level', 'N/A')}\n"
        output += "\n"
    return output

financial_text = build_summary_text(financial_data, is_financial=True)
news_text = build_summary_text(news_data, is_financial=False)

# === 4. Prompt Gemini enrichi ===
prompt = f"""
You are a senior financial risk analyst. Using the dataset below on JPMorgan Chase, generate a professional Markdown risk dashboard for executive use.

This includes:
- A financial risk analysis (`financial_data`) enriched with sentiment, impact, and metrics
- A news-based risk context (`news_data`) with categorized press coverage

## Please include in the markdown:

### 1. Executive Summary
- Top 3-4 key risks
- Main metrics mentioned
- Overall financial risk assessment

### 2. Risk Table
| Risk Category | Incidents | Main Metric | Sentiment | Concern |
|---------------|-----------|-------------|-----------|---------|

### 3. Heatmap
Y = risk category, X = impact (Low 🟢, Medium 🟡, High 🔴)

### 4. Category Analysis
- Group articles by `risk_category`
- Summarize concerns, trends, metrics
- Add mitigation recommendations

### 5. Timeline
Format: `YYYY-MM-DD | Category | Sentiment | Description`

### 6. Trend Arrows
For each category, add:
- Trend ↑ (growing), → (stable), ↓ (declining)
- Explanation

### 7. Final Risk Assessment
- Global risk outlook
- Top 3 urgent actions
- Risks to monitor

--- DATA STARTS BELOW ---

# Financial Risk Data:
{financial_text}

# News Risk Data:
{news_text}
"""

# === 5. Génération du rapport ===
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(prompt)

# === 6. Sauvegarde Markdown ===
with open("jpmorganchase_risk_dashboard.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ Rapport généré : jpmorganchase_risk_dashboard.md")
