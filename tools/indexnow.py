#!/usr/bin/env python3
"""Tell Bing (and Yandex, Naver, Seznam) that onelifeco.app exists.

WHY THIS FILE EXISTS
Measured 2026-09-04: Google has the site (Search Console, 2026-08-27, "URL is on
Google. Page is indexed"), and Bing has NOTHING. Searched on Bing for the exact
quoted <title> of /luten/, for the bare string "onelifeco.app", and for
site:onelifeco.app. Our own pages came back on none of the three; the domain
query returned only third-party pages that link to us, a YouTube video and the
App Store listing. That is the signature of a domain that has never been crawled,
not one that ranks badly.

Why it matters more than "Bing is small". Bing's index is the retrieval layer
behind Copilot and behind ChatGPT's web search. Section 5 of REVERB.md commits us
to AI visibility, and half of that surface cannot see the pages we wrote for it.

Bing Webmaster Tools needs Reza's login. IndexNow does not: it is a documented
open protocol, it authenticates with a key file we host on our own domain, and
Bing, Yandex, Naver and Seznam share submissions with each other. So this is the
whole fix, done from the shell, with no account.

HOW IT AUTHENTICATES
The key below is also published at https://onelifeco.app/<key>.txt containing
exactly the key and nothing else. The endpoint fetches that file to prove we
control the host. If the file stops being served, submissions start failing with
422, so the .txt file is not optional decoration: do not delete it.

USE
    python3 tools/indexnow.py            # submit every URL in sitemap.xml
    python3 tools/indexnow.py --dry-run  # print what would be sent
Run it after publishing a NEW page. Do not run it on a schedule for unchanged
pages: the protocol is for telling engines about changes, and spamming it with
a static list is what gets a host ignored.

Sources, read 2026-09-04: www.bing.com/indexnow (protocol, key-file rules,
endpoint), www.indexnow.org (the participating engines share submissions).
"""
import argparse
import json
import re
import urllib.request

KEY = "491fd658f60fca0bcb0ae907abc4dc22"
HOST = "onelifeco.app"
ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP = "sitemap.xml"


def urls_from_sitemap(path=SITEMAP):
    xml = open(path, encoding="utf-8").read()
    return re.findall(r"<loc>(.*?)</loc>", xml)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    urls = urls_from_sitemap()
    body = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }
    print(f"{len(urls)} URLs from {SITEMAP}")
    for u in urls:
        print("  ", u)
    if args.dry_run:
        print("\ndry run, nothing sent")
        return

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"\nHTTP {r.status} {r.reason}")
            print(r.read().decode("utf-8", "replace")[:500])
    except urllib.error.HTTPError as e:
        # 200 accepted, 202 accepted but key still being validated,
        # 400 bad body, 403 key not valid, 422 URL/key mismatch, 429 too many.
        print(f"\nHTTP {e.code} {e.reason}")
        print(e.read().decode("utf-8", "replace")[:500])


if __name__ == "__main__":
    main()
