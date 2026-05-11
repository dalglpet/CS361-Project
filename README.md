# Password Generator

A terminal-based password generator with login, session management, cloud backup, and CSV export. Built in Python.

---

## What It Does

- Generates secure, random passwords with custom length and character type settings
- Saves passwords into named lists you can manage across the session
- Backs up lists to the cloud and restores them by backup ID
- Exports lists to CSV
- Requires login and validates your session throughout use

---

## Requirements

- Python 3
- `requests` library (`pip install requests`)

Four microservices must be running before you launch the app:

| Service | Default URL |
|---|---|
| Login | `http://127.0.0.1:5000` |
| Session Token | `http://127.0.0.1:5003` |
| Export | `http://127.0.0.1:5002` |
| Data Backup | `http://127.0.0.1:8080` |

---

## How to Run

```bash
python password_generator.py
```

---

## How to Use

1. **Log in** or create an account at the login screen.
2. From the main menu, choose **Generate passwords**.
3. Name your list, set a length (5-100), and choose character types.
4. Generate as many passwords as you want. Each one is saved to your list automatically.
5. Go to **Password lists** to back up, export, or restore a list.

---

## Tips

- Passwords 12+ characters with all character types are strongest.
- Save your **backup ID** after a cloud backup. You need it to restore.
- Your session expires after a period of inactivity. You will be prompted to log in again.

---

## Project Structure

```
password_generator.py   # Main application (all logic lives here)
```

All microservices are external and must be started separately.

---

*Built by Peter Dalgleish*
