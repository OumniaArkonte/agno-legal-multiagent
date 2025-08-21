import streamlit as st
import os
import json
import pdfplumber
from dotenv import load_dotenv
from agno_agents import run_multi_agent_system  

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

st.set_page_config(page_title="Multi-Agent Contract Analyzer", layout="wide")

st.title("Multi-Agent Contract Analyzer")
st.write("Upload a contract file to analyze it with the multi-agent system.")

uploaded_file = st.file_uploader("Upload contract file (.txt, .pdf)", type=["txt", "pdf"])

# Fonction pour extraire texte du PDF
def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

if uploaded_file:
    # Lire le contenu du fichier
    if uploaded_file.type == "application/pdf":
        file_content = extract_pdf_text(uploaded_file)
    else:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")

    st.text_area("Contract content preview:", value=file_content[:2000], height=300)

    # Bouton pour exécuter le multi-agent system
    if st.button("Run Multi-Agent System"):
        with st.spinner("Running agents..."):
            report = run_multi_agent_system(file_content)
        st.success("Analysis completed!")
        st.json(report)

# Webhook WhatsApp minimal (pour recevoir et traiter fichiers)
import flask
from flask import request, jsonify

app = flask.Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        # Vérification token
        if request.args.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"
    
    if request.method == "POST":
        data = request.json

        print(json.dumps(data, indent=2))
        return jsonify({"status": "received"})

if __name__ == "__main__":
    st.write("Streamlit interface ready. Run via `streamlit run whatsapp_webhook.py`")
