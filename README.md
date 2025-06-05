# DailyDoer Agent - A Conversational AI Telegram Bot

DailyDoer Agent is a Python-based Telegram bot powered by Google Gemini. It's designed to understand natural language (both text and voice) to assist with everyday tasks like sending emails, managing a Google Calendar, and getting summaries of news articles.

## Features

* **Natural Language Understanding:** The bot processes natural language commands and queries.
* **Voice Command Processing:** Voice messages sent to the bot are transcribed to text and then processed.
* **Email Sending:** Emails can be composed and sent via an associated Gmail account.
* **Calendar Management:** Events can be created and added to an associated Google Calendar.
* **News Summarization:**
    * Summarizes specific news articles when a URL is provided.
    * Fetches and summarizes latest articles from pre-configured news source homepages by attempting to scrape article links.
* **Basic Chat:** Engages in simple conversational exchanges for queries outside its defined actions.

## Technologies Used

* **Programming Language:** Python 3
* **Core AI Model (NLU & Summarization):** Google Gemini API (`gemini-1.5-flash-latest`)
* **Telegram Integration:** `python-telegram-bot` library
* **Google Cloud Services & APIs:**
    * Gmail API
    * Google Calendar API
    * Google Cloud Speech-to-Text API
* **Google API Client Libraries:**
    * `google-api-python-client`
    * `google-auth-httplib2`
    * `google-auth-oauthlib`
    * `google-cloud-speech`
* **Web Content Fetching & Processing:**
    * `httpx` (for asynchronous HTTP requests to fetch web pages)
    * `BeautifulSoup4` (for parsing HTML to find article links on homepages)
    * `newspaper3k` (for extracting main text content from individual article URLs)
* **Configuration & Utilities:** `json`, `os`, `asyncio`, `time`

## Setup Instructions

Follow these steps to get the DailyDoer Agent running locally:

1.  **Clone the Repository:**
    ```bash
    git clone <your-github-repository-url>
    cd DailyDoer-Agent
    ```

2.  **Create a Python Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    Activate it:
    * On Windows: `venv\Scripts\activate`
    * On macOS/Linux: `source venv/bin/activate`

3.  **Install Dependencies:**
    Ensure a `requirements.txt` file is present (or create one via `pip freeze > requirements.txt` from a correctly configured environment). Then install:
    ```bash
    pip install -r requirements.txt
    ```
    Alternatively, install packages manually:
    ```bash
    pip install python-telegram-bot google-generativeai google-cloud-speech google-api-python-client google-auth-httplib2 google-auth-oauthlib httpx beautifulsoup4 newspaper3k
    ```

4.  **Set Up Credentials & Configuration (VERY IMPORTANT):**

    * **`config.py`**:
        1.  A template for `config.py` should be present in the repository (possibly named `config_template.py` or `config.py` if it contains only placeholders).
        2.  A local `config.py` file must be created. If using a template, copy it to `config.py`.
        3.  Edit this local `config.py` file with the actual secret keys and preferences:
            ```python
            # config.py (Local, gitignored version with actual values)
            TELEGRAM_TOKEN = 'ACTUAL_TELEGRAM_BOT_TOKEN'
            GEMINI_API_KEY = 'ACTUAL_GEMINI_API_KEY'
            YOUR_CHAT_ID = 'YOUR_PERSONAL_TELEGRAM_CHAT_ID' # For direct bot messages

            SPEECH_SA_KEY_PATH = "speech-sa-key.json"
            GOOGLE_CREDENTIALS_PATH = "credentials.json"

            NEWS_SOURCE_HOMEpages = [
                "[https://www.aljazeera.com/news/](https://www.aljazeera.com/news/)",
                # Add other homepages for scraping
            ]
            ```
        4.  **The local `config.py` containing actual keys must be listed in the `.gitignore` file to prevent accidental commits to GitHub.**

    * **`credentials.json` (For Gmail & Google Calendar OAuth):**
        1.  Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
        2.  Create a new project or select an existing one.
        3.  Enable the **Gmail API** and **Google Calendar API** for this project.
        4.  Go to "APIs & Services" -> "Credentials".
        5.  Select "+ CREATE CREDENTIALS" -> "OAuth client ID".
        6.  Choose "Desktop application" as the application type.
        7.  Provide a name and click "Create".
        8.  Download the provided JSON file. Rename this file to `credentials.json` and place it in the root directory of the project.
        9.  **This `credentials.json` file must be listed in the `.gitignore` file.**

    * **`speech-sa-key.json` (For Google Speech-to-Text):**
        1.  In the Google Cloud Console (same project), navigate to "IAM & Admin" -> "Service Accounts".
        2.  Select "+ CREATE SERVICE ACCOUNT".
        3.  Enter a name (e.g., `daily-doer-speech-sa`) and a description. Then, "CREATE AND CONTINUE".
        4.  For the "Role", choose "Cloud Speech Client". Then, "CONTINUE", and "DONE".
        5.  In the list of service accounts, find the newly created one and click on its email address.
        6.  Navigate to the "KEYS" tab. Select "ADD KEY" -> "Create new key".
        7.  Choose "JSON" as the key type and select "CREATE".
        8.  A JSON file will be downloaded. Rename this file to `speech-sa-key.json` and place it in the root directory of the project.
        9.  **This `speech-sa-key.json` file must be listed in the `.gitignore` file.**

    * **`token.json` (For Gmail & Google Calendar - Generated on First Run):**
        * When the bot is run for the first time and attempts to access Gmail or Calendar, a browser window should open for Google Account authorization.
        * After successful authorization, a `token.json` file will be generated in the project directory. This file stores access and refresh tokens.
        * **This `token.json` file must be listed in the `.gitignore` file.**

5.  **Run the Bot:**
    With all dependencies installed and configuration/credential files correctly set up in the project's root directory, the bot can be run using:
    ```bash
    python app.py
    ```
    (Or `python main.py` if the main script is named `main.py`).

## How to Use the Bot

Interaction with the bot occurs via its Telegram chat:

* **Start:** Sending `/start` can be used, though the bot should respond to messages if running.
* **Send Email:** "Email friend@example.com, subject Hello, body How are you doing?"
* **Create Calendar Event:** "Schedule a meeting for tomorrow at 3 PM about the project presentation."
* **Summarize a Specific URL:** "Summarize this page for me: https://example.com/news-article"
* **Get Latest News (from configured sources):** "What's today's news?" or "Get latest news"
* **Voice Commands:** Voice messages containing any of the above commands can be sent. The bot will confirm with "Heard: \[transcribed text]" before processing.
* **Chat:** General phrases like "Hello bot" or "Tell me a joke" will elicit a conversational reply from Gemini.

## Troubleshooting

* **`AttributeError: module 'config' has no attribute '...'`**: This indicates a necessary variable is not defined in the `config.py` file.
* **Google API Errors (401, 403, "credentials not found"):**
    * Verify that `credentials.json` and `speech-sa-key.json` are correctly placed in the project root and are the correct files from the Google Cloud Console.
    * Confirm that the Gmail, Google Calendar, and Cloud Speech-to-Text APIs are enabled in the Google Cloud Project.
    * If Gmail/Calendar issues persist, deleting `token.json` and re-running the bot will re-initiate the Google OAuth authorization flow.
* **News scraping issues:** Extracting links from HTML homepages is inherently fragile. The CSS selectors in `web_utils.py` (`get_article_links_from_homepage`) may require specific tuning for each news website listed in `config.NEWS_SOURCE_HOMEpages`.

---