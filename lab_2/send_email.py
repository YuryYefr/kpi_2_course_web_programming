from dotenv import load_dotenv
from os import environ as env
import os
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Set up the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

load_dotenv()
# sender email and password
google_creds = '../google_creds.json'
sender_email = env.get('EMAIL_SENDER')
recipient_email = env.get('RECIPIENT_EMAIL')


def get_gmail_service():
  token_path = 'token.json'
  creds = None
  # login required first time to obtain access
  if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        google_creds, SCOPES)
      creds = flow.run_local_server(port=0)

    with open(token_path, 'w') as token:
      token.write(creds.to_json())

  return build('gmail', 'v1', credentials=creds)


# Build the Gmail service
service = get_gmail_service()

template_path = "../vanilla_page/vanilla_email_page.html"
with open(template_path, "r") as html_file:
  html_content = html_file.read()


def create_message_with_html(sender, to, subject, html_content):
  message = MIMEMultipart()
  message['to'] = to
  message['subject'] = subject
  msg = MIMEText(html_content, 'html')
  message.attach(msg)
  raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
  return {'raw': raw_message}


def send_message(service, sender, to, subject, html_content):
  try:
    message = create_message_with_html(sender, to, subject, html_content)
    sent_message = service.users().messages().send(userId=sender, body=message).execute()
    print(f"Message sent: {sent_message['id']}")
  except Exception as error:
    print(f"An error occurred: {error}")


send_message(service, sender_email, recipient_email, 'Lab 2 rendered html', html_content)
