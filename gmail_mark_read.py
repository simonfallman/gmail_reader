import os
import base64
import csv
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials  # Correct import for Credentials

# Scopes define the permissions the app will have on your Gmail account
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Set up logging
logging.basicConfig(filename='gmail_mark_read.log', level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        # Use the correct method to load credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Authenticate user if no valid credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def mark_as_read(service, msg_id):
    """Mark an email as read by modifying its labels."""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        logger.info(f"Email with ID {msg_id} marked as read.")
        print(f"Email with ID {msg_id} marked as read.")
    except Exception as e:
        logger.error(f"An error occurred for email ID {msg_id}: {e}")
        print(f"An error occurred: {e}")

def load_emails_from_csv(file_path):
    """Load emails from a CSV file."""
    email_ids = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip the header row
        next(reader)
        # Assuming the email ID is in the first column of CSV
        for row in reader:
            if row:  # Make sure the row is not empty
                email_ids.append(row[0])  # Adjust if email IDs are in a different column
    return email_ids

def main():
    # Authenticate with Gmail API
    service = authenticate_gmail()

    # Load the email IDs from the CSV file
    email_ids = load_emails_from_csv('emails.csv')

    if not email_ids:
        logger.warning("No email IDs found in the CSV file.")
        print("No email IDs found in the CSV file.")
        return

    logger.info(f"Found {len(email_ids)} emails to mark as read.")
    print(f"Found {len(email_ids)} emails to mark as read.")
    
    # Mark each email as read
    for msg_id in email_ids:
        mark_as_read(service, msg_id)

    logger.info("All emails from CSV have been processed.")
    print("All emails from CSV have been processed.")

if __name__ == '__main__':
    main()
