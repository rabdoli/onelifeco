#!/usr/bin/env python3
"""Regenerate every asset the /cassette page uses.

Same rule as make_qr.py: nothing under cassette/ is hand-made, so nobody has to
guess what an image encodes or where it came from.

SOURCES (outside this repo, in the Cassette app project)

    APP/Cassette/Resources/AppIcon.icon      the shipped Liquid Glass icon,
                                             rendered with Icon Composer's ictool
    APP/AppStore/screenshots/captures/       raw 1320x2868 captures of the current
                                             build, the same ones behind the App
                                             Store cards
    APP/AppStore/screenshots/samples/        the synthesized "Website relaunch
                                             check-in" recording; its loudness
                                             envelope draws the hero waveform

OUTPUTS

    cassette/cassette-icon.png     the page mark (320px, shown at up to 148px)
    cassette/og-cassette.png       1200x630 social card, laid out like og-luten.png
    cassette/cassette-qr.svg       App Store QR, ct=web_qr
    cassette/screen-*.webp         five captures for the gallery
    cassette/media/                the press kit downloads: 1024px icon, the five
                                   App Store cards and the five plain screens at
                                   full resolution, plus card thumbnails
    icons/cassette-*.svg           feature orbs, drawn like icons/orb-*.svg
    (stdout)                       the waveform envelope, pasted into script.js

WHY THE ACCENTS ARE WHAT THEY ARE
The five orb colours are the per-card accents of the App Store screenshots
(AppStore/screenshots/compose.py): record red, notes amber, transcript teal,
email coral, shelf sand. The page, the store listing and the app agree.

    python3 tools/make_cassette_assets.py
"""
import array
import os
import subprocess

import segno
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "/Users/rezaabdoli/Cassette/design_handoff_cassette_recorder/Cassette"
ICTOOL = "/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool"
OUT = os.path.join(ROOT, "cassette")
ICONS = os.path.join(ROOT, "icons")

APP_STORE = "https://apps.apple.com/us/app/cassette-ai-note-taker/id6812001404"

# (slug, top colour, bottom colour, shadow colour, glyph markup in a 24x24 box)
ORBS = [
    ("record", "#ff6a5e", "#c42a2a", "#7a1414",
     '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2" opacity="0.55"/>'
     '<circle cx="12" cy="12" r="4.6" fill="currentColor"/>'),
    ("transcript", "#5fe3bd", "#1f9a78", "#0c5a45",
     '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
     '<path d="M4 7h2.5M4 12h2.5M4 17h2.5" opacity="0.55"/>'
     '<path d="M9.5 7H20M9.5 12h8M9.5 17h9.5"/></g>'),
    ("notes", "#ffcc6b", "#d98a1e", "#7e4a08",
     '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
     '<path d="M4.5 7.2l1.7 1.7 3-3"/><path d="M4.5 13.2l1.7 1.7 3-3"/>'
     '<path d="M12.5 7.5H20M12.5 13.5H20"/><path d="M12.5 19H17" opacity="0.55"/></g>'
     '<circle cx="6.6" cy="19" r="1.3" fill="currentColor" opacity="0.55"/>'),
    ("email", "#ff9170", "#d44f2e", "#7c2610",
     '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
     '<rect x="3.5" y="6" width="17" height="12.5" rx="2.4"/><path d="M4.6 7.6l7.4 5.6 7.4-5.6"/></g>'),
    ("shelf", "#f1d79c", "#b8924a", "#6a5020",
     '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
     '<circle cx="10.5" cy="10.5" r="5.6"/><path d="M14.8 14.8l4.7 4.7"/></g>'),
    ("export", "#a9b6ff", "#5a6ad0", "#2c3478",
     '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
     '<path d="M12 4v10.5"/><path d="M8.4 7.6L12 4l3.6 3.6"/>'
     '<path d="M8 11H6.5A2.5 2.5 0 0 0 4 13.5v4A2.5 2.5 0 0 0 6.5 20h11a2.5 2.5 0 0 0 2.5-2.5v-4A2.5 2.5 0 0 0 17.5 11H16"/></g>'),
    ("private", "#8fd3ff", "#2f86c4", "#123f66",
     '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
     '<rect x="5" y="10.5" width="14" height="10" rx="2.4"/><path d="M8.2 10.5V7.8a3.8 3.8 0 0 1 7.6 0v2.7"/></g>'
     '<circle cx="12" cy="15.5" r="1.4" fill="currentColor"/>'),
    ("deck", "#f4efe6", "#b9b1a4", "#5e574c",
     '<g fill="none" stroke="#3a2f2a" stroke-width="2">'
     '<rect x="3" y="6.5" width="18" height="11" rx="2.6"/></g>'
     '<circle cx="8.6" cy="12" r="2.4" fill="#3a2f2a"/><circle cx="15.4" cy="12" r="2.4" fill="#3a2f2a"/>'
     '<path d="M3.5 9h17" stroke="#d6423a" stroke-width="1.6"/>'),
]


def orb_svg(top, bottom, shadow, glyph):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 68 68" width="68" height="68">
  <defs>
    <linearGradient id="bg" x1="0.13" y1="0" x2="0.63" y2="1">
      <stop offset="0" stop-color="{top}"></stop>
      <stop offset="1" stop-color="{bottom}"></stop>
    </linearGradient>
    <radialGradient id="gloss" cx="0.5" cy="-0.25" r="1.15">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.5"></stop>
      <stop offset="0.48" stop-color="#ffffff" stop-opacity="0.07"></stop>
      <stop offset="0.62" stop-color="#ffffff" stop-opacity="0"></stop>
    </radialGradient>
    <radialGradient id="base" cx="0.5" cy="1.1" r="0.9">
      <stop offset="0" stop-color="{shadow}" stop-opacity="0.55"></stop>
      <stop offset="0.6" stop-color="{shadow}" stop-opacity="0"></stop>
    </radialGradient>
  </defs>
  <circle cx="34" cy="34" r="34" fill="url(#bg)"></circle>
  <circle cx="34" cy="34" r="34" fill="url(#base)"></circle>
  <circle cx="34" cy="34" r="34" fill="url(#gloss)"></circle>
  <g transform="translate(17,17) scale(1.4167)" style="color:#fff">{glyph}</g>
</svg>
"""


def icon():
    render = os.path.join(OUT, ".icon-1024.png")
    subprocess.run([ICTOOL, os.path.join(APP, "Cassette/Resources/AppIcon.icon"), "--export-image",
                    "--output-file", render, "--platform", "iOS", "--rendition", "Default",
                    "--width", "1024", "--height", "1024", "--scale", "1"], check=True, capture_output=True)
    big = Image.open(render).convert("RGBA")
    os.remove(render)
    big.resize((320, 320), Image.LANCZOS).save(os.path.join(OUT, "cassette-icon.png"), optimize=True)
    big.save(os.path.join(OUT, "media", "cassette-app-icon-1024.png"), optimize=True)
    # Social card: the icon centred on Luten's card ground, the same 470px box.
    card = Image.new("RGB", (1200, 630), (31, 31, 38))
    mark = big.resize((470, 470), Image.LANCZOS)
    card.paste(mark, (365, 80), mark)
    card.save(os.path.join(OUT, "og-cassette.png"), optimize=True)


def qr():
    qr = segno.make(APP_STORE + "?ct=web_qr", error="m")
    qr.save(os.path.join(OUT, "cassette-qr.svg"), scale=10, dark="#15110a", light="#f6f3ec",
            svgclass="segno", lineclass="qrline", xmldecl=True)
    print("qr version", qr.version, "encodes", APP_STORE + "?ct=web_qr")


def screens():
    for name in ("deck", "notes", "transcript", "email", "shelf"):
        im = Image.open(os.path.join(APP, "AppStore/screenshots/captures", f"raw-{name}.png")).convert("RGB")
        im = im.resize((540, round(540 * im.height / im.width)), Image.LANCZOS)
        im.save(os.path.join(OUT, f"screen-{name}.webp"), "WEBP", quality=82, method=6)


def media():
    """Full-resolution files for /cassette/press. JPEG, not PNG: a 1320x2868 PNG is
    over a megabyte and press use does not need lossless."""
    names = ("record", "notes", "transcript", "email", "shelf")
    for i, name in enumerate(names, 1):
        card = Image.open(os.path.join(APP, "AppStore/screenshots/cards", f"{i}_{name}.png")).convert("RGB")
        card.save(os.path.join(OUT, "media", f"cassette-appstore-{i}-{name}.jpg"), "JPEG", quality=90, optimize=True, progressive=True)
        card.resize((360, round(360 * card.height / card.width)), Image.LANCZOS).save(
            os.path.join(OUT, "media", f"thumb-appstore-{i}-{name}.webp"), "WEBP", quality=80, method=6)
    for name, capture in zip(names, ("deck", "notes", "transcript", "email", "shelf")):
        raw = Image.open(os.path.join(APP, "AppStore/screenshots/captures", f"raw-{capture}.png")).convert("RGB")
        raw.save(os.path.join(OUT, "media", f"cassette-screen-{name}.jpg"), "JPEG", quality=92, optimize=True, progressive=True)


def waveform(points=180):
    pcm = subprocess.run(["ffmpeg", "-v", "quiet", "-i", os.path.join(APP, "AppStore/screenshots/samples/relaunch.m4a"),
                          "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    samples = array.array("h", pcm)
    step = len(samples) // points
    env = [max(abs(s) for s in samples[i * step:(i + 1) * step]) for i in range(points)]
    peak = max(env) or 1
    print("waveform", ",".join(str(round(100 * e / peak)) for e in env))


def main():
    os.makedirs(os.path.join(OUT, "media"), exist_ok=True)
    for slug, top, bottom, shadow, glyph in ORBS:
        with open(os.path.join(ICONS, f"cassette-{slug}.svg"), "w") as f:
            f.write(orb_svg(top, bottom, shadow, glyph))
    icon()
    qr()
    screens()
    media()
    waveform()


if __name__ == "__main__":
    main()
