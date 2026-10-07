#!/Users/akshaysanjai/raycast-todo/venv/bin/python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Block
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🗓
# @raycast.argument1 { "type": "text", "placeholder": "study physics 2-3 (fri 6-7pm, gym 7am-8)" }

import sys, os, re, json, time, pathlib, urllib.parse, urllib.request
from datetime import datetime, timedelta

D = pathlib.Path(__file__).parent
raw = sys.argv[1].strip()

SHORT = [(r"\b(tmrw|tmr|tom|tmw)\b", "tomorrow"), (r"\bnxt\b", "next")]
text = raw
for pat, rep in SHORT:
    text = re.sub(pat, rep, text, flags=re.I)

def to24(h, m, mer):
    h = int(h)
    if mer == "pm" and h != 12: h += 12
    if mer == "am" and h == 12: h = 0
    return h * 60 + int(m or 0)

def guess(h):                      # no am/pm given: 7-11 -> am, 12 & 1-6 -> pm
    return "am" if 7 <= int(h) <= 11 else "pm"

RANGE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:-|–|to|until)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.I)
SINGLE = re.compile(r"(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b|\bat\s+(\d{1,2})(?::(\d{2}))?\b", re.I)

start = end = None
if m := RANGE.search(text):
    h1, m1, a1, h2, m2, a2 = m.groups()
    a1, a2 = (a1 or "").lower() or None, (a2 or "").lower() or None
    if not a1 and not a2: a2 = guess(h2); a1 = a2 if int(h1) <= int(h2) or int(h1) == 12 else "am"
    elif not a1: a1 = a2
    elif not a2: a2 = a1
    start, end = to24(h1, m1, a1), to24(h2, m2, a2)
    if end <= start and not m.group(3):   # e.g. 11-1 => 11am-1pm
        end += 12 * 60 if end + 12 * 60 > start else 0
    if end <= start: end += 12 * 60
    text = text[:m.start()] + " " + text[m.end():]
elif m := SINGLE.search(text):
    if m.group(1): start = to24(m.group(1), m.group(2), m.group(3).lower())
    else: start = to24(m.group(4), m.group(5), guess(m.group(4)))
    end = start + 60
    text = text[:m.start()] + " " + text[m.end():]
else:
    sys.exit("Need a time, e.g. 'study physics 2-3'")

import dateparser
S = {"PREFER_DATES_FROM": "future"}
words = text.split()
day, title = datetime.now().date(), " ".join(words)
for i in range(max(len(words) - 3, 0), len(words)):   # trailing date phrase, up to 3 words
    cand = re.sub(r"^(on|by|for)\s+", "", " ".join(words[i:]), flags=re.I)
    if (d := dateparser.parse(cand, settings=S)):
        day, title = d.date(), " ".join(words[:i])
        break
title = re.sub(r"\s+(on|at|by|for|from)$", "", title.strip(), flags=re.I) or "Busy"

base = datetime(day.year, day.month, day.day).astimezone()
s = base + timedelta(minutes=start)
e = base + timedelta(minutes=end)
body = {"summary": title, "start": {"dateTime": s.isoformat()}, "end": {"dateTime": e.isoformat()}}
fmt = lambda d, f: d.strftime(f).replace(":00", "").lower()
label = f"✓ {title} · {fmt(s, '%a %b %-d, %-I:%M%p')}–{fmt(e, '%-I:%M%p')}"

if os.environ.get("DRY"):
    print(label); sys.exit()

def access_token():
    cache = D / ".access.json"
    try:
        c = json.load(open(cache))
        if c["exp"] > time.time() + 60: return c["token"]
    except Exception: pass
    tok = json.load(open(D / "token.json"))
    r = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", urllib.parse.urlencode({
        "client_id": tok["client_id"], "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()))
    json.dump({"token": r["access_token"], "exp": time.time() + r["expires_in"]}, open(cache, "w"))
    return r["access_token"]

urllib.request.urlopen(urllib.request.Request(
    "https://www.googleapis.com/calendar/v3/calendars/primary/events", json.dumps(body).encode(),
    {"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"}))
print(label)
