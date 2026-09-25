#!/usr/bin/env python3
"""Flip the Cassette press kit from "in review" to "released", once, on release day.

WHY THIS FILE EXISTS
/cassette/press went live on 2026-09-16 while Cassette was still Waiting for
Review, so its Release row says the app was submitted and the date will follow.
Reza asked for that row to update itself the day Apple approves the app, and for
the App Store link to be confirmed working first. This is the whole job, written
down so a scheduled run cannot improvise the copy.

WHAT COUNTS AS RELEASED
Apple's public lookup API returning Cassette. Approval alone is not enough: the
version is set to release automatically after approval, and the listing can take
a while to appear after that, so the lookup (not App Store Connect's state) is
the moment the App Store link actually works for a reader.

    python3 tools/cassette_release.py check            # print the status, change nothing
    python3 tools/cassette_release.py apply            # edit + commit if released
    python3 tools/cassette_release.py apply --push     # ... and push (deploys)

Idempotent: once the press kit says "Released", apply does nothing.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.request
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESS = os.path.join(ROOT, "cassette", "press.html")
CLAUDE_MD = os.path.join(ROOT, "CLAUDE.md")
APP_ID = 6812001404
LOOKUP = f"https://itunes.apple.com/lookup?id={APP_ID}&country=us"

OLD_RELEASE = ("<tr><td>Release</td><td>Submitted to the App Store on Wednesday, September 16, 2026. "
               "Release date to follow App Review</td></tr>")
# The press kit shows the store address as plain text until release (a link to a
# listing that does not exist yet is a 404 for a journalist), then becomes a link.
OLD_STORE = ('apps.apple.com/app/id6812001404 (link goes live on release day)</td>')
NEW_STORE = ('<a href="https://apps.apple.com/app/id6812001404">apps.apple.com/app/id6812001404</a> (live now)</td>')
# The site itself: cassette_ld.RELEASED gates every store link on /cassette, the
# nav pill and the structured data, and llms.txt states the app's status.
LD = os.path.join(ROOT, "cassette_ld.py")
LLMS = os.path.join(ROOT, "llms.txt")
OLD_FLAG = "RELEASED = False"
OLD_LLMS_STATUS = "Submitted to the App Store and awaiting release."
OLD_LLMS_REQ = "Requirements: any iPhone on iOS 17 or later."
OUTPUTS = ["index.html", "luten/index.html", "cassette/index.html", "apps/spend/index.html",
           "about/index.html", "contact/index.html", "termsofservice/index.html",
           "privacypolicy/index.html"]
OLD_COMMENT = ('UPDATE THE\n     "Release" ROW the day App Review approves the app.')
OLD_NOTE = ('**Update\n  its "Release" row the day App Review approves Cassette**; until then it says the\n'
            '  app was submitted on 2026-09-16 with the date to follow.')


def lookup():
    with urllib.request.urlopen(LOOKUP, timeout=30) as r:
        data = json.load(r)
    hits = [x for x in data.get("results", []) if x.get("trackId") == APP_ID]
    return hits[0] if hits else None


def store_page_ok(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def release_day(app):
    # Apple stamps a first release at midnight Pacific; name the day as Apple does.
    stamp = datetime.datetime.fromisoformat(app["releaseDate"].replace("Z", "+00:00"))
    day = stamp.astimezone(ZoneInfo("America/Los_Angeles"))
    return day.strftime("%A, %B ") + str(day.day) + day.strftime(", %Y"), day.date().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["check", "apply"])
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    press = open(PRESS, encoding="utf-8").read()
    if "<tr><td>Release</td><td>Released " in press:
        print("ALREADY_RELEASED press kit already updated; nothing to do")
        return 0

    app = lookup()
    if not app:
        print("NOT_LIVE Cassette is not in the public App Store lookup yet")
        return 0
    url = app.get("trackViewUrl", "")
    if not store_page_ok(url):
        print(f"LISTED_BUT_PAGE_NOT_READY lookup has Cassette but {url} did not return 200 yet")
        return 0
    human, iso = release_day(app)
    print(f"LIVE version {app.get('version')} released {human} ({iso}) {url}")
    if args.mode == "check":
        return 0

    for needle, name in ((OLD_RELEASE, "release row"), (OLD_STORE, "App Store row"), (OLD_COMMENT, "comment")):
        if needle not in press:
            print(f"ABORT the {name} in cassette/press.html no longer matches; update it by hand")
            return 2
    press = press.replace(OLD_RELEASE, f"<tr><td>Release</td><td>Released {human}</td></tr>")
    press = press.replace(OLD_STORE, NEW_STORE)
    press = press.replace(OLD_COMMENT, f'The "Release" row was set on\n     release day ({iso}) by tools/cassette_release.py.')
    ld = open(LD, encoding="utf-8").read()
    llms = open(LLMS, encoding="utf-8").read()
    for text, needle, name in ((ld, OLD_FLAG, "RELEASED flag in cassette_ld.py"),
                               (llms, OLD_LLMS_STATUS, "Cassette status line in llms.txt"),
                               (llms, OLD_LLMS_REQ, "Cassette requirements line in llms.txt")):
        if text.count(needle) != 1:
            print(f"ABORT the {name} no longer matches; update it by hand")
            return 2
    open(PRESS, "w", encoding="utf-8").write(press)
    open(LD, "w", encoding="utf-8").write(ld.replace(OLD_FLAG, "RELEASED = True"))
    llms = llms.replace(OLD_LLMS_STATUS, "Available now on the App Store for iPhone.")
    llms = llms.replace(OLD_LLMS_REQ, OLD_LLMS_REQ + "\n\nDownload: https://apps.apple.com/us/app/cassette-ai-note-taker/id6812001404")
    open(LLMS, "w", encoding="utf-8").write(llms)
    # Rebuild so every store link, badge and QR on /cassette comes back.
    subprocess.run([sys.executable, os.path.join(ROOT, "seo-build.py")], check=True, cwd=ROOT,
                   capture_output=True, text=True)

    md = open(CLAUDE_MD, encoding="utf-8").read()
    if OLD_NOTE in md:
        md = md.replace(OLD_NOTE, f'Its "Release" row was\n  set on release day ({iso}) by `tools/cassette_release.py`.')
        open(CLAUDE_MD, "w", encoding="utf-8").write(md)

    git = lambda *a: subprocess.run(["git", "-C", ROOT, *a], check=True, capture_output=True, text=True).stdout
    git("add", "cassette/press.html", "CLAUDE.md", "cassette_ld.py", "llms.txt", *OUTPUTS)
    git("commit", "-q", "-m", f"Cassette is released ({human}): store links, press kit and llms.txt\n\n"
        f"Set by tools/cassette_release.py once Apple's lookup listed Cassette and its App Store page\n"
        f"answered: {url}\n\nCo-Authored-By: Claude Opus 5 <noreply@anthropic.com>")
    print("COMMITTED", git("log", "--oneline", "-1").strip())
    if args.push:
        git("pull", "-q", "--rebase", "origin", "main")
        git("push", "-q", "origin", "main")
        print("PUSHED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
