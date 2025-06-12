import os
import json

def json_to_text(json_path):
    base, _ = os.path.splitext(json_path)
    txt_path = base + ".txt"
    if not os.path.exists(json_path):
        print(f"⚠️  Fichier non trouvé : {json_path}")
        return
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(txt_path, "w", encoding="utf-8") as out:
            out.write(json.dumps(data, indent=2))
        print(f"✅ Converti : {txt_path}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

# Exemple d'utilisation
json_to_text("jpmorganchase_financial_risk.json")
json_to_text("jpmorganchase_risk_analysis.json")
