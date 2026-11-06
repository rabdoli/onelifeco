#!/usr/bin/env python3
"""Builds the Cassette guides: /cassette/guides/ and /cassette/guides/<slug>/.

One guide is one JSON file in tools/guides/. Edit that file, never the output. Run from the repo root:

    python3 tools/make_cassette_guides.py          check every guide, then write the pages
    python3 tools/make_cassette_guides.py --check  check only, write nothing
    python3 seo-build.py                           afterwards, so /cassette lists the new guide

It also writes the guide lines in sitemap.xml and llms.txt, the screens in cassette/guides/img/, and
tools/guides/_links.html, which seo-build.py puts on /cassette.

Hand-written pages like /cassette/press (NOT built by seo-build.py), so they carry their own copy of the
PostHog block, taken from cassette/press.html at build time, plus guide_section (how far people read) and
guide_cta (which button they used). Nothing here stores anything on the visitor's device.

A guide that fails a check stops the whole build, so nothing half right goes live. The free tier comes from
cassette/config.json, because the app reads the same file: write {free_tapes} and {short_tape_minutes}, never the
numbers. Prices never appear here: they change, and the App Store shows the current one.
"""
import glob, html, json, os, re, sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.onelifeco.app"
GUIDES = os.path.join(ROOT, "tools", "guides")
OUT = os.path.join(ROOT, "cassette", "guides")
SCREENS = os.path.expanduser("~/Cassette/marketing/instagram/grid/assets")

APP_STORE = "https://apps.apple.com/app/apple-store/id6812001404?pt=129004817&amp;ct=web_guide&amp;mt=8"
PLAY = "https://play.google.com/store/apps/details?id=app.cassette.deck&amp;utm_source=onelifeco&amp;utm_campaign=web_guide"
CONFIG = json.load(open(os.path.join(ROOT, "cassette", "config.json"), encoding="utf-8"))
FREE = {"free_tapes": str(CONFIG["freeNotesPerMonth"]),
        "short_tape_minutes": str(CONFIG["freeShortTapeSeconds"] // 60)}


def posthog():
    s = open(os.path.join(ROOT, "cassette", "press.html"), encoding="utf-8").read()
    a = s.index("<!-- Analytics: PostHog")
    b = s.index("</script>", a) + len("</script>")
    return s[a:b]


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
  body { background: #140709; color: rgba(255,255,255,0.85);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.65; overflow-x: hidden; }
  .glow { position: fixed; top: -20%; left: 50%; transform: translateX(-50%); width: 700px; height: 700px; border-radius: 50%;
    background: radial-gradient(circle, rgba(246,241,231,0.08), rgba(232,64,60,0.12) 40%, transparent 70%); pointer-events: none; z-index: 0; }
  .wrap { position: relative; z-index: 1; max-width: 720px; margin: 0 auto; padding: 0 24px; }
  header { padding: 32px 0 8px; display: flex; align-items: center; gap: 12px; }
  header a { display: flex; align-items: center; gap: 12px; text-decoration: none; }
  header img { width: 34px; height: 34px; border-radius: 22%; }
  .brand { font-weight: 300; letter-spacing: 1px; font-size: 22px; color: #fff; }
  .brand b { font-weight: 700; }
  .hero { padding: 44px 0 10px; }
  .eyebrow { font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.4); margin-bottom: 14px; }
  .eyebrow a { color: inherit; text-decoration: none; }
  h1 { font-size: clamp(32px, 6vw, 46px); color: #fff; letter-spacing: -1px; line-height: 1.1; margin-bottom: 12px; text-wrap: balance; }
  .by { font-size: 14px; color: rgba(255,255,255,0.45); }
  h2 { color: #fff; font-size: 23px; line-height: 1.25; margin: 42px 0 12px; letter-spacing: -0.3px; text-wrap: balance; }
  h3 { color: #fff; font-size: 16px; margin: 20px 0 4px; }
  p { margin-bottom: 14px; color: rgba(255,255,255,0.74); }
  strong { color: #fff; font-weight: 600; }
  a { color: #ffb4a8; }
  ul, ol { margin: 0 0 16px 22px; color: rgba(255,255,255,0.78); }
  li { margin-bottom: 8px; padding-left: 2px; }
  .answer { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 18px; padding: 22px 24px; margin: 24px 0 8px; }
  .answer h2 { margin: 0 0 8px; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.45); font-weight: 600; }
  .answer p { color: rgba(255,255,255,0.88); margin-bottom: 10px; }
  .cta { display: inline-block; background: rgba(232,64,60,0.16); border: 1px solid rgba(232,64,60,0.45); color: #ffd9d2;
    text-decoration: none; border-radius: 999px; padding: 12px 22px; font-size: 15px; margin: 6px 10px 6px 0; }
  .cta:hover { background: rgba(232,64,60,0.26); }
  .ctas { margin: 8px 0 14px; }
  .ctanote { font-size: 13px; color: rgba(255,255,255,0.45); margin-bottom: 4px; }
  .shots { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; max-width: 520px; margin: 18px 0 22px; }
  .shots.one { grid-template-columns: minmax(0, 250px); }
  figure img { display: block; width: 100%; height: auto; border-radius: 20px; border: 1px solid rgba(255,255,255,0.14); }
  figcaption { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 8px; text-align: center; }
  .list { list-style: none; margin: 0 0 16px; }
  .list li { padding: 14px 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 0; }
  .list a { color: #fff; text-decoration: none; font-weight: 600; display: block; }
  .list a:hover { color: #ffb4a8; }
  .list span { font-size: 15px; color: rgba(255,255,255,0.6); }
  .note { font-size: 13px; color: rgba(255,255,255,0.45); }
  .sources li { font-size: 13px; color: rgba(255,255,255,0.45); word-break: break-word; }
  footer { padding: 44px 0 70px; color: rgba(255,255,255,0.35); font-size: 13px; border-top: 1px solid rgba(255,255,255,0.07); margin-top: 50px; }
  footer a { color: rgba(255,255,255,0.55); }
  @media (max-width: 480px) { .cta { display: block; text-align: center; margin: 8px 0; } }
"""

# Claims that must never appear in a guide, by concept rather than by exact string.
BANNED = [
    (r"[–—]", "em or en dash"),
    (r"\$\s?\d", "a price (they change; link to the store)"),
    (r"\b\d+\s+(free\s+)?tapes?\b", "the free tier as a number (use {free_tapes})"),
    (r"\bunder \d+ minutes\b", "the short tape limit as a number (use {short_tape_minutes})"),
    (r"\b(best|#1|number one|most accurate|100%)\b.{0,30}\b(app|note taker|recorder|transcription)\b", "a superlative about the product"),
    (r"\b(guarantee[sd]?|never miss)\b", "a promise the app can't keep"),
    (r"\bdelve\b|\bin today's fast-paced\b|\bgame.?changer\b|\bunlock(s|ing)? the\b|\bseamless(ly)?\b", "filler"),
]


def fail(msg):
    sys.exit("GUIDE CHECK FAILED: " + msg)


def fill(text):
    return text.format(**FREE) if "{" in text else text


def inline(text):
    """Escapes the text, then turns **bold** and [label](https://...) into markup."""
    t = html.escape(fill(text), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    def link(m):
        external = m.group(2).startswith("http")
        rel = ' target="_blank" rel="noopener"' if external else ""
        return f'<a href="{html.escape(m.group(2))}"{rel}>{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", link, t)


def plain(text):
    t = fill(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)


def screens():
    return json.load(open(os.path.join(GUIDES, "screens.json"), encoding="utf-8"))


def unmask(im):
    """Some simulator captures carry the camera cutout as a black pill in the status bar (simctl's display mask). It is
    hardware, not app UI; fill it from the status bar on either side, as a capture without the mask shows it."""
    im = im.convert("RGB")
    px = im.load()
    w, h = im.size
    cx = w // 2
    rows = [y for y in range(10, min(200, h)) if sum(px[cx, y]) <= 24]
    if not rows:
        return im
    a = b = cx
    for y in rows:
        x = cx
        while x > cx - 320 and sum(px[x - 1, y]) <= 90:
            x -= 1
        a = min(a, x)
        x = cx
        while x < cx + 320 and sum(px[x + 1, y]) <= 90:
            x += 1
        b = max(b, x)
    a, b = a - 5, b + 5
    for y in range(rows[0] - 4, rows[-1] + 5):
        left, right = px[a - 3, y], px[b + 3, y]
        for x in range(a, b + 1):
            t = (x - a) / (b - a)
            px[x, y] = tuple(round(left[i] * (1 - t) + right[i] * t) for i in range(3))
    return im


def shot(name, write):
    """The real app screen as a web image. Returns its width and height."""
    info = screens().get(name)
    if not info:
        fail(f"screen '{name}' is not in tools/guides/screens.json")
    dst = os.path.join(OUT, "img", name + ".webp")
    if write and not os.path.exists(dst):
        src = os.path.join(SCREENS, info["file"])
        if not os.path.exists(src):
            fail(f"screen file missing: {src}")
        im = Image.open(src)
        im = unmask(im) if info["os"] == "iPhone" else im.convert("RGB")
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
        figs.append(f'<figure><img src="/cassette/guides/img/{name}.webp" width="{w}" height="{h}" loading="lazy" alt="{html.escape(fill(alt))}" />'
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


def check(g, everyone):
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
    raw = json.dumps(g, ensure_ascii=False)  # as written, so {free_tapes} passes and a typed number does not
    for pat, why in BANNED:
        m = re.search(pat, raw, re.I)
        if m:
            fail(f"{slug}: {why}: '{m.group(0)}'")
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
    mine = set(zip(*[text.lower().split()[i:] for i in range(4)]))
    for other in everyone:
        if other["slug"] == slug:
            continue
        o = words(other).lower().split()
        theirs = set(zip(*[o[i:] for i in range(4)]))
        overlap = len(mine & theirs) / max(1, min(len(mine), len(theirs)))
        if overlap > 0.25:
            fail(f"{slug}: {overlap:.0%} the same as {other['slug']}: improve that guide instead of adding a near copy")
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
<meta name="apple-itunes-app" content="app-id=6812001404" />
<meta property="og:title" content="{t}" />
<meta property="og:description" content="{d}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="Cassette" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{BASE}/cassette/og-cassette.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{t}" />
<meta name="twitter:description" content="{d}" />
<meta name="twitter:image" content="{BASE}/cassette/og-cassette.png" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<!-- Built by tools/make_cassette_guides.py from tools/guides/. Edit the JSON, not this file. -->
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
<style>{CSS}</style>
{posthog()}
{TRACK}
</head>
<body>
<div class="glow"></div>
<div class="wrap">

  <header><a href="/cassette/"><img src="/cassette/cassette-icon.png" alt="" width="34" height="34" /><span class="brand">cassette <b>deck</b></span></a></header>
"""


FOOT = """
  <footer>
    Cassette is A One Life Product. <a href="https://www.onelifeco.app/cassette/">onelifeco.app/cassette</a> &middot;
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
    url = f"{BASE}/cassette/guides/{g['slug']}/"
    title, desc = plain(g["title"]), plain(g["description"])
    body, n = [], 0
    for s in g["sections"]:
        n += 1
        body.append(f'<h2 data-n="{n}">{inline(s["h"])}</h2>\n  {blocks_html(s["blocks"], write)}')
    n += 1
    body.append(f'<h2 data-n="{n}">Before you record</h2>\n  <p>Ask first. Whoever you are recording should know about it, some places require everyone\'s consent, and it is the decent thing to do.</p>')
    n += 1
    free = fill("Free to download. Recording is free and unlimited, tapes under {short_tape_minutes} minutes get their transcript and notes free, and longer ones get them free for {free_tapes} tapes a month.")
    body.append(f'<h2 data-n="{n}">Try Cassette</h2>\n  <p>{free}</p>\n  {cta("end")}')
    faq = g.get("faq", [])
    if faq:
        n += 1
        qa = "\n  ".join(f"<h3>{inline(q['q'])}</h3>\n  <p>{inline(q['a'])}</p>" for q in faq)
        body.append(f'<h2 data-n="{n}">Questions</h2>\n  {qa}')
    rel = related(g, everyone)
    if rel:
        items = "".join(f'<li><a href="/cassette/guides/{o["slug"]}/">{inline(o["h1"])}</a><span>{inline(o["description"])}</span></li>' for o in rel)
        body.append(f'<h2>Related guides</h2>\n  <ul class="list">{items}</ul>')
    src = g.get("sources", [])
    if src:
        items = "".join(f'<li>{html.escape(x["name"])}: <a href="{html.escape(x["url"])}" rel="nofollow noopener" target="_blank">{html.escape(x["url"])}</a></li>' for x in src)
        body.append(f'<h2>Sources</h2>\n  <ul class="sources">{items}</ul>')
    graph = [
        {"@type": "Article", "@id": url + "#article", "headline": plain(g["h1"]), "description": desc, "url": url,
         "mainEntityOfPage": url, "datePublished": g["published"], "dateModified": g["updated"], "inLanguage": "en",
         "image": f"{BASE}/cassette/og-cassette.png", "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"},
         "about": {"@id": f"{BASE}/cassette/#app"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Cassette", "item": f"{BASE}/cassette/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{BASE}/cassette/guides/"},
            {"@type": "ListItem", "position": 3, "name": plain(g["h1"]), "item": url}]},
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q["q"]), "acceptedAnswer": {"@type": "Answer", "text": plain(q["a"])}} for q in faq]})
    ld = {"@context": "https://schema.org", "@graph": graph}
    joined = "\n\n  ".join(body)
    return head(title, desc, url, ld) + f"""
  <div class="hero">
    <div class="eyebrow"><a href="/cassette/guides/">Guides</a></div>
    <h1>{inline(g["h1"])}</h1>
    <p class="by">Written by the team that builds Cassette, so we are not neutral about it. Updated {nice_date(g["updated"])}.</p>
  </div>

  <div class="answer">
    <h2>The short answer</h2>
    <p>{inline(g["answer"])}</p>
    {cta("top")}
  </div>

  {joined}
""" + FOOT


def hub(everyone):
    url = f"{BASE}/cassette/guides/"
    title = "Cassette Guides: Recording, Transcripts and Notes"
    desc = "Step by step guides to recording lectures, meetings and voice memos on iPhone and Android, then turning them into transcripts and notes."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en",
         "about": {"@id": f"{BASE}/cassette/#app"}, "publisher": {"@id": f"{BASE}/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Cassette", "item": f"{BASE}/cassette/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": url}]}]}
    items = "".join(f'<li><a href="/cassette/guides/{g["slug"]}/">{inline(g["h1"])}</a><span>{inline(g["description"])}</span></li>' for g in everyone)
    return head(title, desc, url, ld, "website") + f"""
  <div class="hero">
    <div class="eyebrow"><a href="/cassette/">Cassette</a></div>
    <h1>Guides</h1>
    <p class="by">Recording, transcripts and notes on iPhone and Android.</p>
  </div>

  <ul class="list">{items}</ul>

  <h2>Try Cassette</h2>
  <p>Press record. Your transcript and notes are ready when you stop.</p>
  {cta("hub")}
""" + FOOT


def write_sitemap(everyone):
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"  <url>\s*<loc>[^<]*/cassette/guides/[^<]*</loc>.*?</url>\n", "", s, flags=re.S)
    def entry(path, last, pri):
        return f"  <url>\n    <loc>{BASE}{path}</loc>\n    <lastmod>{last}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pri}</priority>\n  </url>\n"
    newest = max(g["updated"] for g in everyone)
    new = entry("/cassette/guides/", newest, "0.7") + "".join(entry(f"/cassette/guides/{g['slug']}/", g["updated"], "0.6") for g in everyone)
    anchor = re.search(r"  <url>\s*<loc>[^<]*/cassette/vs-wispr-flow/</loc>.*?</url>\n", s, flags=re.S)
    if not anchor:
        fail("sitemap.xml has no vs-wispr-flow entry to follow")
    s = s[:anchor.end()] + new + s[anchor.end():]
    open(p, "w", encoding="utf-8").write(s)


def write_llms(everyone):
    p = os.path.join(ROOT, "llms.txt")
    lines = [l for l in open(p, encoding="utf-8").read().split("\n") if "/cassette/guides/" not in l]
    at = next((i for i, l in enumerate(lines) if "/cassette/vs-wispr-flow/" in l), None)
    if at is None:
        fail("llms.txt has no vs-wispr-flow line to follow")
    new = [f"- [Cassette guides]({BASE}/cassette/guides/): step by step recording and notes guides for iPhone and Android"]
    new += [f"- [{plain(g['h1'])}]({BASE}/cassette/guides/{g['slug']}/)" for g in everyone]
    open(p, "w", encoding="utf-8").write("\n".join(lines[:at + 1] + new + lines[at + 1:]))


def write_links(everyone):
    """The line on /cassette, the site's strongest Cassette page: this is what gets a new guide found."""
    links = ", ".join(f'<a href="/cassette/guides/{g["slug"]}/" style="color:#ffb4a8;">{inline(g["h1"])}</a>' for g in everyone[:8])
    block = f'<p class="get-note">Guides: {links}. <a href="/cassette/guides/" style="color:#ffb4a8;">All guides</a>.</p>'
    open(os.path.join(GUIDES, "_links.html"), "w", encoding="utf-8").write(block + "\n")


def main():
    only_check = "--check" in sys.argv
    everyone = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(GUIDES, "*.json")))
                if os.path.basename(p) != "screens.json"]
    if not everyone:
        fail("no guides in tools/guides/")
    everyone.sort(key=lambda g: (g["published"], g["slug"]), reverse=True)
    for g in everyone:
        check(g, everyone)
    print(f"checked {len(everyone)} guides")
    if only_check:
        return
    for g in everyone:
        d = os.path.join(OUT, g["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(g, everyone, True))
        print("wrote /cassette/guides/" + g["slug"] + "/")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(hub(everyone))
    write_sitemap(everyone)
    write_llms(everyone)
    write_links(everyone)
    print("wrote the hub, sitemap.xml, llms.txt and tools/guides/_links.html. Now run: python3 seo-build.py")


if __name__ == "__main__":
    main()
