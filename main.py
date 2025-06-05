# main.py (or app.py)
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import config
from bot_handlers import start, handle_text_message, handle_voice_message

def main():
    try:
        import google_services
        if not google_services.creds: # Check if creds were successfully loaded/created
            print("Warning: Google services (Gmail/Calendar) credentials might not have loaded correctly. Please run the bot once to authenticate if needed.")
    except FileNotFoundError as e:
        print(f"ERROR: Critical file for Google services not found: {e}. Gmail/Calendar features will fail.")
        print(f"Please ensure '{config.GOOGLE_CREDENTIALS_PATH}' exists and is correctly configured.")
    except Exception as e:
        print(f"Error importing or initializing google_services.py: {e}")
        print("Gmail and Calendar functionalities might not work.")

    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    application.bot_data['temp_file_counter'] = 0 

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
        
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()