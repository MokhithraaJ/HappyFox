# Gmail Rule Engine (CLI + GUI Rule Builder)

A small assignment project that:
- Fetches emails from your Gmail inbox via the Gmail API.
- Stores basic fields in a local SQLite DB (`emails.db`).
- Lets you **define rules** (IF/THEN) using a tiny **Tkinter GUI** and saves them to `rules.json`.
- Applies those rules back to Gmail (move to label, mark read/unread).

> You will provide the JSON file for test-cases and a screen recording for the demo. This repo already includes: sample rules, unit tests, and a clear run-book.

---

## Tech Stack
- **Python 3.10+**
- **Google APIs**: `google-api-python-client`, `google-auth`, `google-auth-oauthlib`
- **SQLite** (stdlib)
- **Tkinter** for the rule-builder GUI
- **Pytest** for unit tests

## Folder Structure
```
gmail-rule-engine/
├─ main.py                 # runs: fetch → store → apply rules
├─ rule_builder.py         # GUI to create/append rules into rules.json
├─ rules.json.sample       # sample you can copy to rules.json
├─ requirements.txt
├─ tests/
│  ├─ test_rules_logic.py  # unit tests for rule parsing & matching
│  └─ conftest.py          # pytest fixtures
├─ .gitignore
└─ README.md
```

> **Do not commit secrets.** `credentials.json` and `token.json` are ignored by default.

---

## Prerequisites

1. A Google account with Gmail enabled.
2. Create OAuth client credentials (Desktop application) in Google Cloud Console and download **`credentials.json`**.
3. Enable the **Gmail API** for your project.
4. Install Python 3.10+ and pip.

> Scope used: `https://www.googleapis.com/auth/gmail.modify` (read + modify mailbox).

---

## Installation

```bash
# Clone your fork
git clone <your-fork-url> gmail-rule-engine
cd gmail-rule-engine

# (Recommended) Create a virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Put your Google OAuth file here (the file must be named exactly)
cp /path/to/credentials.json ./credentials.json
```

If your OS is missing Tkinter:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: comes with the official python.org installers
- **Windows**: included in most Python distributions

---

## Usage

### 1) Build rules with the GUI (recommended)
This opens a small window where you can compose conditions and actions and **save** them into `rules.json`.

```bash
python rule_builder.py
```
- Add multiple **conditions** with the `+` button (choose `all`/`any`).
- Add one or more **actions**: *Move Message*, *Mark as Read*, *Mark as Unread*.
- Press **OK** to append your rule to `rules.json` (creates the file if missing).

You can also start from the provided `rules.json.sample`:
```bash
cp rules.json.sample rules.json
```

### 2) Run the engine
```bash
python main.py
```
The first run opens a browser for Google OAuth. After authorization, a local `token.json` is saved for reuse.

What happens:
1. `emails.db` (SQLite) is created if it doesn't exist.
2. Recent inbox messages are pulled (default 50), parsed, and inserted (ignore duplicates).
3. Rules from `rules.json` are evaluated against each stored email.
4. For matches, Gmail actions are applied (add/remove labels, mark read/unread).

---

## Configuration Notes

- **Max results**: adjust `fetch_and_store_emails(service, max_results=50)` inside `main.py` if needed.
- **Relative date**: the `"Date received"` condition accepts values like `2` (days) or `10 days` / `2 months`.
- **Labels**: if a target label (mailbox) doesn’t exist, it will be created on the fly.

---

## Tests

Run all tests:
```bash
pytest -q
```

What’s covered:
- `parse_relative_time` – converts strings like `"2"`, `"10 days"`, `"2 months"` into `timedelta`.
- `condition_matches` – string matching ops and date window logic.
- A thin integration-style test with a **fake Gmail service** to ensure that `apply_rules_and_take_action` attempts the expected Gmail `modify()` calls without touching the network.

> Tests never call real Google APIs. They rely on fakes/mocks and temporary data.

---

## Troubleshooting

- **OAuth consent loop**: delete `token.json` and run again.
- **No Tkinter**: install OS package as shown above.
- **No actions happening**: ensure `rules.json` exists and your rule actually matches some stored emails; try lowering `max_results` and tweaking conditions.

---

## Deliverables Checklist (for reviewers)

- [x] All required features implemented (fetch, store, rules GUI, apply).
- [x] **README** with steps to install and run.
- [x] **Unit tests** included (`pytest`). Bonus: integration-style fake.
- [x] Clear structure; no obvious implementation issues.
- [x] Shareable: push to **GitHub** + include a short **screen recording**:
  - 30–90 seconds overview of architecture and code flow.
  - Live demo: build a rule in GUI, show `rules.json`, run `main.py`, and show the effect in Gmail.
  - Mention the scope (`gmail.modify`) and local storage (`emails.db`).

---

## How to Share the Assignment

1. Push this project to a **public GitHub repo**.
2. Attach your **screen recording** (link in README or repo Releases). Keep it concise:
   - Brief architecture explanation
   - Demo of the GUI rule creation
   - Run the engine and show the Gmail change
3. Include any **JSON test files** provided by reviewers in the repo root as `rules.json` (or reference them in the README).

---

## Security Notes

- Never commit `credentials.json` or `token.json`.
- Use a dedicated Google account for demos.
- The app only reads inbox messages and applies label/read state changes; it does **not** delete content.
