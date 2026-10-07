#!/usr/bin/env python3
"""One-time Google sign-in. Reads client_secret.json, writes token.json."""
import json, http.server, urllib.parse, urllib.request, webbrowser, pathlib

D = pathlib.Path(__file__).parent
c = json.load(open(D / "client_secret.json"))
c = c.get("installed") or c.get("web")
PORT = 8765
REDIRECT = f"http://localhost:{PORT}"

url = c["auth_uri"] + "?" + urllib.parse.urlencode({
    "client_id": c["client_id"], "redirect_uri": REDIRECT, "response_type": "code",
    "scope": "https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar.events",
    "access_type": "offline", "prompt": "consent",
})
code = {}

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        code["v"] = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("code", [None])[0]
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Done. You can close this tab.")
    def log_message(self, *a): pass

webbrowser.open(url)
srv = http.server.HTTPServer(("localhost", PORT), H)
srv.handle_request()

data = urllib.parse.urlencode({
    "code": code["v"], "client_id": c["client_id"], "client_secret": c["client_secret"],
    "redirect_uri": REDIRECT, "grant_type": "authorization_code",
}).encode()
tok = json.load(urllib.request.urlopen(c["token_uri"], data))
json.dump({"client_id": c["client_id"], "client_secret": c["client_secret"],
           "refresh_token": tok["refresh_token"]}, open(D / "token.json", "w"))
print("Saved token.json")
