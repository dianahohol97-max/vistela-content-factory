"""Sync input media from Dropbox into input/ before a build.

Runs on the GitHub Actions runner (which can reach Dropbox), NOT in the design
sandbox. Uses refresh-token auth so it keeps working for the daily cron:
Adrian sets three repo secrets once —
  DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN
(create a Dropbox app, generate a refresh token). If they're absent the script
exits quietly, so the build still runs on whatever is committed.

Folder mapping (Dropbox -> local):
  /весільні відео            -> input/wedding-scenes
  /відео продуктів           -> input/templates      (subfolders preserved for
                                                       product-type detection)
  /Personalise with me       -> input/personalize
"""
import json
import os
import sys
import urllib.request
import urllib.parse

APP_KEY = os.environ.get("DROPBOX_APP_KEY")
APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

MAPPING = [
    ("/весільні відео", "input/wedding-scenes"),
    ("/відео продуктів", "input/templates"),
    ("/Personalise with me", "input/personalize"),
]
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".webm")


def _access_token():
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    }).encode()
    req = urllib.request.Request("https://api.dropbox.com/oauth2/token", data=data)
    with urllib.request.urlopen(req) as r:
        return json.load(r)["access_token"]


def _list_folder(token, path):
    entries, cursor = [], None
    while True:
        if cursor is None:
            url = "https://api.dropboxapi.com/2/files/list_folder"
            body = {"path": path, "recursive": True}
        else:
            url = "https://api.dropboxapi.com/2/files/list_folder/continue"
            body = {"cursor": cursor}
        req = urllib.request.Request(url, data=json.dumps(body).encode())
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as r:
                res = json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  ! list_folder {path}: {e.read().decode()[:200]}")
            return entries
        entries += res.get("entries", [])
        if not res.get("has_more"):
            return entries
        cursor = res["cursor"]


def _download(token, dbx_path, dest):
    req = urllib.request.Request("https://content.dropboxapi.com/2/files/download")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Dropbox-API-Arg", json.dumps({"path": dbx_path}))
    with urllib.request.urlopen(req) as r:
        data = r.read()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)


def main():
    if not (APP_KEY and APP_SECRET and REFRESH_TOKEN):
        print("Dropbox secrets not set — skipping sync (using committed inputs).")
        return
    token = _access_token()
    total = 0
    for dbx_root, local_root in MAPPING:
        for e in _list_folder(token, dbx_root):
            if e.get(".tag") != "file" or not e["name"].lower().endswith(VIDEO_EXT):
                continue
            rel = e["path_display"][len(dbx_root):].lstrip("/")
            dest = os.path.join(local_root, rel)
            if os.path.exists(dest):
                continue
            try:
                _download(token, e["path_lower"], dest)
                total += 1
                print(f"  + {dest}")
            except Exception as ex:  # noqa
                print(f"  ! {dest}: {ex}")
    print(f"Dropbox sync done — {total} new file(s).")


if __name__ == "__main__":
    main()
