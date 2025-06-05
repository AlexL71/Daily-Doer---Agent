# config.py (Template - Fill in your actual values in a local copy that is gitignored)

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE'
YOUR_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID_HERE' # For bot's direct messages if needed

# Paths to your Google credentials files
# These files should be in your project root and listed in .gitignore
SPEECH_SA_KEY_PATH = "speech-sa-key.json"
GOOGLE_CREDENTIALS_PATH = "credentials.json" # For Gmail/Calendar OAuth

# List of news source homepages for HTML scraping
NEWS_SOURCE_HOMEpages = [
    "https://www.aljazeera.com/news/", # Example, works relatively well
    # "https://www.bbc.com/news", # Add other sites you want to scrape
    # "https://www.euronews.com/news", # Ensure your web_utils.py has selectors for these
]