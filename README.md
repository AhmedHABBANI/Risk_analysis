
```bash
git clone https://github.com/AhmedHABBANI/Risk_analysis.git   # ceci va importer le dossier complet dans votre repertoire de travail
pip install -r requirements.txt et y mettre ceci dedant :
streamlit>=1.35.0
pandas>=2.0.0
matplotlib>=3.8.0
seaborn>=0.12.2
requests>=2.31.0
python-dotenv>=1.0.0
google-generativeai>=0.5.4
serpapi>=0.1.5


GOOGLE_API_KEY=your_google_gemini_api_key
SERPAPI_KEY=your_serpapi_key
#executer ceci un par un 
python extract_jpmorgan_risks_serpapi.py         # Récupère les articles via SerpAPI
python extract_jpmorgan_risks.py                 # Analyse des risques avec Gemini
python convert_json_to_txt.py                    # Conversion des fichiers JSON en TXT
python generate_risk_dashboard.py                # Génère le rapport Markdown avec Gemini
streamlit run app.py                             # Lance le dashboard interactif
