#!/Users/akshaysanjai/raycast-todo/venv/bin/python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Remind
# @raycast.mode silent

# Optional parameters:
# @raycast.icon ⏰
# @raycast.argument1 { "type": "text", "placeholder": "call mom in 30m (at 5pm, tmrw 9am)" }

import sys, os, re, json, time, pathlib
from datetime import datetime

D = pathlib.Path(__file__).parent
raw = sys.argv[1].strip()

SHORT = [
    (r"\b(tmrw|tmr|tom|tmw)\b", "tomorrow"), (r"\bnxt\b", "next"), (r"\btonight\b", "today 8pm"),
    (r"\b(\d+)\s?d\b", r"in \1 days"), (r"\b(\d+)\s?h\b", r"in \1 hours"),
    (r"\b(\d+)\s?w\b", r"in \1 weeks"), (r"\b(\d+)\s?m(in)?\b", r"in \1 minutes"),
]
text = raw
for pat, rep in SHORT:
    text = re.sub(pat, rep, text, flags=re.I)

import dateparser
S = {"PREFER_DATES_FROM": "future"}
words = text.split()
dt = title = None
for i in range(1, len(words) + 1):            # longest trailing phrase (<=5 words) that parses
    if len(words) - i > 5: continue
    cand = re.sub(r"^(by|at|on|before|for)\s+", "", " ".join(words[i:]), flags=re.I)
    if cand and (d := dateparser.parse(cand, settings=S)):
        dt, when, title = d, cand, " ".join(words[:i])
        break
if dt is None:
    sys.exit("Need a time, e.g. 'call mom in 30m'")
if not re.search(r"\d\s*(am|pm)|\d:\d\d|noon|midnight|today \d|in \d+ (hour|minute)", when, re.I):
    dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)   # date only -> 9am
title = re.sub(r"\s+(by|at|on|before|for|in)$", "", title.strip(), flags=re.I) or "Reminder"

label = dt.strftime("%a %-I:%M%p").lower().replace(":00", "")
if os.environ.get("DRY"):
    print(f"⏰ {title} · {label}"); sys.exit()

f = D / "reminders.json"
items = json.load(open(f)) if f.exists() else []
items.append({"msg": title, "due": dt.timestamp()})
json.dump(items, open(f, "w"))
print(f"⏰ {title} · {label}")
