# google_services.py
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import config # To get GOOGLE_CREDENTIALS_PATH

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/calendar']
creds = None
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = config.GOOGLE_CREDENTIALS_PATH

if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing token: {e}. Deleting token.json to re-authenticate.")
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            creds = None # Force re-authentication
    
    if not creds: # Re-authenticate if refresh failed or no token
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"ERROR: '{CREDENTIALS_FILE}' not found. Please download it from Google Cloud Console.")
            # Potentially raise an exception or exit if critical
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
    if creds: # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

def send_email(to, subject, body):
    if not creds:
        print("Google credentials not loaded. Cannot send email.")
        return False # Indicate failure
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Email sent to {to}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def create_calendar_event(summary, start_time, end_time):
    if not creds:
        print("Google credentials not loaded. Cannot create calendar event.")
        return False # Indicate failure
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Seoul'}, # Adjust timezone if needed
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Seoul'},   # Adjust timezone if needed
        }
        service.events().insert(calendarId='primary', body=event).execute()
        print(f"Calendar event '{summary}' created.")
        return True
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return False