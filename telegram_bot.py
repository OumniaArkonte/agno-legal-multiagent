import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from agno_agents import run_multi_agent_system  

load_dotenv()

# Récupérer le token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Le token Telegram n'est pas défini ! Vérifie ton .env")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bonjour ! Envoie-moi un fichier PDF ou TXT pour l'analyse de contrat."
    )

# Gestion des fichiers envoyés
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_name = document.file_name

    if not (file_name.endswith(".pdf") or file_name.endswith(".txt")):
        await update.message.reply_text("Seuls les fichiers PDF et TXT sont acceptés.")
        return

    # Télécharger le fichier
    file = await document.get_file()
    file_path = f"./tmp/{file_name}"
    os.makedirs("./tmp", exist_ok=True)
    await file.download_to_drive(file_path)

    await update.message.reply_text("Fichier reçu ! Analyse en cours... ")

    # Appel au système multi-agent
    try:
        analysis_result = run_multi_agent_system(file_path)
    except Exception as e:
        await update.message.reply_text(f"Erreur lors de l'analyse : {e}")
        return

    # Envoyer le résultat à l'utilisateur
    result_text = f"Analyse terminée !\n\nRésumé :\n{analysis_result.get('summary', 'Aucun résumé')}\n\n" \
                  f"Principaux risques : {analysis_result.get('key_risks', [])}\n\n" \
                  f"Recommandations : {analysis_result.get('recommendations', [])}"
    
    await update.message.reply_text(result_text)

# Commande inconnue ou texte
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commande inconnue. Envoie-moi un fichier PDF ou TXT.")

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), unknown))

    print("Bot Telegram démarré...")
    app.run_polling()
