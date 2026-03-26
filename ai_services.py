import google.generativeai as genai
import time
import config

genai.configure(api_key=config.GEMINI_API_KEY)

def summarize_text_with_gemini(text_to_summarize: str) -> str:
    if not text_to_summarize or text_to_summarize.strip() == "":
        return "The webpage didn't seem to have enough text content for a summary."
    if text_to_summarize.startswith("Sorry, I couldn't"):
        return text_to_summarize

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""Please provide a quick and concise summary of the following text, ideally in 3 to 5 sentences, 
focusing on the main points and key information.
If the text seems to be an error message or indicates failure to retrieve content, please state that clearly.

---
{text_to_summarize}
---

Quick Summary (3-5 sentences):
"""
    try:
        response = model.generate_content(prompt)
        if response.parts and response.parts[0].text:
            return response.parts[0].text
        else:
            print(f"Gemini summarization returned an unexpected response structure: {response}")
            return "Sorry, I received an unusual response while trying to summarize the text."
    except Exception as e:
        print(f"Error summarizing text with Gemini: {e}")
        return "Sorry, I encountered an error while trying to summarize the text."

def process_natural_language(text: str) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    current_date_for_prompt = time.strftime('%Y-%m-%d')
    
    today_weekday = time.localtime().tm_wday
    days_until_tuesday = (1 - today_weekday + 7) % 7 
    if days_until_tuesday == 0 and time.localtime().tm_hour >= 14:
        days_until_tuesday = 7
    
    next_tuesday_timestamp = time.time() + (days_until_tuesday * 24 * 60 * 60)
    next_tuesday_date_str = time.strftime('%Y-%m-%d', time.localtime(next_tuesday_timestamp))

    prompt = f"""
    You are the intelligent brain of a Telegram bot. Analyze the user's request and determine the correct action and its parameters.
    Respond ONLY with a valid JSON object. Do not include any other text or explanations.

    The available actions are:
    1. "send_email": Requires "to" (string), "subject" (string), and "body" (string).
    2. "create_calendar_event": Requires "summary" (string), "start_time" (string, ISO 8601 format like 'YYYY-MM-DDTHH:MM:SS'), and "end_time" (string, ISO 8601 format).
    3. "summarize_url_content": Requires "url" (string).
    4. "get_latest_news_from_sources": Does not require parameters. User implies they want general news.
    5. "chat": When the user is just making small talk or asking something outside defined actions. Requires a "response" (string).

    - If a user asks to write content as part of an action, generate it and include it in the appropriate parameter.
    - Infer details like the subject of an email if not explicitly given.
    - For calendar events, today's date is {current_date_for_prompt}. If the user says "tomorrow", calculate the date. If "next [weekday]", calculate that date.
    - Ensure time for calendar events is in HH:MM:SS format. If AM/PM is used, convert to 24-hour format. If only hour is given (e.g. "2 PM"), assume :00 for minutes.

    Here are some examples:
    User request: "send mail to test@example.com saying we made agent and put poem in mail"
    Your JSON response: {{"action": "send_email", "to": "test@example.com", "subject": "We made an AI Agent!", "body": "We have successfully made an AI agent!\\n\\nHere is a short poem about it:\\n\\nA line of code, a spark of thought,\\nA silent servant, deftly taught."}}
    User request: "schedule a meeting about our project next Tuesday at 2 PM for 1 hour"
    Your JSON response: {{"action": "create_calendar_event", "summary": "Meeting about our project", "start_time": "{next_tuesday_date_str}T14:00:00", "end_time": "{next_tuesday_date_str}T15:00:00"}}
    User request: "summarize the news from this page for me https://www.bbc.com/news/some-article"
    Your JSON response: {{"action": "summarize_url_content", "url": "https://www.bbc.com/news/some-article"}}
    User request: "what's today's news?"
    Your JSON response: {{"action": "get_latest_news_from_sources"}}
    User request: "tell me some news"
    Your JSON response: {{"action": "get_latest_news_from_sources"}}
    User request: "what's the weather like"
    Your JSON response: {{"action": "chat", "response": "I can't check the real-time weather, but I can send emails, schedule events, or summarize news articles if you provide a link!"}}

    Now, analyze the following user request. Remember to only output the JSON.

    User request: "{text}"
    Your JSON response:
    """
    try:
        response = model.generate_content(prompt)
        if response.parts and response.parts[0].text:
            return response.parts[0].text
        else:
            print(f"Gemini NLU returned an unexpected response structure: {response}")
            return '{{"action": "chat", "response": "I had a bit of trouble understanding that. Could you try again?"}}'
    except Exception as e:
        print(f"Error in process_natural_language with Gemini: {e}")
        return '{{"action": "chat", "response": "I encountered an error trying to understand your request. Please try again."}}'
