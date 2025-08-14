# Gmail Rule Engine

## 📌 About the Project
This project connects to your Gmail account using the **Gmail API**, downloads recent emails, stores them in a local SQLite database, and applies **custom rules** to automatically take actions like:
- Moving emails to a specific label
- Marking them as read or unread

You can create these rules using the **Tkinter-based GUI** (`rule_builder.py`), which stores them in a `rules.json` file. The main script (`main.py`) reads these rules, checks your emails, and performs the defined actions.

---

## 🛠 Tech Stack
- **Python 3.10+**
- **Gmail API** with:
  - `google-api-python-client`
  - `google-auth`
  - `google-auth-oauthlib`
- **SQLite** (built-in Python database)
- **Tkinter** for GUI rule creation
- **JSON** for storing rules

---

## 📜 Rules
Rules are stored in `rules.json`.  
A rule consists of:
- **Conditions**: When the rule should trigger (e.g., "From contains example.com" AND "Subject contains Invoice")
- **Actions**: What to do when conditions match (e.g., "Mark as Read", "Move to Label")

Example `rules.json`:
```json
[
    {
        "description": "Altering Google mail",
        "predicate": "all",
        "conditions": [
            {
                "field": "From",
                "operator": "contains",
                "value": "Google"
            },
            {
                "field": "Subject",
                "operator": "contains",
                "value": "Security alert"
            },
            {
                "field": "Date received",
                "operator": "is less than",
                "value": "2"
            }
        ],
        "actions": [
            {
                "action": "Move Message",
                "mailbox": "Trash"
            },
            {
                "action": "Mark as Read"
            }
        ]
    }
]
```

---

## 🚀 Steps to Run the Project

1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

2. **Create and Activate a Virtual Environment** (recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install Required Dependencies**
```bash
pip install -r requirements.txt
```
Or directly:
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

4. **Enable Gmail API and Get `credentials.json`**
   - Go to **[Google Cloud Console](https://console.cloud.google.com/)**
   - Create a new project (or select an existing one)
   - Go to **APIs & Services → Library**
   - Search for **Gmail API** and click **Enable**
   - Go to **APIs & Services → Credentials**
   - Click **Create Credentials → OAuth client ID**
   - Select **Desktop app**
   - Download the JSON file, rename it to `credentials.json`, and place it in your project folder

5. **Create Rules Using the GUI**
```bash
python rule_builder.py
```
   - Add conditions and actions
   - Click **OK** to save
   - This will create/append to `rules.json`

6. **Run the Main Script**
```bash
python main.py
```
   - First run will open a browser for Google OAuth login
   - After authorization, `token.json` will be saved for reuse
   - Emails will be fetched into `emails.db` and rules applied

---

## 📹 Demonstration
Refer to the provided **screen recording** for:
- Creating rules via `rule_builder.py`
- Running `main.py` to fetch and process emails
- Live Gmail changes after applying rules

---

## 📝 Quick Commands (Copy-Paste Friendly)
```bash
git clone <your-repo-url>
cd <your-repo-folder>
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
# OR
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# Add credentials.json to project folder
python rule_builder.py
python main.py
```

