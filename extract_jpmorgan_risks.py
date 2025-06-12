import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from serpapi import GoogleSearch

# 🔐 Clés API
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 🔧 Configuration Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# 🔍 Étape 1 : Rechercher les articles via SerpAPI
def fetch_serpapi_news(company_name):
    query = f"{company_name} financial news May 2025"
    params = {
        "engine": "google",
        "q": query,
        "hl": "en",
        "gl": "us",
        "num": 10,
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    articles = []
    for r in results.get("organic_results", []):
        articles.append({
            "title": r.get("title"),
            "date": r.get("date") or r.get("snippet")[:10],
            "source": r.get("source") or r.get("displayed_link"),
            "content": r.get("snippet", "")[:1000]
        })

    return articles

# 🧠 Étape 2 : Construction du prompt
def build_prompt(articles, company="JPMorgan Chase"):
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
Each JSON element must include a confidence_score key.
"""
    for art in articles:
        prompt += f"""
---
Title: {art['title']}
Date: {art['date']}
Source: {art['source']}
Content: {art['content']}
"""
    return prompt

# 🤖 Étape 3 : Appel à Gemini
def analyze_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
        return None

# 💾 Étape 4 : Sauvegarde JSON
def save_output(json_text, filename="jpmorganchase_financial_risk.json"):
    if not json_text:
        print("❌ Aucun contenu à sauvegarder.")
        return
    # Nettoyage Markdown JSON
    if json_text.startswith("```json"):
        json_text = json_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(json_text)
        # Sauvegarde complète et formatée
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        print(f"✅ Résultat sauvegardé dans {filename}")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur lors du parsing JSON : {e}")
        with open("invalid_output.txt", "w", encoding="utf-8") as f:
            f.write(json_text)
        print("🔍 Résultat brut sauvegardé dans invalid_output.txt")


# 🚀 Main
if __name__ == "__main__":
    # 🔁 Relance manuelle via articles filtrés si dispo
    if os.path.exists("filtered_articles.json"):
        print("📥 Chargement des articles filtrés à haute confiance...")
        with open("filtered_articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    else:
        print("🔍 Récupération des articles avec SerpAPI...")
        articles = fetch_serpapi_news("JPMorgan Chase")

    if not articles:
        print("❌ Aucun article trouvé.")
        exit()

    print("✏️ Génération du prompt...")
    prompt = build_prompt(articles)

    print("🤖 Analyse avec Gemini...")
    json_result = analyze_with_gemini(prompt)

    print("💾 Sauvegarde...")
    save_output(json_result)
