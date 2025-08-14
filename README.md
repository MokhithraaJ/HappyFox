# Gmail Rules Automation

This project automates Gmail email processing based on user-defined rules. You can create rules using a simple GUI, store them in a JSON file (`rules.json`), and then run the automation script to fetch, store, and process Gmail messages according to those rules.

---

## Features

- **Fetch Emails from Gmail** using Google API.
- **Store Emails Locally** in an SQLite database (`emails.db`).
- **Rule-Based Processing** — match on `From`, `Subject`, `Date`, and perform actions.
- **Actions Supported:**
  - Move message to label/folder
  - Mark email as Read or Unread
- **Interactive GUI Rule Builder** to easily create rules and save them as `rules.json`.

---

## Requirements

- Python **3.8+**
- A Google Cloud Project with the **Gmail API** enabled
- OAuth 2.0 desktop app credentials (`credentials.json`)

---

## Installation

1. **Clone the Repository**
