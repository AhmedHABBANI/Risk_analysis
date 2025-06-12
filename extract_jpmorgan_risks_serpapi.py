import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

queries = [
    ("JPMorgan Chase stock volatility May 2025", "Market & financial"),
    ("JPMorgan fintech competition Stripe May 2025", "Competitive"),
    ("JPMorgan deposit outflow liquidity stress May 2025", "Liquidity & capital structure"),
    ("JPMorgan SEC compliance investigation May 2025", "Regulatory & legal"),
    ("JPMorgan cybersecurity incident 2025", "Technological"),
    ("JPMorgan sanctions exposure Russia China 2025", "Geopolitical"),
    ("JPMorgan ESG controversy or scandal May 2025", "ESG"),
]

def guess_sentiment(text):
    if any(word in text.lower() for word in ["scandal", "drop", "decline", "investigation", "loss", "outflow", "volatility", "cyberattack", "fine", "exposure", "sanction", "fraud"]):
        return "Negative"
    elif any(word in text.lower() for word in ["growth", "positive", "profit", "gain", "stable"]):
        return "Positive"
    else:
        return "Neutral"

def guess_impact_level(category):
    high_impact = ["Regulatory & legal", "Liquidity & capital structure", "Technological"]
    return "High" if category in high_impact else "Medium"

all_articles = []

for query, category in queries:
    params = {
        "engine": "google",
        "q": query,
        "hl": "en",
        "gl": "us",
        "num": 5,
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    for result in results.get("organic_results", []):
        snippet = result.get("snippet", "")[:300]
        article = {
            "title": result.get("title"),
            "date": result.get("date") or "2025-05",
            "source": result.get("source") or result.get("displayed_link"),
            "link": result.get("link"),
            "summary": snippet,
            "risk_category": category,
            "sentiment": guess_sentiment(snippet),
            "impact_level": guess_impact_level(category)
        }
        all_articles.append(article)

# ✅ Supprimer les doublons par (title + source)
seen = set()
deduplicated = []
for art in all_articles:
    key = (art["title"], art["source"])
    if key not in seen:
        deduplicated.append(art)
        seen.add(key)

# ✅ Sauvegarde
with open("jpmorganchase_risk_analysis.json", "w", encoding="utf-8") as f:
    json.dump(deduplicated, f, indent=2)

print(f"✅ {len(deduplicated)} articles sauvegardés dans jpmorganchase_risk_analysis.json")
