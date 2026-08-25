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

BASE = "https://onelifeco.app"
APP_STORE = "https://apps.apple.com/us/app/luten-sleep-focus-sounds/id6777673392"

# Every profile that is genuinely ours. Adding one we do not control, or one
# that 404s, weakens the set rather than strengthening it.
SAME_AS = [
    APP_STORE,
    "https://www.instagram.com/lutenapp/",
    "https://www.tiktok.com/@lutenapp",
    "https://www.youtube.com/@lutenapp",
]

SOFTWARE_APP = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
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
FAQ = [
    ("Is Luten a meditation app?",
     "No. Luten is functional sound, not guided meditation. You tell it how you "
     "feel and press play. No course, no breathing homework, no gurus."),
    ("What is Luten?",
     "Luten is an iOS app that plays sound for sleep, focus, ADHD, stress and "
     "kids, and learns which sounds you actually stay with. It is made by One "
     "Life. The name is pronounced LOO-ten."),
    ("Can sound help an ADHD or busy mind focus?",
     "Luten's ADHD mode plays steady, low-surprise sound with a timer, made for "
     "a restless mind. It is a wellness tool, not a medical device, and it does "
     "not treat any condition."),
    ("What sounds help you sleep with a racing mind?",
     "Warm, beatless sound: brown noise, low tones and ocean drift. Luten also "
     "shows a sleep score from Apple Health so you can see your nights."),
    ("Does Luten have study and focus sound?",
     "Yes. Focus mode queues steady study sound and starts a timer, so you drop "
     "into work without falling down a playlist rabbit hole."),
    ("How do I get Luten, and is it free?",
     "Luten is on the App Store for iPhone. It is a free download with two free "
     "sounds in every section, and a subscription unlocks the rest."),
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
