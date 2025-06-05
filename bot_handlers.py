# bot_handlers.py
import json
import os
import asyncio
import config
from ai_services import process_natural_language, summarize_text_with_gemini
from speech_service import audio_to_text
from google_services import send_email, create_calendar_event
from web_utils import get_text_from_url, get_article_links_from_homepage

async def execute_bot_action(user_text, message_object_to_reply):
    json_response_text_for_error_log = ""
    try:
        json_response_text = process_natural_language(user_text)
        json_response_text_for_error_log = json_response_text

        if json_response_text.strip().startswith("```json"):
            json_response_text = json_response_text.strip()[7:-4].strip()
        elif json_response_text.strip().startswith("```"):
             json_response_text = json_response_text.strip()[3:-3].strip()
            
        data = json.loads(json_response_text)
        action = data.get("action")

        if action == "send_email":
            send_email(to=data["to"], subject=data["subject"], body=data["body"])
            await message_object_to_reply.reply_text(f"OK, I've sent the email to {data['to']}.")
        elif action == "create_calendar_event":
            create_calendar_event(summary=data["summary"], start_time=data["start_time"], end_time=data["end_time"])
            await message_object_to_reply.reply_text(f"OK, I've scheduled '{data['summary']}' in your calendar.")
        elif action == "summarize_url_content":
            url_to_summarize = data.get("url")
            if not url_to_summarize:
                await message_object_to_reply.reply_text("You asked me to summarize a URL, but I didn't get the URL. Please try again.")
                return
            await message_object_to_reply.reply_text(f"Okay, I'll try to fetch and summarize: {url_to_summarize}")
            extracted_text = await get_text_from_url(url_to_summarize)
            if extracted_text:
                if extracted_text.startswith("Sorry, I couldn't"):
                    summary = extracted_text
                else:
                    # await message_object_to_reply.reply_text("Content fetched. Now summarizing with Gemini...") # Optional intermediate message
                    summary = summarize_text_with_gemini(extracted_text)
                await message_object_to_reply.reply_text(summary)
            else:
                await message_object_to_reply.reply_text("Sorry, I couldn't extract any text content from that URL to summarize.")

        elif action == "get_latest_news_from_sources":
            await message_object_to_reply.reply_text("Fetching the latest news by scraping my sources. This might take a few moments...")
            
            processed_articles_info = []
            article_link_tasks = []
            
            for homepage_url in config.NEWS_SOURCE_HOMEpages:
                article_link_tasks.append(get_article_links_from_homepage(homepage_url, limit=1))

            link_fetch_results = await asyncio.gather(*article_link_tasks, return_exceptions=True)
            
            unique_article_urls = set()
            for result in link_fetch_results:
                if isinstance(result, list) and result: 
                    unique_article_urls.add(result[0]) 
                elif isinstance(result, Exception):
                    print(f"Error fetching links from a homepage during gather: {result}")
            
            final_article_urls_to_process = list(unique_article_urls)[:3] 

            if not final_article_urls_to_process:
                await message_object_to_reply.reply_text("Sorry, I couldn't find any specific articles from my configured news sources via scraping right now.")
                return

            for article_url in final_article_urls_to_process:
                text_content = await get_text_from_url(article_url)
                
                if text_content and not text_content.startswith("Sorry, I couldn't"):
                    summary = summarize_text_with_gemini(text_content)
                    processed_articles_info.append({"summary": summary, "url": article_url})
                else:
                    error_message = text_content if text_content else "Could not retrieve content."
                    processed_articles_info.append({"summary": f"Could not get a summary: {error_message}", "url": article_url})
            
            if processed_articles_info:
                response_parts = ["Here are some news highlights:\n"]
                for info in processed_articles_info:
                    response_parts.append(f"Quick Summary (3-5 sentences):\n{info['summary']}\n\nSource: {info['url']}")
                
                final_response = "\n\n---\n\n".join(response_parts)
                
                if len(final_response) > 4050: 
                    current_message_part = "Here are some news highlights:\n\n"
                    for idx, info_item in enumerate(processed_articles_info):
                        part_content = f"Quick Summary (3-5 sentences):\n{info_item['summary']}\n\nSource: {info_item['url']}"
                        if idx < len(processed_articles_info) -1:
                             part_content += "\n\n---\n\n"
                        if len(current_message_part) + len(part_content) > 4050:
                            await message_object_to_reply.reply_text(current_message_part)
                            current_message_part = part_content
                        else:
                            current_message_part += part_content
                    if current_message_part: 
                        await message_object_to_reply.reply_text(current_message_part)
                else:
                    await message_object_to_reply.reply_text(final_response)
            else:
                await message_object_to_reply.reply_text("I tried to fetch news but couldn't retrieve or summarize any articles at the moment.")
        
        elif action == "chat":
            await message_object_to_reply.reply_text(data["response"])
        else:
            await message_object_to_reply.reply_text("I'm not sure how to handle that action based on the processed text.")

    except Exception as e:
        print(f"Error in execute_bot_action: {e}")
        if json_response_text_for_error_log: print(f"Gemini's raw response was: '{json_response_text_for_error_log}'")
        await message_object_to_reply.reply_text("Sorry, I had trouble processing that request. Could you try rephrasing?")

async def handle_text_message(update, context):
    user_text = update.message.text
    # print(f"Received text: {user_text}") # Optional: keep for local debugging
    await execute_bot_action(user_text, update.message)

async def handle_voice_message(update, context):
    voice = update.message.voice
    file_id = voice.file_id
    file_path = f"{context.bot_data.get('temp_file_counter', 0)}_{file_id}.oga"
    context.bot_data['temp_file_counter'] = context.bot_data.get('temp_file_counter', 0) + 1
    try:
        voice_file_from_telegram = await context.bot.get_file(file_id)
        await voice_file_from_telegram.download_to_drive(custom_path=file_path)
        # print(f"Downloaded voice file: {file_path}") # Optional: keep for local debugging
        transcribed_text = await audio_to_text(file_path)
        if transcribed_text:
            # print(f"Transcribed text: {transcribed_text}") # Optional: keep for local debugging
            await update.message.reply_text(f"Heard: \"{transcribed_text}\"")
            await execute_bot_action(transcribed_text, update.message)
        else:
            await update.message.reply_text("Sorry, I couldn't understand the audio or there was no speech detected.")
    except Exception as e:
        print(f"Error processing voice message: {e}")
        await update.message.reply_text("Sorry, an error occurred while processing your voice message.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            # print(f"Deleted voice file: {file_path}") # Optional: keep for local debugging

async def start(update, context):
    await update.message.reply_text("AI Assistant activated. Just tell me what you need, by text or voice!")