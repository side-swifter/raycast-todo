#!/usr/bin/python3
# Run by launchd every 30s: fires due reminders as macOS notifications.
import json, time, pathlib, subprocess
f = pathlib.Path(__file__).parent / "reminders.json"
if not f.exists(): raise SystemExit
items = json.load(open(f)); now = time.time()
due = [i for i in items if i["due"] <= now]
if due:
    json.dump([i for i in items if i["due"] > now], open(f, "w"))
    for i in due:
        late = " (missed)" if now - i["due"] > 120 else ""
        msg = i["msg"].replace("\\", "\\\\").replace('"', '\\"') + late
        subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "⏰ Reminder" sound name "Glass"'])
