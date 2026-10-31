#!/usr/bin/env python3
"""Builds the Cassette comparison pages: /cassette/vs-otter/ and /cassette/vs-wispr-flow/.

Hand-written pages like /cassette/press (NOT built by seo-build.py), so they carry their own
copy of the PostHog block, taken from cassette/press.html at build time: change the analytics
there and rerun this. Run from the repo root:  python3 tools/make_cassette_compare.py

Every competitor fact below was read from the competitor's own pages on 31 October 2026 and is
listed with its source at the foot of each page. Rules for editing (Reza, 31 Oct 2026, from the
Wispr Flow research): only facts we can source, said fairly; no logos or brand art of theirs; an
honest "who should pick which"; Cassette's own claims checked against the app's code (on-device
transcripts, On-device only, Private Cloud Compute on iOS 27). Prices are US App Store prices.
Lifetime has no number here on purpose: it had a launch price until 31 October 2026.
"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.onelifeco.app"
CHECKED = "31 October 2026"


def posthog():
    s = open(os.path.join(ROOT, "cassette", "press.html"), encoding="utf-8").read()
    a = s.index("<!-- Analytics: PostHog")
    b = s.index("</script>", a) + len("</script>")
    return s[a:b]


CSS = """
  :root { color-scheme: dark; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #140709; color: rgba(255,255,255,0.85);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6; overflow-x: hidden; }
  .glow { position: fixed; top: -20%; left: 50%; transform: translateX(-50%); width: 700px; height: 700px; border-radius: 50%;
    background: radial-gradient(circle, rgba(246,241,231,0.08), rgba(232,64,60,0.12) 40%, transparent 70%); pointer-events: none; z-index: 0; }
  .wrap { position: relative; z-index: 1; max-width: 880px; margin: 0 auto; padding: 0 24px; }
  header { padding: 32px 0 8px; display: flex; align-items: center; gap: 12px; }
  header a { display: flex; align-items: center; gap: 12px; text-decoration: none; }
  header img { width: 34px; height: 34px; border-radius: 22%; }
  .brand { font-weight: 300; letter-spacing: 1px; font-size: 22px; color: #fff; }
  .brand b { font-weight: 700; }
  .hero { padding: 48px 0 18px; }
  .hero .eyebrow { font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.4); margin-bottom: 14px; }
  .hero h1 { font-size: clamp(34px, 6vw, 52px); color: #fff; letter-spacing: -1px; line-height: 1.08; margin-bottom: 16px; }
  .hero .tag { font-size: clamp(16px, 3vw, 20px); color: rgba(255,255,255,0.6); max-width: 680px; }
  h2 { color: #fff; font-size: 22px; margin: 44px 0 14px; letter-spacing: -0.3px; }
  h3 { color: #fff; font-size: 16px; margin: 0 0 8px; }
  p { margin-bottom: 14px; color: rgba(255,255,255,0.7); }
  a { color: #ffb4a8; }
  ul { margin: 0 0 4px 20px; color: rgba(255,255,255,0.75); }
  li { margin-bottom: 7px; }
  .picks { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 22px 24px; margin-bottom: 16px; }
  .card.us { border-color: rgba(92,242,200,0.3); background: rgba(92,242,200,0.05); }
  .table { border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; overflow: hidden; margin-bottom: 14px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 12px 14px; font-size: 15px; vertical-align: top; text-align: left; }
  thead th { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: rgba(255,255,255,0.45); background: rgba(255,255,255,0.03); }
  tbody th { color: rgba(255,255,255,0.5); font-weight: 400; width: 22%; }
  tbody td { color: rgba(255,255,255,0.85); width: 39%; }
  tbody tr { border-top: 1px solid rgba(255,255,255,0.07); }
  td.cas { background: rgba(92,242,200,0.035); }
  .cta { display: inline-block; background: rgba(232,64,60,0.16); border: 1px solid rgba(232,64,60,0.45); color: #ffd9d2;
    text-decoration: none; border-radius: 999px; padding: 13px 26px; font-size: 15px; margin: 6px 10px 6px 0; }
  .note { font-size: 13px; color: rgba(255,255,255,0.4); }
  .sources li { font-size: 13px; color: rgba(255,255,255,0.45); word-break: break-word; }
  footer { padding: 44px 0 70px; color: rgba(255,255,255,0.35); font-size: 13px; border-top: 1px solid rgba(255,255,255,0.07); margin-top: 50px; }
  footer a { color: rgba(255,255,255,0.55); }
  @media (max-width: 640px) {
    .picks { grid-template-columns: 1fr; }
    thead { display: none; }
    tbody tr { display: block; padding: 10px 0; }
    tbody th, tbody td { display: block; width: auto; padding: 4px 14px; }
    tbody th { font-size: 12px; letter-spacing: .1em; text-transform: uppercase; }
    tbody td::before { content: attr(data-who) ": "; color: rgba(255,255,255,0.45); }
  }
"""

CASSETTE_STORE = ("https://apps.apple.com/app/apple-store/id6812001404?pt=129004817&amp;ct=web_compare&amp;mt=8",
                  "https://play.google.com/store/apps/details?id=app.cassette.deck&amp;utm_source=onelifeco&amp;utm_campaign=web_compare")

CASSETTE_PRICE = ("Recording is free and unlimited, with no minute meter. Premium is $1.99 a week, $5.99 a month, "
                  "or $49.99 a year with a 7-day free trial, or pay once with Lifetime. One purchase covers iPhone, iPad and Mac.")

PAGES = [
    {
        "slug": "vs-otter",
        "them": "Otter",
        "title": "Cassette vs Otter: a private, offline note taker compared (2026)",
        "desc": ("Cassette and Otter both turn conversations into transcripts and notes. Cassette works in airplane mode "
                 "with no outside AI service; Otter transcribes in its cloud and joins online meetings."),
        "tag": ("Both turn a conversation into a transcript and notes. The difference is where that happens: Cassette writes "
                "them without an outside AI service and works in airplane mode, while Otter transcribes in its cloud and "
                "can join your online meetings for you."),
        "pick_us": [
            "You record in the room: lectures, interviews, meetings around a table.",
            "You want your tapes kept on your phone, with no outside AI service.",
            "You are often offline, on a plane or in a basement lecture hall.",
            "You would rather pay once than subscribe.",
            "On a Mac, you don't want anything joining the call.",
        ],
        "pick_them": [
            "Your team wants a shared workspace, channels and comments.",
            "You want a notetaker that joins Zoom, Teams or Google Meet on its own.",
            "You need Salesforce, HubSpot or Zapier, or a web app and Windows.",
            "Your meetings are mostly online and you are always connected.",
        ],
        "rows": [
            ("Where the transcript is written",
             "On your phone. Android always; iPhone on the device for the languages it supports there, otherwise by Apple's speech recognition.",
             "On Otter's servers. Offline, Otter keeps recording and processes the tape once it can upload it. [1]"),
            ("Works in airplane mode",
             "Yes: recording, the transcript and the notes.",
             "Recording only. The live transcript pauses until a connection is back. [1]"),
            ("Who writes the notes",
             "Apple's models on iPhone and Mac (simpler notes, written on the device, where Apple Intelligence is missing), Cassette's own model on Android. Never an outside AI service.",
             "Otter's AI: summaries with action items and outlines, plus AI Chat. [2]"),
            ("Online meetings",
             "On the Mac, Cassette records what the Mac plays and your microphone. Nothing joins the call.",
             "Otter's notetaker joins Zoom, Microsoft Teams and Google Meet to write and share notes. [2]"),
            ("Free plan",
             "Unlimited recording. Transcripts and notes for 2 tapes a month.",
             "300 transcription minutes a month, up to 30 minutes per conversation, the 25 most recent kept. [2]"),
            ("Paid plan",
             CASSETTE_PRICE,
             "Pro is $16.99 a month, or $8.33 a month billed annually: 1,200 minutes a month, up to 90 minutes per conversation. [2]"),
            ("Pay once",
             "Yes, Lifetime.",
             "No one-time plan listed. [2]"),
            ("Devices",
             "iPhone, iPad, Mac, Apple Watch and Android.",
             "Web, iPhone, Android, Mac and Windows apps, and a Chrome extension. [2]"),
            ("Languages",
             "Your iPhone's language, wherever Apple's speech recognition supports it; many languages on Android.",
             "English, Spanish, French, German, Japanese and Chinese. [2]"),
            ("Teams",
             "Made for one person. No shared workspace.",
             "Shared workspaces, channels, and admin features on Business. [2]"),
        ],
        "sources": [
            ("Otter Help Center: Record with Otter offline or without an internet connection",
             "https://help.otter.ai/hc/en-us/articles/44008744581271-Record-with-Otter-offline-or-without-an-internet-connection"),
            ("Otter pricing and plan comparison", "https://otter.ai/pricing"),
        ],
    },
    {
        "slug": "vs-wispr-flow",
        "them": "Wispr Flow Notetaker",
        "title": "Cassette vs Wispr Flow Notetaker: meeting notes compared (2026)",
        "desc": ("Cassette and Wispr Flow Notetaker both record without a bot in your calls. Cassette runs on iPhone, Mac, "
                 "Apple Watch and Android and works offline; Wispr Notetaker runs on Mac and Windows."),
        "tag": ("Neither one sends a bot into your calls. Wispr Notetaker lives on your Mac or Windows PC next to Wispr's "
                "dictation; Cassette is a recorder for your phone, your wrist and your Mac that writes the notes without "
                "an outside AI service, even in airplane mode."),
        "pick_us": [
            "You record on your phone or Apple Watch: lectures, interviews, meetings in a room.",
            "You want the transcript and the notes written with no outside AI service, offline too.",
            "You are on Android, or you move between iPhone and Mac.",
            "You want a follow-up email drafted, or the notes sent to OneNote, Notion or Keep in one tap.",
            "You would rather pay once than subscribe.",
        ],
        "pick_them": [
            "You work on a Mac or Windows PC from one calendar meeting to the next.",
            "You want speaker names taken from your calendar invites and your dictionary.",
            "You want to ask questions across all your meetings, or reach them from Claude or ChatGPT.",
            "You also want Wispr's voice dictation in every app.",
        ],
        "rows": [
            ("Devices",
             "iPhone, iPad, Mac, Apple Watch and Android.",
             "Mac and Windows. Wispr says mobile is on its roadmap. [1]"),
            ("Bot in your calls",
             "None. On the Mac, Cassette records what the Mac plays and your microphone.",
             "None. It records on your computer, with no bot in the call. [1]"),
            ("Where it is processed",
             "No outside AI service. On Android everything is on the phone; on iPhone and Mac, Apple's models write the notes.",
             "Wispr's service. Wispr says customer data is processed in the United States, encrypted in transit and at rest. [2]"),
            ("Works in airplane mode",
             "Yes: recording, the transcript and the notes.",
             "Wispr does not say."),
            ("Free plan",
             "Unlimited recording. Transcripts and notes for 2 tapes a month.",
             "Included in Flow Free, with a weekly meeting limit. Recordings under five minutes don't count. [1]"),
            ("Paid plan",
             CASSETTE_PRICE,
             "Pro is $15 a month, or $12 a month billed annually, with dictation included. Unlimited Notetaker is on Growth, from $26 a month billed annually. [1]"),
            ("Pay once",
             "Yes, Lifetime.",
             "No one-time plan listed. [1]"),
            ("Languages",
             "Your iPhone's language, wherever Apple's speech recognition supports it; many languages on Android.",
             "Wispr says Notetaker transcribes in 21 languages. [3]"),
            ("Where it is ahead",
             "Apple Watch recording, a Record button on the Lock Screen and the Action button, a ready follow-up email, SEND TO your notes app.",
             "Names from your calendar, questions across meetings, MCP access for AI tools, and voice dictation. [1]"),
        ],
        "sources": [
            ("Wispr Flow pricing and FAQ", "https://wisprflow.ai/pricing"),
            ("Wispr: Private AI notetakers, 9 questions to ask", "https://wisprflow.ai/notetaker/most-private-ai-notetaker"),
            ("Wispr: How to use your meeting transcripts in any AI tool", "https://wisprflow.ai/notetaker/use-meeting-transcripts-in-ai-tools"),
        ],
    },
]


def page(p):
    url = f"{BASE}/cassette/{p['slug']}/"
    them = html.escape(p["them"])
    rows = "\n".join(
        f'        <tr><th scope="row">{html.escape(k)}</th><td class="cas" data-who="Cassette">{html.escape(c)}</td>'
        f'<td data-who="{them}">{html.escape(t)}</td></tr>' for k, c, t in p["rows"])
    us = "".join(f"<li>{html.escape(x)}</li>" for x in p["pick_us"])
    tm = "".join(f"<li>{html.escape(x)}</li>" for x in p["pick_them"])
    src = "".join(f'<li>[{i}] {html.escape(n)}: <a href="{u}" rel="nofollow noopener" target="_blank">{u}</a></li>'
                  for i, (n, u) in enumerate(p["sources"], 1))
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": url, "url": url, "name": p["title"], "description": p["desc"],
             "dateModified": "2026-10-31", "inLanguage": "en",
             "about": {"@id": f"{BASE}/cassette/#app"}, "publisher": {"@id": f"{BASE}/#org"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Cassette", "item": f"{BASE}/cassette/"},
                {"@type": "ListItem", "position": 2, "name": f"Cassette vs {p['them']}", "item": url}]},
        ],
    }
    t, d = html.escape(p["title"]), html.escape(p["desc"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{t}</title>
<meta name="description" content="{d}" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="{url}" />
<meta property="og:title" content="{t}" />
<meta property="og:description" content="{d}" />
<meta property="og:type" content="article" />
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
<!-- Built by tools/make_cassette_compare.py. Edit the generator, not this file. -->
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
<style>{CSS}</style>
{posthog()}
</head>
<body>
<div class="glow"></div>
<div class="wrap">

  <header><a href="/cassette/"><img src="/cassette/cassette-icon.png" alt="" width="34" height="34" /><span class="brand">cassette <b>deck</b></span></a></header>

  <div class="hero">
    <div class="eyebrow">Compare</div>
    <h1>Cassette vs {them}</h1>
    <p class="tag">{html.escape(p["tag"])}</p>
  </div>

  <h2>The short answer</h2>
  <div class="picks">
    <div class="card us"><h3>Pick Cassette if</h3><ul>{us}</ul></div>
    <div class="card"><h3>Pick {them} if</h3><ul>{tm}</ul></div>
  </div>

  <h2>Side by side</h2>
  <div class="table">
    <table>
      <thead><tr><th scope="col"></th><th scope="col">Cassette</th><th scope="col">{them}</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>
  <p class="note">Checked on {CHECKED}. Prices are US prices before tax; Cassette's are the App Store's. Numbers in brackets point to the sources below. If something here has changed, write to <a href="mailto:hello@onelifeco.app">hello@onelifeco.app</a> and we will fix it.</p>

  <h2>Before you record</h2>
  <p>Whichever you choose, ask everyone before you record. Some places require everyone's consent, and it is the decent thing to do.</p>

  <h2>Try Cassette</h2>
  <p>Free to download. Recording is free and unlimited, and the transcript and notes are free for 2 tapes a month.</p>
  <p><a class="cta" href="{CASSETTE_STORE[0]}" target="_blank" rel="noopener">Download on the App Store</a><a class="cta" href="{CASSETTE_STORE[1]}" target="_blank" rel="noopener">Get it on Google Play</a></p>
  <p><a href="/cassette/">More about Cassette</a> &middot; <a href="/cassette/{'vs-wispr-flow' if p['slug'] == 'vs-otter' else 'vs-otter'}/">Cassette vs {'Wispr Flow Notetaker' if p['slug'] == 'vs-otter' else 'Otter'}</a></p>

  <h2>Sources</h2>
  <ul class="sources">{src}</ul>
  <p class="note">{them} is a trademark of its owner. This page is ours, not theirs, and is not endorsed by them.</p>

  <footer>
    Cassette is A One Life Product. <a href="https://www.onelifeco.app/cassette/">onelifeco.app/cassette</a> &middot;
    <a href="https://www.onelifeco.app/privacypolicy">Privacy</a> &middot;
    <a href="https://www.onelifeco.app/termsofservice">Terms</a>
  </footer>

</div>
</body>
</html>
"""


for p in PAGES:
    out = os.path.join(ROOT, "cassette", p["slug"])
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page(p))
    print("wrote /cassette/" + p["slug"] + "/")
