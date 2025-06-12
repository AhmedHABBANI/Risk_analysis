import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

# 🔐 Clé API Gemini
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# ✅ Fonction principale d’appel à Gemini
def analyze_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
        return None

# 🧠 Générer un prompt à partir d’un DataFrame (re-filtrage avec confidence_score)
def build_prompt_from_df(df, company="JPMorgan Chase"):
    prompt = f"""
You are a financial risk analyst AI.

Analyze the following news about {company}. For each article, classify the financial risk into ONLY one of the following categories:

- Valuation risks
- Revenue risks
- Margin pressure
- Liquidity & capital structure
- Investment & CAPEX risks
- Currency & international exposure
- Operational financial risks

Return a JSON array. For each article, return the following fields:

- title
- date (YYYY-MM-DD)
- source
- summary (40–75 words)
- financial_metric (if any)
- risk_category (choose one)
- sentiment (Positive / Neutral / Negative)
- impact_level (Low / Medium / High)
- confidence_score (0.0 to 1.0 based on how clear and reliable the classification is)

DO NOT include explanations or comments. Just return a clean JSON array.
"""
    for _, art in df.iterrows():
        prompt += f"""
---
Title: {art['title']}
Date: {art['date']}
Source: {art['source']}
Content: {art.get('summary', '')[:1000]}
"""
    return prompt

# 💾 Sauvegarde des résultats JSON
def save_output(json_text, filename="jpmorganchase_filtered_risk.json"):
    if not json_text:
        print("❌ Aucun contenu à sauvegarder.")
        return
    if json_text.startswith("```json"):
        json_text = json_text.replace("```json", "").replace("```", "").strip()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_text)
    print(f"✅ Résultat sauvegardé dans {filename}")

# 📄 Re-générer le markdown à partir du JSON existant (déjà utilisé dans Streamlit)
def regenerate_dashboard_from_json(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            print("⚠️ Format JSON invalide")
            return False

        prompt = build_prompt_from_df(df)
        result = analyze_with_gemini(prompt)

        if result:
            with open("jpmorganchase_risk_dashboard.md", "w", encoding="utf-8") as f:
                f.write(result)
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Erreur lors du traitement du fichier JSON : {e}")
        return False
