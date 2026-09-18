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
    icons/cassette-*.svg           feature icons, drawn from the app's own parts
    (stdout)                       the waveform envelope, pasted into script.js

WHY THE ICONS LOOK LIKE THAT
They are the app's own materials, not generic glyphs: the plastic key face, the
ruled paper with its red margin, the cassette from the app icon, the LCD and the
SHARE glyph. The card accents in cassette/index.html follow the app's palette.

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

# The feature icons are drawn from the app's own parts, so the page looks like the thing it sells:
# a plastic key face (Palette.panel* and keyEdge), the notes paper with its red margin rule, the app
# icon's cassette, the deck's LCD, and the SHARE glyph the tape screen uses.
KEY = """  <defs>
    <linearGradient id="face" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F4F2EE"/><stop offset="0.52" stop-color="#E4E2DD"/><stop offset="1" stop-color="#CCCAC5"/>
    </linearGradient>
    <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBF7EE"/><stop offset="1" stop-color="#F3EEE1"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1B201F"/><stop offset="1" stop-color="#0A0D0C"/>
    </linearGradient>
    <radialGradient id="led" cx="0.38" cy="0.32" r="0.8">
      <stop offset="0" stop-color="#E8615A"/><stop offset="0.55" stop-color="#C33A34"/><stop offset="1" stop-color="#9C1D1B"/>
    </radialGradient>
  </defs>
  <g>
    <rect x="3" y="4" width="62" height="61" rx="16" fill="#9E9B96" opacity="0.5"/>
    <rect x="3" y="3" width="62" height="61" rx="16" fill="url(#face)"/>
    <path d="M7 19a12 12 0 0 1 12-12h30a12 12 0 0 1 12 12" fill="none" stroke="#FCFBF9" stroke-width="1.6" stroke-linecap="round" opacity="0.9"/>
    <rect x="3.75" y="3.75" width="60.5" height="59.5" rx="15.25" fill="none" stroke="#B3B0AB" stroke-width="1.5"/>
  </g>
"""


def key_svg(glyph):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 68 68" width="68" height="68">\n'
            + KEY + glyph + "</svg>\n")


def paper_page(x=13, y=13, w=42, h=41, margin=9):
    """A ruled page with the red margin rule, like the tape's notes paper."""
    return (f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="url(#paper)" stroke="#B9B5AC" stroke-width="1.2"/>\n'
            f'    <line x1="{x + margin}" y1="{y + 1.5}" x2="{x + margin}" y2="{y + h - 1.5}" stroke="#C44848" stroke-width="1.2" opacity="0.65"/>\n')


def rule(x, y, w, opacity=0.5, color="#2B2A28", height=1.8):
    return f'    <rect x="{x}" y="{y}" width="{w}" height="{height}" rx="{height / 2}" fill="{color}" opacity="{opacity}"/>\n'


def cassette_shell(x, y, w=40, h=17, label="#C0332E"):
    """The app icon's cassette: cream shell, red stripe, dark window, two reels."""
    cy = y + h * 0.62
    reel = h * 0.19
    return (f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h * 0.18}" fill="#EDE8DC" stroke="#A8A49B" stroke-width="1.1"/>\n'
            f'    <rect x="{x + 1.2}" y="{y + h * 0.2}" width="{w - 2.4}" height="{h * 0.11}" fill="{label}"/>\n'
            f'    <rect x="{x + w * 0.22}" y="{cy - h * 0.23}" width="{w * 0.56}" height="{h * 0.46}" rx="{h * 0.12}" fill="#211E1C"/>\n'
            + "".join(f'    <circle cx="{x + w * f}" cy="{cy}" r="{reel}" fill="#FBF7EE"/>\n'
                      f'    <circle cx="{x + w * f}" cy="{cy}" r="{reel * 0.42}" fill="#3B3733"/>\n' for f in (0.34, 0.66)))


def icon_glyphs():
    """slug to glyph markup, in the order the page uses them."""
    return [
        # the deck's red REC light
        ("record",
         '    <circle cx="34" cy="33.5" r="13.5" fill="#B7B3AC" opacity="0.35"/>\n'
         '    <circle cx="34" cy="33.5" r="12.5" fill="url(#led)"/>\n'
         '    <circle cx="30.4" cy="29.6" r="3.4" fill="#FFFFFF" opacity="0.42"/>\n'
         '    <circle cx="34" cy="33.5" r="12.5" fill="none" stroke="#7E1513" stroke-width="1.1" opacity="0.55"/>\n'),
        # the transcript page: a timestamp against every line
        ("transcript",
         paper_page(margin=11)
         + "".join(rule(11.5, y, 6.5, 0.45, "#6E6A63", 1.6) + rule(26.5, y, w, 0.5)
                   for y, w in ((19.5, 24), (27.5, 21), (35.5, 25), (43.5, 15)))),
        # the notes page: a highlighted line, then actions with their checkboxes
        ("notes",
         paper_page()
         + rule(24, 19, 24, 0.5)
         + '    <rect x="23" y="26" width="26" height="6.5" rx="2" fill="#FFD264" opacity="0.85"/>\n'
         + rule(24, 28.4, 24, 0.55)
         + '    <rect x="23.5" y="37" width="6" height="6" rx="1.4" fill="none" stroke="#2B2A28" stroke-width="1.4" opacity="0.7"/>\n'
         + rule(32.5, 39, 16, 0.5)
         + '    <rect x="23.5" y="46" width="6" height="6" rx="1.4" fill="none" stroke="#2B2A28" stroke-width="1.4" opacity="0.7"/>\n'
         + rule(32.5, 48, 12, 0.5)),
        # the follow-up letter
        ("email",
         '    <rect x="11" y="19" width="46" height="31" rx="3.5" fill="url(#paper)" stroke="#B9B5AC" stroke-width="1.2"/>\n'
         '    <rect x="12.2" y="45.5" width="43.6" height="3.3" rx="1.6" fill="#C44848" opacity="0.6"/>\n'
         '    <path d="M12.5 21.5 34 37 55.5 21.5" fill="none" stroke="#2B2A28" stroke-width="2" stroke-linejoin="round" opacity="0.8"/>\n'
         '    <path d="M12.5 47.8 27 33.5M55.5 47.8 41 33.5" fill="none" stroke="#2B2A28" stroke-width="1.4" opacity="0.35"/>\n'),
        # tapes on the shelf
        ("shelf",
         cassette_shell(14, 14) + cassette_shell(14, 35.5)
         + '    <rect x="12" y="55.5" width="44" height="2.6" rx="1.3" fill="#2B2A28" opacity="0.28"/>\n'),
        # the app's own SHARE glyph: a tray with an arrow leaving it
        ("export",
         '    <path d="M20 36v12a2.5 2.5 0 0 0 2.5 2.5h23A2.5 2.5 0 0 0 48 48V36" fill="none" stroke="#2B2A28" stroke-width="3" stroke-linecap="round" opacity="0.85"/>\n'
         '    <path d="M34 42V17" fill="none" stroke="#2B2A28" stroke-width="3" stroke-linecap="round" opacity="0.85"/>\n'
         '    <path d="M25.5 25.5 34 17l8.5 8.5" fill="none" stroke="#2B2A28" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>\n'),
        # the deck's LCD, lit
        ("private",
         '    <rect x="10" y="20" width="48" height="27" rx="5" fill="url(#glass)" stroke="#2A2E2C" stroke-width="1.2"/>\n'
         '    <rect x="14.5" y="24.5" width="17" height="5" rx="1" fill="#5CF2C8" opacity="0.95"/>\n'
         '    <rect x="34" y="24.5" width="9" height="5" rx="1" fill="#5CF2C8" opacity="0.5"/>\n'
         + "".join(f'    <rect x="{14.5 + i * 4.2}" y="{38.5 - h}" width="2.6" height="{h + 3}" rx="0.9" fill="#5CF2C8" opacity="{0.9 if i < 7 else 0.35}"/>\n'
                   for i, h in enumerate((2, 4, 6, 5, 7, 4, 6, 2, 1)))
         + '    <rect x="14.5" y="41.5" width="39" height="1.6" rx="0.8" fill="#5CF2C8" opacity="0.25"/>\n'),
        # the piano key row
        ("deck",
         '    <rect x="9" y="19" width="50" height="31" rx="5" fill="#A9A6A1" opacity="0.75"/>\n'
         + "".join(f'    <rect x="{x}" y="22" width="9.5" height="25" rx="2.4" fill="#F2F0EC" stroke="#AEABA6" stroke-width="1"/>\n'
                   + "".join(f'    <rect x="{x + 1.8}" y="{36 + j * 2.6}" width="5.9" height="1.3" rx="0.65" fill="#8E8B86"/>\n' for j in range(3))
                   for x in (12, 23, 34, 45))),
    ]


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
    for slug, glyph in icon_glyphs():
        with open(os.path.join(ICONS, f"cassette-{slug}.svg"), "w") as f:
            f.write(key_svg(glyph))
    icon()
    qr()
    screens()
    media()
    waveform()


if __name__ == "__main__":
    main()
