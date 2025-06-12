import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Chemins des fichiers
json_path = "jpmorganchase_risk_analysis.json"
json_path2= "jpmorganchase_financial_risk.json"
md_path = "jpmorganchase_risk_dashboard.md"

# Fonctions locales
from utils.gemini_client import regenerate_dashboard_from_json
from utils.gemini_analysis import generate_dynamic_recommendations
from utils.export import export_md_to_pdf

# Configuration Streamlit
st.set_page_config(layout="wide", page_title="JPMorgan Chase - Risk Dashboard")
st.title("📊 JPMorgan Chase – Financial Risk Dashboard")

# Chargement des données
df = pd.read_json(json_path)
df.columns = df.columns.str.lower().str.strip()
df2 = pd.read_json(json_path2)
df2.columns = df2.columns.str.lower().str.strip()

# Colonnes manquantes
df["impact_level"] = df.get("impact_level", "Medium")
df["sentiment"] = df.get("sentiment", "Neutral")
df["risk_category"] = df.get("risk_category", "Autre")
df2["financial_metric"] = df2.get("financial_metric", "N/A")
df2["risk_category"] = df2.get("risk_category", "Autre")    
df2["sentiment"] = df2.get("sentiment", "Neutral")

# Nettoyage
df["impact_level"] = df["impact_level"].astype(str).str.capitalize()
df["sentiment"] = df["sentiment"].astype(str).str.capitalize()
df["risk_category"] = df["risk_category"].astype(str).str.title()
df2["impact_level"] = df2["impact_level"].astype(str).str.capitalize()
df2["sentiment"] = df2["sentiment"].astype(str).str.capitalize()
df2["risk_category"] = df2["risk_category"].astype(str).str.title()


# 🧰 Helpers
def impact_emoji(level):
    return {
        "Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"
    }.get(level, "⚪")

def format_category(cat):
    return f"<span style='background-color:#e0f0ff; color:#005c99; padding:3px 8px; border-radius:8px;'>{cat}</span>"

# 🎛️ Filtres
st.sidebar.header("🔍 Filtres")
categories = st.sidebar.multiselect("Catégorie de risque", df["risk_category"].unique(), default=list(df["risk_category"].unique()))
sentiments = st.sidebar.multiselect("Sentiment", df["sentiment"].unique(), default=list(df["sentiment"].unique()))
impact_levels = st.sidebar.multiselect("Impact", df["impact_level"].unique(), default=list(df["impact_level"].unique()))

# Filtrage
filtered_df = df[
    df["risk_category"].isin(categories) &
    df["sentiment"].isin(sentiments) &
    df["impact_level"].isin(impact_levels)
]

# 🗂️ Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📑 Rapport Markdown",
    "📰 Articles filtrés",
    "📊 Visualisations",
    "🧠 Recommandations",
    "📉 Uncertainty Mapping"
])

with tab1:
    st.subheader("📄 Rapport complet généré par Gemini")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("Aucun fichier markdown trouvé.")

    st.markdown("### 📥 Télécharger les fichiers")
    with open(md_path, "rb") as f:
        st.download_button("⬇️ Télécharger le Markdown", f, file_name="jpmorganchase_risk_dashboard.md")
    with open(json_path, "rb") as f:
        st.download_button("⬇️ Télécharger les données JSON", f, file_name="jpmorganchase_risk_analysis.json")

    if st.button("🧾 Exporter en PDF"):
        export_md_to_pdf(md_path, "rapport.pdf")
        with open("rapport.pdf", "rb") as f:
            st.download_button("⬇️ Télécharger le PDF", f, file_name="rapport_jpmorgan.pdf")

    if st.button("🧠 Analyser à nouveau "):
        with st.spinner("Analyse en cours ..."):
            success = regenerate_dashboard_from_json(json_path)
        if success:
            st.success("✅ Rapport regénéré avec succès.")
            st.rerun()
        else:
            st.error("❌ Échec de la génération du rapport.")

with tab2:
    st.subheader("🗞️ Articles classés")
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            st.markdown(f"""
            <div style='padding:10px; margin-bottom:8px; border:1px solid #ddd; border-radius:10px'>
                <h5>{row['title']}</h5>
                <p><strong>Date :</strong> {row['date']} | <strong>Source :</strong> {row['source']}</p>
                <p>{row['summary']}</p>
                <p>
                    {impact_emoji(row['impact_level'])}
                    Impact: <strong>{row['impact_level']}</strong> |
                    Sentiment: <strong>{row['sentiment']}</strong> |
                    Risque: {format_category(row['risk_category'])}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Aucun article ne correspond aux filtres.")

with tab3:
    st.subheader("📊 Visualisations approfondies des risques")

    # 1. Barplot - Nombre de risques par catégorie et sentiment
    st.markdown("### 🔹 Nombre d'alertes par catégorie et sentiment")
    grouped = df.groupby(['risk_category', 'sentiment']).size().reset_index(name='count')
    pivot = grouped.pivot(index='risk_category', columns='sentiment', values='count').fillna(0)
    st.bar_chart(pivot)

    # 2. Heatmap - Croisement Catégorie x Impact
    st.markdown("### 🔥 Carte de chaleur des catégories vs gravité")
    heatmap_data = df.groupby(['risk_category', 'impact_level']).size().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heatmap_data, annot=True, fmt="g", cmap="YlOrRd", ax=ax)
    st.pyplot(fig)

    # 3. Chronologie - Évolution temporelle des alertes par catégorie
    st.markdown("### 📈 Chronologie des alertes par catégorie")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    timeline = df.groupby([df['date'].dt.to_period('D').dt.to_timestamp(), 'risk_category']).size().unstack().fillna(0)
    st.line_chart(timeline)


with tab4:
    st.subheader("📌 Recommandations dynamiques")

if st.button("🧠 Recommandations "):
    with st.spinner("Analyse stratégique en cours..."):
        data = filtered_df.to_dict(orient="records")
        try:
            recommendations = generate_dynamic_recommendations(data)
            st.success("✅ Recommandations générées avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")
            recommendations = {}
else:
    recommendations = {}

if recommendations:
    for cat, bloc in recommendations.items():
        with st.expander(f"📂 {cat}"):
            st.markdown(f"**Résumé** : {bloc['summary']}")
            st.markdown("**✅ Recommandations** :")
            for r in bloc["actions"]:
                st.markdown(f"- {r}")
            st.markdown(f"**📈 Commentaire stratégique** : {bloc['comment']}")
else:
    st.info("Cliquez sur le bouton ci-dessus pour lancer l’analyse.")

with tab5:
    st.subheader("📉 Uncertainty Mapping")

    if "confidence_score" not in df2.columns:
        st.error("❌ Les scores de confiance ne sont pas disponibles dans les données.")
    else:
        try:
            df2["confidence_score"] = pd.to_numeric(df2["confidence_score"], errors='coerce')
            avg_score = df2["confidence_score"].mean()

            st.metric("🔎 Score moyen de confiance", f"{avg_score:.2f}", delta=None)

            st.progress(min(avg_score, 1.0))

            threshold = 0.75
            if avg_score < threshold:
                st.warning(f"⚠️ Score moyen < {threshold}. Il est conseillé de relancer l'analyse avec uniquement les articles fiables.")
                if st.button("🔁 Relancer l’analyse Gemini avec les articles fiables (score > 0.75)"):
                    filtered = df2[df2["confidence_score"] >= threshold]
                    from utils.gemini_client import build_prompt_from_df, analyze_with_gemini, save_output
                    prompt = build_prompt_from_df(filtered)
                    with st.spinner("Analyse en cours avec Gemini..."):
                        result = analyze_with_gemini(prompt)
                        if result:
                            save_output(result, filename="jpmorganchase_filtered_risk.json")
                            st.success("✅ Analyse relancée avec succès. Voir fichier : jpmorganchase_filtered_risk.json")
                        else:
                            st.error("❌ Échec de la génération avec Gemini.")
            else:
                st.success("✅ Score de confiance global satisfaisant. Pas besoin de relancer l’analyse.")

        except Exception as e:
            st.error(f"Erreur lors de l’analyse des scores : {e}")