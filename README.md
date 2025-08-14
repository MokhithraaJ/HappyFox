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
    "description": "Mark interview mails from HR as read",
    "predicate": "all",
    "conditions": [
      {"field": "From", "operator": "contains", "value": "hr@example.com"},
      {"field": "Subject", "operator": "contains", "value": "Interview"}
    ],
    "actions": [
      {"action": "Mark as Read"}
    ]
  }
]
