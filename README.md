# Python Gmail Reader

This project provides Python scripts to automate Gmail inbox management using the Gmail API. It allows you to authenticate securely, extract metadata from unread emails, export them to a CSV file, and batch mark emails as read based on the exported data.

## Features
- Authenticate with Gmail using OAuth2
- Export unread email IDs and subjects to CSV
- Batch mark emails as read from a CSV list

## Setup
1. Clone the repository.
2. Obtain your `credentials.json` from the Google Cloud Console and place it in the project directory (do **not** upload this file to GitHub).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the scripts as needed:
   ```bash
   python get_emails_test.py
   python gmail_mark_read.py
   ```

## Notes
- Token and credential files, logs, and CSV outputs are excluded from version control for security.
- See `.gitignore` for details. 