"""Structured data for the /luten route.

Split out of seo-build.py because it had grown into two unreadable one-line
string literals, and because what it says is now a factual claim about the
product that has to be kept true. It was already wrong: the FAQ still told
Google the app "launches on the App Store August 18" and offered a
free-for-life waitlist that was removed before launch.

WHY THIS MATTERS MORE THAN NORMAL SEO MARKUP
"Luten" is not a coined word. Checked 2026-08-22, the entire Google top ten for
the bare query is a dictionary entry, the Middle English Compendium, the Luyten
surname, a Brandon Sanderson fandom wiki, Amazon, a genealogy site, Lute the
material, Lute in Poland, and a musician called Luten on Spotify. The app does
not appear at all. Google has no reason yet to believe an entity called Luten
exists, so the job is entity disambiguation before it is ranking.

`sameAs` is the documented lever. Google's Organization structured data guidance
describes it as "the URL of a page on another website with additional
information about your organization" and says such properties feed the knowledge
panel and help distinguish an organization from similar ones. Every profile we
control is listed so the same name resolves to one entity.

NOT INCLUDED, DELIBERATELY: aggregateRating. Google lists a rating or review as
REQUIRED for a SoftwareApplication rich result, so omitting it means no rich
result. The App Store reports userRatingCount 0 as of 2026-08-22, and inventing
a rating in markup is exactly what earns a structured-data manual action. Add it
when real ratings exist, not before.
"""

BASE = "https://www.onelifeco.app"
APP_STORE = "https://apps.apple.com/us/app/luten-sleep-focus-sounds/id6777673392"

# Every profile that is genuinely ours. Adding one we do not control, or one
# that 404s, weakens the set rather than strengthening it.
SAME_AS = [
    "https://www.producthunt.com/products/luten",
    # Approved and published 2026-08-30 (added by AlternativeTo on Aug 28).
    # Verified in a browser, not with curl: the site answers a non-browser
    # client with a Cloudflare challenge, so a 403 there is not a dead link.
    "https://alternativeto.net/software/luten/",
    "https://www.saashub.com/luten",
    APP_STORE,
    "https://www.instagram.com/lutenapp/",
    "https://www.tiktok.com/@lutenapp",
    "https://www.youtube.com/@lutenapp",
]

SOFTWARE_APP = {
    "@context": "https://schema.org",
    # MobileApplication is the schema.org subtype of SoftwareApplication for
    # phone apps. Google's software app rich result accepts it, and it tells an
    # assistant plainly that Luten is something you install on a phone.
    "@type": "MobileApplication",
    "@id": f"{BASE}/luten/#app",
    "name": "Luten",
    # The exact App Store title, so the two listings corroborate each other.
    "alternateName": "Luten: Sleep & Focus Sounds",
    "applicationCategory": "HealthApplication",
    "operatingSystem": "iOS",
    "url": f"{BASE}/luten/",
    "sameAs": SAME_AS,
    "downloadUrl": APP_STORE,
    "description": ("A sound-first iOS app for a busy mind: ADHD, focus, study "
                    "and sleep. Tell it how you feel and press play. "
                    "Not another meditation app."),
    # `offers` is one of Google's required properties. The app is a free
    # download with in-app subscriptions, so price 0 is the honest value.
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock",
        "url": APP_STORE,
    },
    "publisher": {"@id": f"{BASE}/#org"},
}

# Answers describe what the app IS. None of them promise an outcome, name a
# listening duration, or state the catalogue size.
#
# THIS LIST IS ALSO THE VISIBLE FAQ ON /luten. seo-build.py renders it into the
# page at the <!--LUTEN_FAQ--> marker in _source.html, so the page and the
# FAQPage markup are the same words by construction. Google requires FAQ markup
# to match visible content, and the two had already drifted apart (different
# answers, and a question in the markup that was not on the page).
#
# Several questions are phrased the way people ask an assistant ("What sounds
# help you fall asleep?"). The ANSWERS still only describe sound and the app:
# what people choose, what Luten has, and that Luten does not prescribe a
# length. That is the line in CLAUDE.md, and it holds for the question text too.
FAQ = [
    ("What is Luten?",
     "Luten is an iOS app that plays sound for sleep, focus, ADHD, "
     "stress and kids, and learns which sounds you actually stay with. "
     "It is made by One Life. The name is pronounced LOO-ten."),
    ("Is Luten a meditation app?",
     "No. Luten is functional sound, not guided meditation. You tell it "
     "how you feel and press play. No course, no breathing homework, no "
     "gurus."),
    ("What sounds help you fall asleep?",
     "People often choose steady sound with no beat and nothing that builds "
     "or drops: brown noise, pink noise, rain, ocean, fan hum and low held "
     "tones. Which one suits you is personal, so Luten lets you try them and "
     "puts the ones you keep playing first. It also shows a sleep score from "
     "Apple Health so you can see your nights."),
    ("What is the difference between white noise, pink noise and brown noise?",
     "White noise has equal energy at every frequency, so it sounds bright "
     "and hissy, like static. Pink noise has less energy as the pitch rises, "
     "so it sounds softer and more even, like steady rain. Brown noise drops "
     "off faster still, so it sounds deep and rumbling, like a waterfall or "
     "strong wind. Luten includes all three, each synthesised to its true "
     "spectrum."),
    ("What sound is good for focus while working?",
     "Many people work to steady sound with no lyrics and no sudden changes, "
     "such as cafe or library ambience, pink noise, brown noise, steady rain "
     "or soft instrumental study music. Luten's Focus mode plays that kind of "
     "sound and starts a focus timer, and ADHD mode adds a Pomodoro-style "
     "timer."),
    ("Can sound help an ADHD or busy mind focus?",
     "Luten's ADHD mode plays steady, low-surprise sound with a timer, "
     "made for a restless mind. It is a wellness tool, not a medical "
     "device, and it does not treat any condition."),
    ("How long should you listen to sleep sounds?",
     "There is no set length, and Luten does not prescribe one. Let a sound "
     "play until you stop it, or set a sleep timer so it fades out after the "
     "time you choose."),
    ("Is it safe to play sleep sounds all night?",
     "Luten can play all night with the screen locked, or stop on a sleep "
     "timer that fades the sound out. Every sound is instrumental with even "
     "loudness, so nothing jumps in the night. Keep the volume low and "
     "comfortable, and ask a doctor if you have questions about your hearing "
     "or your sleep."),
    ("What makes Luten different from other sleep sound apps?",
     "Luten is sound, not guided meditation: you say how you feel and press "
     "play, with no course to finish. It covers sleep, focus, stress, ADHD "
     "and kids in one app, every sound is instrumental with even loudness, "
     "and Sona, the companion that suggests sounds, runs on your iPhone. It "
     "also shows a sleep score from Apple Health."),
    ("Does Luten work without a connection?",
     "Yes. Download the sounds you want and they play with no signal, on "
     "a plane, in a basement, anywhere. Nothing has to buffer before it "
     "starts."),
    ("Does Luten keep playing when I lock my phone?",
     "Yes. Playback carries on with the screen off, with full controls "
     "on the lock screen and in Control Center, and a sleep timer if you "
     "want one."),
    ("Does Luten send my data anywhere?",
     "Sona, the companion you talk to, runs entirely on your iPhone "
     "using Apple's own on-device language tools. What you type stays on "
     "the phone."),
    ("How do I get Luten, and is it free?",
     "Luten is out now on the App Store for iPhone. It is a free "
     "download with an optional subscription, and every subscription "
     "starts with a 7-day free trial. Android is coming soon."),
]

FAQ_PAGE = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ
    ],
}


def blocks():
    """The JSON-LD script tags for /luten, as one string."""
    import json
    return "".join(
        '<script type="application/ld+json">%s</script>'
        % json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        for d in (SOFTWARE_APP, FAQ_PAGE))


def page_html(indent="        "):
    """The visible FAQ items for /luten, in the page's .diff markup."""
    from html import escape
    return "\n".join(
        '%s<div class="diff"><h4>%s</h4><p>%s</p></div>'
        % (indent, escape(q, quote=False), escape(a, quote=False))
        for q, a in FAQ)
