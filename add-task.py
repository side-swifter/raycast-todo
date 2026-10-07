#!/Users/akshaysanjai/raycast-todo/venv/bin/python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Task
# @raycast.mode silent

# Optional parameters:
# @raycast.icon ✅
# @raycast.argument1 { "type": "text", "placeholder": "call mom tmrw 5pm" }

import sys, re, json, time, pathlib, urllib.parse, urllib.request

D = pathlib.Path(__file__).parent
raw = sys.argv[1].strip()

# Shorthand -> something dateparser understands
SHORT = [
    (r"\b(tmrw|tmr|tom|tmw)\b", "tomorrow"),
    (r"\beod\b", "today 5pm"),
    (r"\btonight\b", "today 8pm"),
    (r"\bnxt\b", "next"),
    (r"\b(\d+)\s?d\b", r"in \1 days"),
    (r"\b(\d+)\s?h\b", r"in \1 hours"),
    (r"\b(\d+)\s?w\b", r"in \1 weeks"),
    (r"\b(\d+)\s?m(in)?\b", r"in \1 minutes"),
]
text = raw
for pat, rep in SHORT:
    text = re.sub(pat, rep, text, flags=re.I)

DATEISH = re.compile(
    r"\d|today|tomorrow|tonight|noon|midnight|morning|evening|next|"
    r"mon|tue|wed|thu|fri|sat|sun|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", re.I)
TIMEISH = re.compile(r"\d\s*(am|pm)|\d:\d\d|noon|midnight|today \d|in \d+ (hour|minute)", re.I)

title, dt, when = text, None, None
if DATEISH.search(text):
    import dateparser
    S = {"PREFER_DATES_FROM": "future"}
    words = text.split()
    for i in range(1, len(words)):          # longest trailing phrase that parses as a date
        cand = " ".join(words[i:])
        cand_clean = re.sub(r"^(by|at|on|before|due|for)\s+", "", cand, flags=re.I)
        if len(words) - i <= 5 and (d := dateparser.parse(cand_clean, settings=S)):
            title = re.sub(r"\s+(by|at|on|before|due|for)$", "", " ".join(words[:i]), flags=re.I)
            dt, when = d, cand_clean
            break
    if dt is None and (d := dateparser.parse(text, settings=S)):
        pass  # whole thing is a date, no title: keep as plain task

body = {"title": title}
if dt:
    body["due"] = dt.strftime("%Y-%m-%dT00:00:00.000Z")
    if TIMEISH.search(when):
        t = dt.strftime("%-I:%M%p").lower().replace(":00", "")
        body["title"] = f"{title} ({t})"
        body["notes"] = f"Due {dt.strftime('%a %b %-d, %-I:%M %p')}"

def access_token():
    cache = D / ".access.json"
    try:
        c = json.load(open(cache))
        if c["exp"] > time.time() + 60:
            return c["token"]
    except Exception:
        pass
    tok = json.load(open(D / "token.json"))
    r = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", urllib.parse.urlencode({
        "client_id": tok["client_id"], "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()))
    json.dump({"token": r["access_token"], "exp": time.time() + r["expires_in"]}, open(cache, "w"))
    return r["access_token"]

urllib.request.urlopen(urllib.request.Request(
    "https://tasks.googleapis.com/tasks/v1/lists/@default/tasks", json.dumps(body).encode(),
    {"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"}))
print("✓ " + body["title"] + (f" · {dt.strftime('%a %b %-d')}" if dt else ""))
