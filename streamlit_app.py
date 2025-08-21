import streamlit as st
from dotenv import load_dotenv
import os
from app.utils.io import any_to_text
from app.utils.pipeline import process_contract

# Charger les variables d'environnement (.env)
load_dotenv()

# Forcer l’utilisation de Gemini (via Agno)
os.environ["AGNO_PROVIDER"] = "google"

GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-exp")

st.set_page_config(page_title="Legal Multi-Agent (Agno + Gemini)", layout="wide")
st.title(" Legal Multi-Agent System (Gemini)")

# Vérification de la clé API Gemini
ok = True
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error(" Aucune clé Gemini détectée (GOOGLE_API_KEY).")
    ok = False
else:
    st.success(" Clé Gemini détectée.")
    st.write(f" Provider: {os.getenv('AGNO_PROVIDER')}")
    st.write(f" Model ID: {GEMINI_MODEL_ID}")

# Choix de la juridiction
jurisdiction = st.selectbox("Jurisdiction", ["FR", "EU", "US", "UK"], index=0)

# Upload du contrat
file = st.file_uploader("Upload a contract (.pdf/.docx/.txt)", type=["pdf", "docx", "txt"])

# Lancement de l’analyse
if file and st.button("Run analysis"):
    if not ok:
        st.stop()

    with st.spinner(" Parsing document..."):
        try:
            text = any_to_text(file.name, file.read())
        except Exception as e:
            st.error(f"Erreur lors de l’extraction du texte : {e}")
            st.stop()

        if not text.strip():
            st.error(" Le texte extrait est vide.")
            st.stop()

    with st.spinner(" Running agents (Gemini)..."):
        try:
            result = process_contract(text, jurisdiction=jurisdiction, model_id=GEMINI_MODEL_ID)
            st.success(" Analyse terminée.")
            st.subheader(" Manager Consolidated Report (JSON)")
            st.json(result)
        except Exception as e:
            st.error(f" Erreur pendant l’analyse : {e}")
