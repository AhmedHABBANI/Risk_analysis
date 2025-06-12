
```bash
git clone https://github.com/AhmedHABBANI/Risk_analysis.git
pip install -r requirements.txt
# creer fichie .env der feh apis dylk
GOOGLE_API_KEY=your_google_gemini_api_key
SERPAPI_KEY=your_serpapi_key
#executer had rfss
python extract_jpmorgan_risks_serpapi.py         # Récupère les articles via SerpAPI
python extract_jpmorgan_risks.py                 # Analyse des risques avec Gemini
python convert_json_to_txt.py                    # Conversion des fichiers JSON en TXT
python generate_risk_dashboard.py                # Génère le rapport Markdown avec Gemini
streamlit run app.py                             # Lance le dashboard interactif
