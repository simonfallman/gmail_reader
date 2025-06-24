import os
import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials  # Corrected import

# Scopes define the permissions the app will have on your Gmail account
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    # Check if token.json exists (contains saved credentials)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def list_messages(service, query='', max_results=100):
    """List messages matching a specific query and handle pagination."""
    try:
        # Initialize the list of emails
        messages = []
        # The API request to get the list of emails
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        
        # Collect messages from the response
        while 'messages' in results:
            messages.extend(results['messages'])
            
            # If there are more emails, fetch the next page
            if 'nextPageToken' in results:
                page_token = results['nextPageToken']
                results = service.users().messages().list(userId='me', q=query, pageToken=page_token, maxResults=max_results).execute()
            else:
                break
        
        return messages
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_email_subject(service, msg_id):
    """Fetch and return the subject of an email."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='metadata').execute()
        headers = message['payload'].get('headers', [])
        for header in headers:
            if header['name'].lower() == 'subject':
                return header['value']
        return "(No Subject)"
    except Exception as e:
        print(f"An error occurred while fetching email subject: {e}")
        return "(Error Fetching Subject)"

def save_to_csv(service, messages):
    """Save the list of emails to a CSV file."""
    with open('emails.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Email ID', 'Subject']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, msg in enumerate(messages, start=1):
            subject = get_email_subject(service, msg['id'])
            writer.writerow({'Email ID': msg['id'], 'Subject': subject})
            
            # Print progress for every 100 emails processed
            if i % 100 == 0:
                print(f"Processed {i}/{len(messages)} emails...")
        
    print(f"All {len(messages)} emails have been saved to 'emails.csv'.")


def main():
    service = authenticate_gmail()

    # Fetch unread emails older than 1 months
    query = "is:unread"
    print(f"Querying for emails with query: {query}")
    
    messages = list_messages(service, query=query, max_results=100)

    if not messages:
        print("No unread emails found.")
        return

    print(f"Found {len(messages)} unread emails.")
    
    # Save the emails to a CSV file, passing the service object
    save_to_csv(service, messages)

    print("Emails have been saved to 'emails.csv'.")

if __name__ == '__main__':
    main()
