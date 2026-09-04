#!/usr/bin/env python3
"""Regenerate the App Store QR on the Luten page.

WHY THIS FILE EXISTS

`luten/luten-qr.svg` was a build output with no source. Nobody could tell what
URL it encoded without decoding the image, and changing it meant hand-editing
generated path data. That is exactly the trap CLAUDE.md warns about with the
page files, so the QR now has a generator like everything else.

WHY THE URL CARRIES ?ct=

App Store Connect's analytics carry a Campaign column, and on 2026-09-03 it was
empty on every row, because not one App Store link we publish carried a campaign
token. Every tap from the website into the App Store was landing in an
unattributed "Web referrer" bucket. `ct` is the campaign token Apple reads into
that column.

Each surface gets its own token so they stay separable:

    web_hero    the button above the fold
    web_badge   the Download on the App Store badge, lower down
    web_qr      THIS code, scanned with a phone camera

web_qr is the one worth watching. The hero QR was added on 2026-09-03 because
the page takes almost no iPhone traffic (3 of 76 pageviews) while its only
call to action sent desktop visitors to a page they cannot install from. This
token is how we find out whether that actually converts anyone, rather than
assuming it does.

    python3 tools/make_qr.py
"""
import segno

# Same palette as the surrounding card in styles.css (.qr-code background is
# #f6f3ec), so the code sits flush on the cream tile rather than on white.
DARK = "#15110a"
LIGHT = "#f6f3ec"
SCALE = 10

URL = ("https://apps.apple.com/us/app/luten-sleep-focus-sounds/"
       "id6777673392?ct=web_qr")
OUT = "luten/luten-qr.svg"


def main() -> None:
    # error='m' keeps the code readable if the cream tile is partly obscured,
    # without inflating the module count enough to hurt at 104px.
    qr = segno.make(URL, error="m")
    qr.save(OUT, scale=SCALE, dark=DARK, light=LIGHT,
            svgclass="segno", lineclass="qrline", xmldecl=True)
    print(f"wrote {OUT}  version={qr.version}  encodes {URL}")


if __name__ == "__main__":
    main()
