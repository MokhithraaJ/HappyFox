import os
import sqlite3
import json
import base64
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API Scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
DB_FILE = 'emails.db'

# ======================= DB SETUP =========================
def create_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            threadId TEXT,
            sender TEXT,
            recipients TEXT,
            subject TEXT,
            date TEXT,
            snippet TEXT,
            labelIds TEXT,
            body TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ======================= GMAIL API =========================
def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# ======================= FETCH EMAILS =========================
def fetch_and_store_emails(service, max_results=50):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX'], maxResults=max_results
    ).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(
            userId='me', id=msg_id, format='full'
        ).execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])

        def get_header(name):
            for h in headers:
                if h['name'].lower() == name.lower():
                    return h['value']
            return None

        sender = get_header('From')
        recipients = get_header('To')
        subject = get_header('Subject')
        date = get_header('Date')
        snippet = message.get('snippet', '')
        labelIds = ','.join(message.get('labelIds', []))

        # Extract simple text/plain body
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload.get('body', {}).get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        cursor.execute('''
            INSERT OR IGNORE INTO emails
            (id, threadId, sender, recipients, subject, date, snippet, labelIds, body)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, message.get('threadId'), sender, recipients, subject, date, snippet, labelIds, body))

    conn.commit()
    conn.close()

# ======================= RULE LOADING =========================
def load_rules():
    try:
        with open('rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# ======================= UTILS =========================
def parse_relative_time(value):
    """
    Converts "10 days", "2 months", or "7" (defaults days) into timedelta.
    """
    value = value.strip()
    if value.isdigit():
        return timedelta(days=int(value))
    match = re.match(r'(\d+)\s*(day|days|month|months)', value.lower())
    if not match:
        return None
    num = int(match.group(1))
    return timedelta(days=num * 30) if 'month' in match.group(2) else timedelta(days=num)

# ======================= MATCHING LOGIC =========================
def condition_matches(cond, email):
    field = cond['field'].strip().lower()
    op = cond['operator'].strip().lower()
    val = str(cond['value']).strip().lower()

    # Handle Date fields separately
    if field in ('received', 'date received'):
        try:
            email_date = parsedate_to_datetime(email['date'])
            if email_date.tzinfo is None:
                email_date = email_date.replace(tzinfo=timezone.utc)
        except Exception:
            return False
        delta = parse_relative_time(cond['value'])
        if not delta:
            return False
        age = datetime.now(timezone.utc) - email_date
        return (
            (op in ('is less than', 'less than') and age <= delta) or
            (op in ('is greater than', 'greater than') and age > delta)
        )

    # Extract value from email record
    if field == 'from':
        field_value = (email.get('from') or '').lower()
    elif field == 'to':
        field_value = (email.get('to') or '').lower()
    elif field == 'subject':
        field_value = (email.get('subject') or '').lower()
    elif field == 'message':
        field_value = (email.get('message') or '').lower()
    else:
        field_value = (email.get(field, '') or '').lower()

    # String operators
    return (
        (op == 'contains' and val in field_value) or
        (op == 'does not contain' and val not in field_value) or
        (op == 'equals' and val == field_value) or
        (op == 'does not equal' and val != field_value)
    )

# ======================= LABEL HANDLING =========================
def get_label_id(service, label_name):
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']
    return None

# ======================= APPLY RULES =========================
def apply_rules_and_take_action(service):
    rules = load_rules()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails')

    for row in cursor.fetchall():
        email = {
            'id': row[0],
            'threadId': row[1],
            'from': row[2],
            'to': row[3],
            'subject': row[4],
            'date': row[5],
            'snippet': row[6],
            'labels': row[7],
            'message': row[8]
        }

        for rule in rules:
            predicate = rule.get('predicate', 'all').lower()
            conditions = rule.get('conditions', [])
            actions = rule.get('actions', [])

            matches = [condition_matches(c, email) for c in conditions]

            if (predicate == 'all' and all(matches)) or (predicate == 'any' and any(matches)):
                for action_item in actions:
                    act = action_item.get('action', '').strip().lower()

                    if act == 'mark as read':
                        service.users().messages().modify(
                            userId='me', id=email['id'],
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()

                    elif act == 'mark as unread':
                        service.users().messages().modify(
                            userId='me', id=email['id'],
                            body={'addLabelIds': ['UNREAD']}
                        ).execute()

                    elif act == 'move message':
                        target_mailbox = action_item.get('mailbox', 'Inbox')
                        label_id = get_label_id(service, target_mailbox)
                        if not label_id:
                            lbl = service.users().labels().create(
                                userId='me',
                                body={
                                    'name': target_mailbox,
                                    'labelListVisibility': 'labelShow',
                                    'messageListVisibility': 'show'
                                }
                            ).execute()
                            label_id = lbl['id']
                        service.users().messages().modify(
                            userId='me', id=email['id'],
                            body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
                        ).execute()

    conn.close()

# ======================= MAIN =========================
def main():
    create_db()
    service = get_gmail_service()
    fetch_and_store_emails(service)
    apply_rules_and_take_action(service)

if __name__ == '__main__':
    main()
