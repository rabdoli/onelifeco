#!/usr/bin/env python3
"""Builds the Luten guides: /luten/guides/ and /luten/guides/<slug>/.

One guide is one JSON file in tools/luten_guides/. Edit that file, never the output. Run from the repo root:

    python3 tools/make_luten_guides.py            check every guide, then write the pages
    python3 tools/make_luten_guides.py --check    check only, write nothing
    python3 tools/make_luten_guides.py --preview  write the pages only, leaving sitemap.xml, llms.txt and /luten alone
    python3 seo-build.py                          afterwards, so /luten lists the new guide

It also writes the guide lines in sitemap.xml and llms.txt, the screens in luten/guides/img/, and
tools/luten_guides/_links.html, which seo-build.py puts on /luten. It owns only the /luten/guides/ lines in those files;
tools/make_cassette_guides.py owns the /cassette/guides/ ones.

Hand-written pages like /luten/white-noise (NOT built by seo-build.py), so they carry their own copy of the PostHog block
and the two store-click listeners, taken from luten/white-noise/index.html at build time, plus guide_section (how far
people read) and guide_cta (which button they used). Nothing here stores anything on the visitor's device.

A guide that fails a check stops the whole build, so nothing half right goes live. Luten's rules are stricter than
Cassette's and they are checked on the finished page, not only the JSON, because a clean page can hide a dirty generator:
never the free tier or the catalogue size, no health claims including soft ones, never a prescribed listening duration or
an outcome attached to one. Prices never appear: they change, and the store shows the current one. If a check fails, fix
the guide, never the check.
"""
import glob, html, json, os, re, subprocess, sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.onelifeco.app"
GUIDES = os.path.join(ROOT, "tools", "luten_guides")
OUT = os.path.join(ROOT, "luten", "guides")
SCREENS = os.path.expanduser("~/luten-app/Marketing/seo/screens")
# Pages that already answer a search. A guide that repeats one of them should improve it instead.
HAND_WRITTEN = ["white-noise", "rain-sounds", "fan-sounds", "3am", "no-talking"]

APP_STORE = "https://apps.apple.com/us/app/luten-sleep-focus-sounds/id6777673392?ct=web_guide"
PLAY = "https://play.google.com/store/apps/details?id=app.luten.android&amp;utm_source=onelifeco&amp;utm_campaign=web_guide"


def posthog():
    s = open(os.path.join(ROOT, "luten", "white-noise", "index.html"), encoding="utf-8").read()
    a = s.index("<!-- Analytics: PostHog")
    b = s.index("</head>", a)
    return s[a:b].rstrip()


TRACK = """<script>
// How far people read, so the buttons can sit where readers stop. Each heading reports once per page load.
document.addEventListener('DOMContentLoaded', function () {
  if (!window.posthog || !('IntersectionObserver' in window)) return;
  var seen = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      seen.unobserve(e.target);
      posthog.capture('guide_section', { route: location.pathname, n: +e.target.dataset.n, section: e.target.textContent.slice(0, 60) });
    });
  });
  document.querySelectorAll('[data-n]').forEach(function (h) { seen.observe(h); });
});
// Which button: the top, the middle or the end of the guide.
document.addEventListener('click', function (e) {
  var a = e.target && e.target.closest && e.target.closest('a[data-place]');
  if (!a || !window.posthog) return;
  posthog.capture('guide_cta', { route: location.pathname, place: a.dataset.place, store: a.dataset.store });
}, true);
</script>"""

CSS = """
  :root { color-scheme: dark; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0b1326; color: rgba(255,255,255,0.85);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.65; overflow-x: hidden; }
  .glow { position: fixed; top: -20%; left: 50%; transform: translateX(-50%); width: 700px; height: 700px; border-radius: 50%;
    background: radial-gradient(circle, rgba(251,191,36,0.10), rgba(139,92,246,0.10) 40%, transparent 70%); pointer-events: none; z-index: 0; }
  .wrap { position: relative; z-index: 1; max-width: 720px; margin: 0 auto; padding: 0 24px; }
  header { padding: 32px 0 8px; }
  .brand { font-weight: 200; letter-spacing: 9px; font-size: 22px; color: #fff; padding-left: 9px; }
  .brand a { color: inherit; text-decoration: none; }
  .hero { padding: 44px 0 10px; }
  .eyebrow { font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.4); margin-bottom: 14px; }
  .eyebrow a { color: inherit; text-decoration: none; }
  h1 { font-size: clamp(32px, 6vw, 46px); color: #fff; letter-spacing: -1px; line-height: 1.1; margin-bottom: 12px; text-wrap: balance; }
  .by { font-size: 14px; color: rgba(255,255,255,0.45); }
  h2 { color: #fff; font-size: 23px; line-height: 1.25; margin: 42px 0 12px; letter-spacing: -0.3px; text-wrap: balance; }
  h3 { color: #fff; font-size: 16px; margin: 20px 0 4px; }
  p { margin-bottom: 14px; color: rgba(255,255,255,0.74); }
  strong { color: #fff; font-weight: 600; }
  a { color: #c0c1ff; }
  ul, ol { margin: 0 0 16px 22px; color: rgba(255,255,255,0.78); }
  li { margin-bottom: 8px; padding-left: 2px; }
  .answer { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 22px 24px; margin: 24px 0 8px; }
  .answer h2 { margin: 0 0 8px; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.45); font-weight: 600; }
  .answer p { color: rgba(255,255,255,0.88); margin-bottom: 10px; }
  .cta { display: inline-block; background: rgba(128,131,255,0.16); border: 1px solid rgba(128,131,255,0.35); color: #dcdcff;
    text-decoration: none; border-radius: 999px; padding: 12px 22px; font-size: 15px; margin: 6px 10px 6px 0; }
  .cta:hover { background: rgba(128,131,255,0.26); }
  .ctas { margin: 8px 0 14px; }
  .shots { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; max-width: 520px; margin: 18px 0 22px; }
  .shots.one { grid-template-columns: minmax(0, 250px); }
  figure img { display: block; width: 100%; height: auto; border-radius: 20px; border: 1px solid rgba(255,255,255,0.14); }
  figcaption { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 8px; text-align: center; }
  .list { list-style: none; margin: 0 0 16px; }
  .list li { padding: 14px 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 0; }
  .list a { color: #fff; text-decoration: none; font-weight: 600; display: block; }
  .list a:hover { color: #c0c1ff; }
  .list span { font-size: 15px; color: rgba(255,255,255,0.6); }
  .note { font-size: 13px; color: rgba(255,255,255,0.45); }
  .sources li { font-size: 13px; color: rgba(255,255,255,0.45); word-break: break-word; }
  footer { padding: 44px 0 70px; color: rgba(255,255,255,0.35); font-size: 13px; border-top: 1px solid rgba(255,255,255,0.07); margin-top: 50px; }
  footer a { color: rgba(255,255,255,0.55); }
  @media (max-width: 480px) { .cta { display: block; text-align: center; margin: 8px 0; } }
"""

# Claims that must never appear in a guide, by concept rather than by exact string. Checked case-insensitively on the
# finished page's text. Written as phrases, so "sleep", "deep" or "breathing" on their own stay usable: the claim is in the verb.
BANNED = [
    (r"[–—]", "em or en dash"),
    (r"\$\s?\d|\b\d+(\.\d+)?\s?(dollars|usd)\b", "a price (they change; link to the store)"),
    # The free tier and the catalogue. Free to download, an optional subscription and the trial are fine; the mechanics are not.
    (r"\b\d[\d,]*\+?\s+(free\s+|premium\s+|original\s+|different\s+)?(sounds?|tracks?|soundscapes?|mixes)\b", "the catalogue size or free tier as a number"),
    (r"\b(hundreds|thousands|dozens|tons|lots)\s+of\s+(sounds?|tracks?|soundscapes?)\b", "the catalogue size in words"),
    (r"\bfree\s+(sounds?|tracks?|tier|plan|version|forever)\b|\bsounds?\s+(are|is)\s+free\b|\bfor free\b", "the free tier"),
    (r"\bunlock(s|ed|ing)?\b|\bcatalog(ue)?\b|\bpaywall\b|\bpremium\s+(sounds?|tracks?|only)\b", "the free tier or catalogue"),
    # Health claims, including soft ones.
    (r"\b(helps?|helping|lets?|makes?|gets?|puts?|sends?)\s+(you\s+|your\s+\w+\s+|people\s+)?(to\s+)?(fall\s+asleep|sleep|focus|relax|calm|concentrate|unwind|drift|study)\b", "a sound or feature credited with an outcome"),
    (r"\b(better|deeper|faster|longer|improved|quality|restful|restorative)\s+(sleep|focus|rest|concentration)\b|\bsleep\s+(better|faster|longer|deeper)\b|\bfall\s+asleep\s+(faster|quicker|sooner)\b", "a promised outcome"),
    (r"\b(reduc|lower|boost|rais|improv|relie|eas|sooth|quiet|calm)(e|es|ed|ing|ve|ves|ved|ving|s)?\s+(your\s+|the\s+)?(stress|anxiety|cortisol|dopamine|blood pressure|heart rate|mood|tinnitus|symptoms?|mind|nerves|racing)\b", "a claimed physiological change"),
    (r"\b(stress|anxiety|pain|tinnitus)\s+relief\b", "a claimed relief"),
    (r"\b(cures?|heals?|treats?|treatment|therapy|therapeutic|remedy|diagnos\w+|symptoms?|disorder|insomnia|medication)\b", "a medical word"),
    (r"\b(clinically|scientifically|medically)\b|\bproven\b|\b(science|studies|research|evidence)\s+(says?|shows?|suggests?|proves?|finds?|found|backed)\b|\bbacked by\b|\bresearch-backed\b|\bstudies\b", "an appeal to proof"),
    (r"\bwhat works\b|\bworks best\b|\bactually works\b|\bbest for (sleep|focus|adhd|anxiety|stress)\b|\bbenefits?\b|\beffective\b", "an implied result"),
    (r"\b(your|the)\s+(brain|nervous system|body clock|circadian)\b|\bmelatonin\b|\bcortisol\b|\bdopamine\b|\bdeep sleep\b|\brem sleep\b|\bsleep cycle", "a mechanism stated as fact"),
    # A prescribed listening duration, or an outcome attached to one. Seconds are fine (a fade, a breath); minutes and hours are not.
    (r"\b\d+(\.\d+)?\s*(-|to)?\s*\d*\s*(min|mins|minutes?|hrs?|hours?|nights?|weeks?)\b", "a duration, which reads as a prescription"),
    (r"\b(a|an|one|two|three|four|five|six|seven|eight|ten|fifteen|twenty|thirty|forty|forty-five|sixty|half an?|half)\s+(min|minute|minutes|hr|hour|hours|night|nights|week|weeks)\b", "a duration in words"),
    (r"\b(every|each)\s+night\b|\ball night\b|\bnightly\b", "a prescribed routine"),
    # Product claims and filler.
    (r"\b(best|#1|number one|most accurate|100%|only app|unlike any)\b.{0,30}\b(app|apps|sound|sounds|timer)\b", "a superlative about the product"),
    (r"\bguarantee[sd]?\b|\bnever wake\b|\bwon't wake\b", "a promise the app can't keep"),
    (r"\bno vocals\b|\bevery sound is instrumental\b|\buniform loudness\b|\bevery track\b.{0,30}\bloudness\b", "untrue of every track: say no narration and no lyrics, and nearly every track"),
    (r"\boffline\b|\bairplane mode\b", "offline needs a subscription, which can't be said without the free tier"),
    (r"\bdelve\b|\bin today's fast-paced\b|\bgame.?changer\b|\bseamless(ly)?\b|\brevolutionary\b", "filler"),
    (r"\bcassette\b", "the other product"),
]


def fail(msg):
    sys.exit("GUIDE CHECK FAILED: " + msg)


def inline(text):
    """Escapes the text, then turns **bold** and [label](https://...) into markup."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    def link(m):
        external = m.group(2).startswith("http")
        rel = ' target="_blank" rel="noopener"' if external else ""
        return f'<a href="{html.escape(m.group(2))}"{rel}>{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", link, t)


def plain(text):
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)


def page_text(markup):
    """The words a visitor reads, and the words a search engine indexes: title, description and body, no code."""
    head_bits = re.findall(r'<title>(.*?)</title>|<meta name="description" content="(.*?)"', markup, re.S)
    t = " ".join(a or b for a, b in head_bits)
    body = markup[markup.index("<body>"):]
    body = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", body)
    body = re.sub(r"<header>[\s\S]*?</header>", " ", body)  # the styled wordmark, the one place lowercase is right
    body = re.sub(r'<ul class="sources">[\s\S]*?</ul>', " ", body)  # others' page titles and addresses, not our words
    alts = " ".join(re.findall(r'alt="(.*?)"', body))
    return html.unescape(t + " " + re.sub(r"<[^>]+>", " ", body) + " " + alts)


def check_words(slug, markup):
    text = page_text(markup)
    for pat, why in BANNED:
        m = re.search(pat, text, re.I)
        if m:
            a = max(0, m.start() - 50)
            fail(f"{slug}: {why}: '...{text[a:m.end() + 30].strip()}...'")
    # Brand casing: "Luten" in running text, never lowercase or all caps. A web address like onelifeco.app/luten is fine.
    m = re.search(r"\bLUTEN\b|(?<![/\w.])luten\b", text)
    if m:
        fail(f"{slug}: write Luten in title case: '{text[max(0, m.start() - 40):m.end() + 20].strip()}'")


def screens():
    return json.load(open(os.path.join(GUIDES, "screens.json"), encoding="utf-8"))


def shot(name, write):
    """The real app screen as a web image. Returns its width and height. Never draw or mock up a screen."""
    info = screens().get(name)
    if not info:
        fail(f"screen '{name}' is not in tools/luten_guides/screens.json")
    dst = os.path.join(OUT, "img", name + ".webp")
    if write and not os.path.exists(dst):
        src = os.path.join(SCREENS, info["file"])
        if not os.path.exists(src):
            fail(f"screen file missing: {src}")
        im = Image.open(src).convert("RGB")
        w = 620
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im.save(dst, "WEBP", quality=82, method=6)
    if os.path.exists(dst):
        return Image.open(dst).size
    return (620, 1347)


def cta(place):
    return (f'<div class="ctas"><a class="cta" data-place="{place}" data-store="ios" href="{APP_STORE}" target="_blank" rel="noopener">Download on the App Store</a>'
            f'<a class="cta" data-place="{place}" data-store="android" href="{PLAY}" target="_blank" rel="noopener">Get it on Google Play</a></div>')


def shots_html(names, alts, write):
    figs = []
    for name, alt in zip(names, alts):
        w, h = shot(name, write)
        figs.append(f'<figure><img src="/luten/guides/img/{name}.webp" width="{w}" height="{h}" loading="lazy" alt="{html.escape(alt)}" />'
                    f'<figcaption>{screens()[name]["os"]}</figcaption></figure>')
    return f'<div class="shots{" one" if len(figs) == 1 else ""}">{"".join(figs)}</div>'


def blocks_html(blocks, write):
    out = []
    for b in blocks:
        if "p" in b:
            out.append(f'<p>{inline(b["p"])}</p>')
        elif "h3" in b:
            out.append(f'<h3>{inline(b["h3"])}</h3>')
        elif "ul" in b:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in b["ul"]) + "</ul>")
        elif "ol" in b:
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in b["ol"]) + "</ol>")
        elif "shots" in b:
            out.append(shots_html(b["shots"], b["alts"], write))
        elif "cta" in b:
            out.append(cta(b["cta"]))
        else:
            fail(f"unknown block {b}")
    return "\n  ".join(out)


def words(g):
    bits = [g["title"], g["answer"]]
    for s in g["sections"]:
        bits.append(s["h"])
        for b in s["blocks"]:
            for k in ("p", "h3"):
                if k in b:
                    bits.append(b[k])
            for k in ("ul", "ol"):
                bits.extend(b.get(k, []))
    bits.extend(q["q"] + " " + q["a"] for q in g.get("faq", []))
    return plain(" ".join(bits))


def grams(text):
    t = text.lower().split()
    return set(zip(*[t[i:] for i in range(4)]))


def existing_pages():
    """The hand-written Luten pages, as text, so a guide can't quietly compete with one."""
    out = {}
    for name in HAND_WRITTEN:
        s = open(os.path.join(ROOT, "luten", name, "index.html"), encoding="utf-8").read()
        s = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", s[s.index("<body"):])
        out[name] = re.sub(r"<[^>]+>", " ", s)
    return out


def check(g, everyone, pages):
    slug = g.get("slug", "?")
    for k in ("slug", "title", "description", "h1", "keyword", "answer", "published", "updated", "sections"):
        if not g.get(k):
            fail(f"{slug}: missing {k}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        fail(f"{slug}: bad slug")
    if not 30 <= len(plain(g["title"])) <= 62:
        fail(f"{slug}: title is {len(plain(g['title']))} characters, want 30 to 62")
    if not 90 <= len(plain(g["description"])) <= 160:
        fail(f"{slug}: description is {len(plain(g['description']))} characters, want 90 to 160")
    text = words(g) + " " + plain(g["description"]) + " " + plain(g["h1"])
    n = len(text.split())
    if n < 350:
        fail(f"{slug}: {n} words, too thin to help anyone")
    if n > 1800:
        fail(f"{slug}: {n} words, cut it down: a guide is an answer, not an essay")
    places = [b["cta"] for s in g["sections"] for b in s["blocks"] if "cta" in b]
    if not places:
        fail(f"{slug}: needs a button in the body, where readers stop")
    if len(places) != len(set(places)):
        fail(f"{slug}: two buttons share the place name {places}")
    systems = set()
    for s in g["sections"]:
        for b in s["blocks"]:
            if "shots" in b:
                if len(b["shots"]) != len(b.get("alts", [])):
                    fail(f"{slug}: every screen needs its alt text")
                systems.update(screens().get(x, {}).get("os") for x in b["shots"])
    if not g.get("single_os") and not {"iPhone", "Android"} <= systems:
        fail(f"{slug}: show both iPhone and Android, or set single_os with the reason")
    if not re.search(r"\biphone\b", text, re.I) or not re.search(r"\bandroid\b", text, re.I):
        if not g.get("single_os"):
            fail(f"{slug}: name both iPhone and Android")
    mine = grams(text)
    for other in everyone:
        if other["slug"] == slug:
            continue
        theirs = grams(words(other))
        overlap = len(mine & theirs) / max(1, min(len(mine), len(theirs)))
        if overlap > 0.25:
            fail(f"{slug}: {overlap:.0%} the same as {other['slug']}: improve that guide instead of adding a near copy")
    for name, body in pages.items():
        theirs = grams(body)
        overlap = len(mine & theirs) / max(1, min(len(mine), len(theirs)))
        if overlap > 0.25:
            fail(f"{slug}: {overlap:.0%} the same as /luten/{name}/: improve that page instead")
    for r in g.get("related", []):
        if r not in {x["slug"] for x in everyone}:
            fail(f"{slug}: related guide '{r}' does not exist")


def head(title, desc, url, ld, og_type="article"):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{t}</title>
<meta name="description" content="{d}" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="{url}" />
<meta name="apple-itunes-app" content="app-id=6777673392" />
<meta property="og:title" content="{t}" />
<meta property="og:description" content="{d}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="Luten" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{BASE}/luten/og-luten.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{t}" />
<meta name="twitter:description" content="{d}" />
<meta name="twitter:image" content="{BASE}/luten/og-luten.png" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<!-- Built by tools/make_luten_guides.py from tools/luten_guides/. Edit the JSON, not this file. -->
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
<style>{CSS}</style>
{posthog()}
{TRACK}
</head>
<body>
<div class="glow"></div>
<div class="wrap">

  <header><div class="brand"><a href="/luten/">luten</a></div></header>
"""


FOOT = """
  <footer>
    Luten is A One Life Product. It is a wellness app, not a medical device, and nothing here is advice about treating a
    sleep or attention problem. <a href="https://www.onelifeco.app/luten/">onelifeco.app/luten</a> &middot;
    <a href="https://www.onelifeco.app/luten/guides/">Guides</a> &middot;
    <a href="https://www.onelifeco.app/privacypolicy">Privacy</a> &middot;
    <a href="https://www.onelifeco.app/termsofservice">Terms</a>
  </footer>

</div>
</body>
</html>
"""


def nice_date(d):
    y, m, day = d.split("-")
    names = "January February March April May June July August September October November December".split()
    return f"{int(day)} {names[int(m) - 1]} {y}"


def related(g, everyone):
    """The guides this one names, then the guides that name it, so a new link works in both directions."""
    picks = list(g.get("related", []))
    picks += [o["slug"] for o in everyone if g["slug"] in o.get("related", []) and o["slug"] not in picks]
    by = {o["slug"]: o for o in everyone}
    return [by[s] for s in picks if s != g["slug"]][:5]


def page(g, everyone, write):
    url = f"{BASE}/luten/guides/{g['slug']}/"
    title, desc = plain(g["title"]), plain(g["description"])
    body, n = [], 0
    for s in g["sections"]:
        n += 1
        body.append(f'<h2 data-n="{n}">{inline(s["h"])}</h2>\n  {blocks_html(s["blocks"], write)}')
    n += 1
    body.append(f'<h2 data-n="{n}">Try Luten</h2>\n  <p>Sleep and focus sounds, on iPhone and Android. Free to download, with an optional subscription that starts with a 7 day free trial.</p>\n  {cta("end")}')
    faq = g.get("faq", [])
    if faq:
        n += 1
        qa = "\n  ".join(f"<h3>{inline(q['q'])}</h3>\n  <p>{inline(q['a'])}</p>" for q in faq)
        body.append(f'<h2 data-n="{n}">Questions</h2>\n  {qa}')
    rel = related(g, everyone)
    if rel:
        items = "".join(f'<li><a href="/luten/guides/{o["slug"]}/">{inline(o["h1"])}</a><span>{inline(o["description"])}</span></li>' for o in rel)
        body.append(f'<h2>Related guides</h2>\n  <ul class="list">{items}</ul>')
    src = g.get("sources", [])
    if src:
        items = "".join(f'<li>{html.escape(x["name"])}: <a href="{html.escape(x["url"])}" rel="nofollow noopener" target="_blank">{html.escape(x["url"])}</a></li>' for x in src)
        body.append(f'<h2>Sources</h2>\n  <ul class="sources">{items}</ul>')
    graph = [
        {"@type": "Article", "@id": url + "#article", "headline": plain(g["h1"]), "description": desc, "url": url,
         "mainEntityOfPage": url, "datePublished": g["published"], "dateModified": g["updated"], "inLanguage": "en",
         "image": f"{BASE}/luten/og-luten.png", "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Luten", "item": f"{BASE}/luten/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{BASE}/luten/guides/"},
            {"@type": "ListItem", "position": 3, "name": plain(g["h1"]), "item": url}]},
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q["q"]), "acceptedAnswer": {"@type": "Answer", "text": plain(q["a"])}} for q in faq]})
    ld = {"@context": "https://schema.org", "@graph": graph}
    joined = "\n\n  ".join(body)
    return head(title, desc, url, ld) + f"""
  <div class="hero">
    <div class="eyebrow"><a href="/luten/guides/">Guides</a></div>
    <h1>{inline(g["h1"])}</h1>
    <p class="by">Written by the team that builds Luten, so we are not neutral about it. Updated {nice_date(g["updated"])}.</p>
  </div>

  <div class="answer">
    <h2>The short answer</h2>
    <p>{inline(g["answer"])}</p>
    {cta("top")}
  </div>

  {joined}
""" + FOOT


def hub(everyone):
    url = f"{BASE}/luten/guides/"
    title = "Luten Guides: Sleep Timers, Sound Settings and More"
    desc = "Practical step by step guides to sound on iPhone and Android: timers, settings and getting a phone to play what you want, the way you want it."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en", "publisher": {"@id": f"{BASE}/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Luten", "item": f"{BASE}/luten/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": url}]}]}
    items = "".join(f'<li><a href="/luten/guides/{g["slug"]}/">{inline(g["h1"])}</a><span>{inline(g["description"])}</span></li>' for g in everyone)
    return head(title, desc, url, ld, "website") + f"""
  <div class="hero">
    <div class="eyebrow"><a href="/luten/">Luten</a></div>
    <h1>Guides</h1>
    <p class="by">Practical guides to sound on iPhone and Android.</p>
  </div>

  <ul class="list">{items}</ul>

  <h2>Try Luten</h2>
  <p>Sleep and focus sounds, on iPhone and Android.</p>
  {cta("hub")}
""" + FOOT


def write_sitemap(everyone):
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"  <url>\s*<loc>[^<]*/luten/guides/[^<]*</loc>.*?</url>\n", "", s, flags=re.S)
    def entry(path, last, pri):
        return f"  <url>\n    <loc>{BASE}{path}</loc>\n    <lastmod>{last}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pri}</priority>\n  </url>\n"
    newest = max(g["updated"] for g in everyone)
    new = entry("/luten/guides/", newest, "0.7") + "".join(entry(f"/luten/guides/{g['slug']}/", g["updated"], "0.6") for g in everyone)
    anchor = re.search(r"  <url>\s*<loc>[^<]*/luten/no-talking/</loc>.*?</url>\n", s, flags=re.S)
    if not anchor:
        fail("sitemap.xml has no no-talking entry to follow")
    s = s[:anchor.end()] + new + s[anchor.end():]
    open(p, "w", encoding="utf-8").write(s)


def write_llms(everyone):
    p = os.path.join(ROOT, "llms.txt")
    lines = [l for l in open(p, encoding="utf-8").read().split("\n") if "/luten/guides/" not in l]
    at = next((i for i, l in enumerate(lines) if "/luten/no-talking/" in l), None)
    if at is None:
        fail("llms.txt has no no-talking line to follow")
    new = [f"- [Luten guides]({BASE}/luten/guides/): practical step by step guides to sound on iPhone and Android"]
    new += [f"- [{plain(g['h1'])}]({BASE}/luten/guides/{g['slug']}/)" for g in everyone]
    open(p, "w", encoding="utf-8").write("\n".join(lines[:at + 1] + new + lines[at + 1:]))


def write_links(everyone):
    """The line on /luten, the site's strongest Luten page: this is what gets a new guide found."""
    links = ", ".join(f'<a href="/luten/guides/{g["slug"]}/" style="color:#c0c1ff;">{inline(g["h1"])}</a>' for g in everyone[:8])
    block = f'<p class="get-note">Guides: {links}. <a href="/luten/guides/" style="color:#c0c1ff;">All guides</a>.</p>'
    open(os.path.join(GUIDES, "_links.html"), "w", encoding="utf-8").write(block + "\n")


def main():
    only_check, preview = "--check" in sys.argv, "--preview" in sys.argv
    everyone = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(GUIDES, "*.json")))
                if os.path.basename(p) != "screens.json"]
    if not everyone:
        fail("no guides in tools/luten_guides/")
    everyone.sort(key=lambda g: (g["published"], g["slug"]), reverse=True)
    pages = existing_pages()
    for g in everyone:
        check(g, everyone, pages)
    rendered = {g["slug"]: page(g, everyone, not only_check) for g in everyone}
    for slug, markup in rendered.items():
        check_words(slug, markup)
    the_hub = hub(everyone)
    check_words("hub", the_hub)
    print(f"checked {len(everyone)} guides")
    # The hand-written pages and /luten get the same kind of check, since readers go from a guide straight to them.
    pages_ok = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "check_luten_pages.py")])
    if pages_ok.returncode:
        fail("a Luten page breaks the copy rules: fix that sentence, never the check")
    if only_check:
        return
    for slug, markup in rendered.items():
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(markup)
        print("wrote /luten/guides/" + slug + "/")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(the_hub)
    if preview:
        print("preview only: sitemap.xml, llms.txt and /luten were left alone")
        return
    write_sitemap(everyone)
    write_llms(everyone)
    write_links(everyone)
    print("wrote the hub, sitemap.xml, llms.txt and tools/luten_guides/_links.html. Now run: python3 seo-build.py")


if __name__ == "__main__":
    main()
