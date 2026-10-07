# raycast-todo

Raycast script commands that send quick text to Google Tasks and Google Calendar.

- **Task** (`add-task.py`): `call mom tmrw 5pm` creates a Google Task with a due date (shows up in Calendar). Shorthand: `tmrw`, `eod`, `tonight`, `3d`, `2h`, `1w`.
- **Block** (`block.py`): `study physics 2-3 fri` creates a Calendar event. No am/pm: 7-11 = am, 12 and 1-6 = pm.

## Setup

1. Create the venv and install deps:
   ```
   python3 -m venv venv && venv/bin/pip install -r requirements.txt
   ```
   Update the shebang on line 1 of both scripts to point at your `venv/bin/python3`.
2. In Google Cloud Console, enable the **Google Tasks API** and **Google Calendar API**, create an OAuth client ID (**Desktop app**), download the JSON as `client_secret.json` in this folder, and add yourself as a test user.
3. Sign in once: `python3 auth.py` (writes `token.json`).
4. In Raycast: Settings, Extensions, Script Commands, Add Directories, pick this folder. Give each command an alias.

`client_secret.json`, `token.json` and `.access.json` are gitignored. Never commit them.
