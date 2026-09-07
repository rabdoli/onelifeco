#!/usr/bin/env python3
"""
Generates https://onelifeco.app/luten/quiz/ .

WHY THIS EXISTS. Reverb's mandate (REVERB.md section 1b) makes new installs the
binding constraint and forces an UNTRIED channel after a missed week. The
web-to-app quiz funnel is the only untried channel an unattended agent can build
end to end: no login, no card, no new account. Built 2026-09-07.

WHAT IT HONESTLY IS. A conversion asset with an SEO by-product, not an
acquisition channel on its own. It converts the traffic the site already gets and
gives every other channel a destination more interesting than a static page. The
measured reason it was worth building: in the 14 days to 2026-09-07 the site took
16 iOS pageviews and NOT ONE of them tapped an App Store link, while all three
recorded taps came from Windows, Mac and Android, where a tap hits a wall. The
one audience that could install did not convert.

EDIT THIS FILE, NOT luten/quiz/index.html. The page is a build output.
Run:  python3 tools/build_quiz.py

Every string below passes a compliance gate before it is written, modelled on
tools/press/build_press_page.py in the luten-app repo. The script REFUSES to
write the page if a rule trips, because a marketing page that publishes the
catalogue size or a health claim is worse than no page at all.
"""
import os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "luten", "quiz", "index.html")
SEED = os.path.join(ROOT, "luten", "3am", "index.html")

APPSTORE = "https://apps.apple.com/us/app/luten-sleep-focus-sounds/id6777673392"

# ---------------------------------------------------------------- the questions

Q1 = [
    ("sleep",  "Get back to sleep",              "It is the middle of the night and you are awake."),
    ("start",  "Start something I keep putting off", "The task is not hard. Beginning it is."),
    ("focus",  "Concentrate with people around",  "An office, a shared flat, a cafe, a library that is not quiet."),
    ("down",   "Come down from a day",            "You finished hours ago and your head did not."),
    ("child",  "Settle a child",                  "Bedtime, a nap, or a car that needs to stay calm."),
]

Q2 = [
    ("voice",  "A voice",  "Talking, singing, a narrator, someone telling me to breathe."),
    ("tune",   "A tune",   "A melody or a beat I end up following instead of working."),
    ("change", "A change", "Anything that builds, shifts, or surprises me halfway through."),
]

# ------------------------------------------------------- the fifteen results
# Every title and every description below is copied from the real catalog in
# ~/luten-app/src/data/tracks*.ts. Nothing here is invented. If a track is
# renamed or removed in the app, fix it here in the same change.

RESULTS = {
 ("sleep","voice"): ("Three In The Morning",
   "Very low cello and double bass, one dark chord held with almost no movement in it.",
   "Nothing in the Luten catalog has a voice in it. No narration, no singing, no one telling you to relax. This one was written for the exact hour you are awake in."),
 ("sleep","tune"): ("Deep Pink Noise",
   "Pink noise with the highs taken away. Deep and close.",
   "No melody to follow, because there is no melody. Pink noise sits between the hiss of white and the rumble of brown, and this version has the top rolled off so it stays soft across a long night."),
 ("sleep","change"): ("The Long Middle",
   "A single sustained cello note, almost motionless from the first second to the last.",
   "It does not build and it does not resolve. There is nothing coming that you need to stay awake for."),

 ("start","voice"): ("Parallel Play",
   "Sparse felt piano over distant room tone. Company without conversation.",
   "Some people find it easier to begin when the room does not feel empty. This is that room, and nobody in it is going to talk to you."),
 ("start","tune"): ("Steady Brown Noise",
   "Brown noise held completely level. One thing to hold on to.",
   "Brown noise is a preference, not a treatment, and we will not tell you otherwise. What is true is that this one is synthesised to its actual spectral slope rather than made by pulling the treble off a recording, and it does not move."),
 ("start","change"): ("One Thing At A Time",
   "One sustained reed organ tone with the slightest movement in it.",
   "The whole track is the first second. Nothing arrives later."),

 ("focus","voice"): ("Pure White Noise",
   "Flat, even white noise. The same from the first second to the last.",
   "The worst office sound is a conversation you can almost make out, because your brain keeps trying to finish the sentence. Covering speech is a question of acoustics rather than wellness, and broadband noise is the plainest tool for it."),
 ("focus","tune"): ("Page Turns",
   "Pages turning in a still room, sparse and quiet, like a library desk nearby.",
   "No tempo anywhere in it. Lo-fi has a beat, and a beat is a thing to follow. Half an hour in you are nodding along instead of reading."),
 ("focus","change"): ("Steady Pink Noise",
   "Pink noise held perfectly level, with nothing to notice.",
   "Deliberately uneventful. There is nothing in here worth turning your head for."),

 ("down","voice"): ("Low Cedar Stillness",
   "Solo cello, long slow bows in the low register, woody and grounding.",
   "One instrument, no words, no guide. If wordless choirs still read as voices to you, this has none of that either."),
 ("down","tune"): ("The Long Exhale",
   "A descending pad whose fall is always longer than its rise.",
   "Shaped rather than composed. It is a slow shape repeating, not a piece of music going somewhere."),
 ("down","change"): ("Empty And Still",
   "A near-silent sine pad, mostly space.",
   "Closer to a quiet room than to a track. Most of it is the space between."),

 ("child","voice"): ("Kiri no Komoriuta",
   "A Japanese lullaby on solo koto, sparse and full of space, with a breathy shakuhachi far away.",
   "The lullabies in Luten come from all over the world and every one of them is instrumental, so nothing is being sung at a child in a language they are meant to understand."),
 ("child","tune"): ("Soft White Noise",
   "White noise with the top softened. Gentler over a long night.",
   "For a child who settles to a hush rather than a song. No tune, nothing that ends."),
 ("child","change"): ("Bíum Bíum",
   "An Icelandic lullaby on harmonium, sustained and very still, the reeds just audible.",
   "It circles rather than develops. Nothing in it wakes anybody up."),
}

SECTION_OF = {"sleep":"Sleep","start":"ADHD","focus":"Focus","down":"Stress","child":"Kids"}

# --------------------------------------------------------- the compliance gate

# Each rule is (pattern, why, case_sensitive). The casing rule MUST be
# case sensitive: the first version of this gate ran every rule under re.I, so
# `\bLUTEN\b` matched the ordinary word "Luten" and the gate refused to write a
# page that was entirely compliant. A gate that cries wolf gets switched off.
BANNED = [
    # catalogue size and free tier, in every form that has ever slipped through
    (r"\bsixteen\b", "spells out the free tier count", False),
    (r"\b\d+\s+sounds\b", "publishes a catalogue or free tier count", False),
    (r"\btwo (free )?sounds\b", "publishes the free tier", False),
    (r"\bsounds (are|is) free\b", "publishes the free tier", False),
    (r"\bfree forever\b", "publishes the free tier", False),
    (r"\bunlocks the\b", "describes the paywall mechanic", False),
    (r"\bfull library\b", "describes the paywall mechanic", False),
    (r"\bhundreds of sounds\b", "publishes a catalogue size", False),
    # health claims
    (r"\b(cures?|heals?|treats?|diagnoses?|remedy|clinically proven)\b", "health claim", False),
    (r"\b(will|helps? you) (sleep|fall asleep|focus|concentrate)\b", "efficacy claim", False),
    (r"\bproven to\b", "efficacy claim", False),
    (r"\bscientifically\b", "efficacy claim", False),
    # duration prescriptions
    (r"\bfor best results\b", "prescribes use", False),
    (r"\bjust \d+ minutes\b", "prescribes a duration", False),
    (r"\blisten for \d+", "prescribes a duration", False),
    # typography and casing
    (r"[–—]", "contains an en dash or em dash", False),
    (r"\bLUTEN\b", "all-caps brand in display text", True),
]

def check(text):
    problems = []
    for pattern, why, cased in BANNED:
        flags = 0 if cased else re.I
        for m in re.finditer(pattern, text, flags):
            problems.append(f"  {why}: ...{text[max(0,m.start()-60):m.end()+60]}...")
    return problems

# ------------------------------------------------------------------ the page

def seed_parts():
    src = open(SEED, encoding="utf-8").read()
    fonts = src[src.index('<link rel="preconnect"'):src.index('<meta charset=')]
    style = src[src.index('<style>'):src.index('</style>') + 8]
    ph    = src[src.index('<!-- Analytics: PostHog'):
                src.index('</script>', src.index('appstore_click')) + 9]
    return fonts, style, ph

def build():
    fonts, style, posthog = seed_parts()

    title = "Which Luten sound should you start with?"
    desc  = ("Two questions about what you are trying to do and what ruins it for you, "
             "and a named sound to start with. No talking, no vocals, no ads, no bright screen.")

    # Question markup
    q1 = "\n".join(
        f'      <button class="opt" data-q="1" data-v="{k}"><b>{html.escape(lab)}</b>'
        f'<span>{html.escape(sub)}</span></button>'
        for k, lab, sub in Q1)
    q2 = "\n".join(
        f'      <button class="opt" data-q="2" data-v="{k}"><b>{html.escape(lab)}</b>'
        f'<span>{html.escape(sub)}</span></button>'
        for k, lab, sub in Q2)

    # Every result, as real crawlable HTML. A quiz drawn only by JavaScript is
    # invisible to Google, to Bing and to the AI assistants that retrieve from
    # them, which would throw away the whole SEO half of the reason to build it.
    rows = []
    for (a, b), (track, sound, why) in RESULTS.items():
        lab1 = next(l for k, l, _ in Q1 if k == a)
        lab2 = next(l for k, l, _ in Q2 if k == b)
        rows.append(
            f'    <div class="card res" id="r-{a}-{b}">\n'
            f'      <div class="reskey">{html.escape(lab1)} &middot; {html.escape(lab2)} ruins it</div>\n'
            f'      <h3>{html.escape(track)}</h3>\n'
            f'      <p class="sound">{html.escape(sound)}</p>\n'
            f'      <p>{html.escape(why)}</p>\n'
            f'      <p class="note">In the {SECTION_OF[a]} section of Luten.</p>\n'
            f'      <a class="cta" href="{APPSTORE}?ct=web_quiz_{a}_{b}" '
            f'target="_blank" rel="noopener">Open {html.escape(track)} in Luten <span>&rarr;</span></a>\n'
            f'    </div>')
    all_results = "\n".join(rows)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{fonts}<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{html.escape(title)} | Luten</title>
<meta name="description" content="{html.escape(desc)}" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="https://onelifeco.app/luten/quiz/" />
<meta property="og:title" content="{html.escape(title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="Luten" />
<meta property="og:url" content="https://onelifeco.app/luten/quiz/" />
<meta property="og:image" content="https://luten-cc112.web.app/luten/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(title)}" />
<meta name="twitter:description" content="{html.escape(desc)}" />
<meta name="twitter:image" content="https://luten-cc112.web.app/luten/og-image.png" />
{style}
<style>
  .quiz {{ margin: 8px 0 10px; }}
  .step {{ display: none; }}
  .step.on {{ display: block; }}
  .qh {{ font-size: 13px; letter-spacing: 2px; text-transform: uppercase;
         color: rgba(255,255,255,0.4); margin-bottom: 12px; }}
  .opt {{ display: block; width: 100%; text-align: left; cursor: pointer;
          background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.10);
          border-radius: 16px; padding: 16px 20px; margin-bottom: 10px; color: inherit;
          font: inherit; line-height: 1.45; transition: border-color .15s, background .15s; }}
  .opt:hover, .opt:focus-visible {{ background: rgba(128,131,255,0.10);
          border-color: rgba(128,131,255,0.45); outline: none; }}
  .opt b {{ display: block; color: #fff; font-weight: 500; font-size: 17px; }}
  .opt span {{ display: block; color: rgba(255,255,255,0.5); font-size: 14px; margin-top: 3px; }}
  .back {{ background: none; border: none; color: rgba(255,255,255,0.45); font: inherit;
           cursor: pointer; padding: 6px 0; font-size: 14px; }}
  .reskey {{ font-size: 12px; letter-spacing: 1.5px; text-transform: uppercase;
             color: rgba(255,255,255,0.35); margin-bottom: 10px; }}
  .res h3 {{ margin-top: 0; font-size: 25px; }}
  .sound {{ color: rgba(255,255,255,0.85); font-size: 17px; }}
  #answer {{ margin-bottom: 8px; }}
  .all-results .res {{ margin-bottom: 14px; }}
</style>
{posthog}
</head>
<body>
<div class="glow"></div>
<div class="wrap">

  <header><div class="brand"><a href="/luten/">luten</a></div></header>

  <div class="hero">
    <div class="eyebrow">Two questions</div>
    <h1>Which sound should you start with?</h1>
    <p class="tag">Most sound apps hand everybody the same list and let you dig. This asks
    what you are actually doing and what you cannot stand, then names one thing to try.</p>
  </div>

  <div class="quiz">
    <div class="step on" id="s1">
      <div class="qh">1 of 2</div>
      <h2 style="margin-top:0">What are you trying to do?</h2>
{q1}
    </div>

    <div class="step" id="s2">
      <div class="qh">2 of 2</div>
      <h2 style="margin-top:0">What ruins it for you?</h2>
{q2}
      <button class="back" id="back">&larr; Back</button>
    </div>

    <div class="step" id="s3">
      <div class="qh">Start here</div>
      <div id="answer"></div>
      <button class="back" id="again">&larr; Try a different answer</button>
    </div>
  </div>

  <h2>What the app does with this</h2>
  <p>The version above is two taps and a fixed answer. In Luten you say how you feel in your
  own words, and Sona reads it on the phone itself using Apple's on-device language tools.
  Nothing you type is sent anywhere. It also learns which sounds you keep and which you skip,
  so the answer stops being generic.</p>
  <p>Luten is free to download on the App Store for iPhone. The subscription is optional and
  every subscription starts with a 7 day free trial.</p>
  <p><a class="cta" href="{APPSTORE}?ct=web_quiz_body" target="_blank" rel="noopener">Download
  Luten on the App Store <span>&rarr;</span></a></p>

  <h2>Every answer, in one place</h2>
  <p class="note">Fifteen combinations, so you can read them without answering anything.</p>
  <div class="all-results">
{all_results}
  </div>

  <h2>Questions people ask before they download</h2>
  <div class="card">
    <h3>Is there any talking?</h3>
    <p>No. There are no vocals anywhere in the catalog. No narration, no guided meditation,
    no course.</p>

    <h3>Does it play with the screen off?</h3>
    <p>Yes. Audio keeps going in the background and on the lock screen, sounds download for
    offline playback, and the player stays black while it plays.</p>

    <h3>Are these claims about what sound does to me?</h3>
    <p>No, and deliberately not. The descriptions above say what a sound is, not what it will
    do to you. Whether something suits you is your call, not ours, and how long you listen is
    your business.</p>

    <h3>Is it free?</h3>
    <p>It is free to download. The subscription is optional and every subscription starts with
    a 7 day free trial.</p>
  </div>

  <p class="note">More on the specifics:
  <a href="/luten/3am/">sounds for waking at 3am</a>,
  <a href="/luten/no-talking/">sleep sounds with no talking</a>,
  <a href="/luten/white-noise/">white, pink and brown noise</a>,
  <a href="/luten/rain-sounds/">rain sounds with no thunder</a>,
  <a href="/luten/fan-sounds/">fan sounds for sleeping</a>.</p>

  <footer>
    <p>Luten is A One Life Product. <a href="/luten/">Luten</a> &middot;
    <a href="/luten/press">Press kit</a> &middot;
    <a href="/">One Life</a> &middot;
    <a href="/privacypolicy/">Privacy</a> &middot;
    <a href="/termsofservice/">Terms</a></p>
  </footer>

</div>

<script>
(function () {{
  var pick = {{}};
  function show(id) {{
    ['s1','s2','s3'].forEach(function (s) {{
      document.getElementById(s).classList.toggle('on', s === id);
    }});
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}
  function cap(name, props) {{ if (window.posthog) posthog.capture(name, props || {{}}); }}

  document.querySelectorAll('.opt').forEach(function (b) {{
    b.addEventListener('click', function () {{
      var q = b.getAttribute('data-q'), v = b.getAttribute('data-v');
      if (q === '1') {{
        pick.a = v;
        cap('quiz_step_1', {{ answer: v }});
        show('s2');
      }} else {{
        pick.b = v;
        var src = document.getElementById('r-' + pick.a + '-' + pick.b);
        if (!src) return;
        var box = document.getElementById('answer');
        box.innerHTML = src.innerHTML;
        cap('quiz_complete', {{ doing: pick.a, ruins: pick.b, result: pick.a + '_' + pick.b }});
        history.replaceState(null, '', '#' + pick.a + '-' + pick.b);
        show('s3');
      }}
    }});
  }});

  document.getElementById('back').addEventListener('click', function () {{ show('s1'); }});
  document.getElementById('again').addEventListener('click', function () {{
    history.replaceState(null, '', location.pathname);
    show('s1');
  }});

  // A shared link like /luten/quiz/#sleep-voice opens straight on that answer.
  var h = (location.hash || '').replace('#', '');
  if (/^[a-z]+-[a-z]+$/.test(h) && document.getElementById('r-' + h)) {{
    var p = h.split('-');
    pick.a = p[0]; pick.b = p[1];
    document.getElementById('answer').innerHTML = document.getElementById('r-' + h).innerHTML;
    cap('quiz_deeplink', {{ result: p[0] + '_' + p[1] }});
    show('s3');
  }}
}})();
</script>
</body>
</html>
"""
    return page


if __name__ == "__main__":
    page = build()

    # Gate the human-written copy, not the boilerplate. Strip the reused PostHog
    # snippet and the CSS first, or the minified library trips the regexes.
    body = re.sub(r"<script>.*?</script>", " ", page, flags=re.S)
    body = re.sub(r"<style>.*?</style>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)

    problems = check(body)
    if problems:
        print("REFUSING TO WRITE. Compliance gate tripped:")
        print("\n".join(problems))
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"wrote {OUT}  ({len(page)} bytes, {len(RESULTS)} results)")
    print("compliance gate: passed")
