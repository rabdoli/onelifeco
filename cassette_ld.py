"""Structured data for the /cassette route.

Built the same way as luten_ld.py and for the same reason: what it says is a
factual claim about the product, so it lives in one readable place and has to be
kept true. The FAQ answers below are the ones on the page, word for word; if you
edit one, edit the other.

"Cassette" is an even more generic word than "Luten", so the job is again entity
disambiguation first. The App Store listing is the only profile Cassette has
(checked with Reza 2026-09-16: no social accounts yet). Add each new profile to
SAME_AS when it exists, never before.

NOT INCLUDED, DELIBERATELY: aggregateRating, for the reason given in
luten_ld.py. Cassette has no App Store ratings yet; add it when real ones exist.

THE FREE TIER IS STATED HERE ON PURPOSE. The rule against publishing a free tier
belongs to Luten. For Cassette, Reza approved "transcripts and notes free for 5
tapes a month" on 2026-09-16, and it matches the App Store description.
"""

BASE = "https://www.onelifeco.app"
APP_STORE = "https://apps.apple.com/us/app/cassette-ai-note-taker/id6812001404"

# RELEASED is False until Apple's public lookup lists Cassette. Until then its App
# Store URL is a 404 for every reader, so the build (seo-build.py, via
# prerelease() below) swaps each store link, badge and QR for "coming soon" copy
# and drops the URL from the structured data. tools/cassette_release.py sets this
# to True on release day and rebuilds; do not flip it by hand before the lookup
# answers, and do not hand-edit the store links in _source.html.
RELEASED = False

SAME_AS = [
    APP_STORE,
]

SOFTWARE_APP = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "@id": f"{BASE}/cassette/#app",
    "name": "Cassette",
    # The exact App Store title, so the two listings corroborate each other.
    "alternateName": "Cassette: AI Note Taker",
    # The App Store files it under Productivity with Business second; Business is
    # the closest of Google's supported applicationCategory values.
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "iOS 17.0 or later",
    "url": f"{BASE}/cassette/",
    "sameAs": SAME_AS,
    "downloadUrl": APP_STORE,
    "image": f"{BASE}/cassette/cassette-icon.png",
    "screenshot": [f"{BASE}/cassette/screen-{n}.webp" for n in ("deck", "notes", "transcript", "email", "shelf")],
    "description": ("A cassette deck for iPhone that records meetings, lectures, "
                    "interviews and voice memos, then writes the transcript, the "
                    "summary, the action items and the follow-up email."),
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock",
        "url": APP_STORE,
    },
    "publisher": {"@id": f"{BASE}/#org"},
}
if not RELEASED:
    # No download URL, no store sameAs, no availability until the listing exists.
    SOFTWARE_APP.pop("downloadUrl")
    _same = [u for u in SAME_AS if u != APP_STORE]
    if _same:
        SOFTWARE_APP["sameAs"] = _same
    else:
        SOFTWARE_APP.pop("sameAs")
    SOFTWARE_APP["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "USD"}

FAQ = [
    ("Is Cassette free?",
     "Yes, to download and to record, with no minute meter. Transcripts and "
     "notes are free for 5 tapes a month. Cassette Premium writes up every "
     "tape and backs up your shelf, and the annual plan starts with a 7-day "
     "free trial."),
    ("Does my audio leave my iPhone?",
     "The audio stays on your iPhone unless you sign in with Premium to back it up. "
     "Transcripts come from Apple speech recognition, on the device wherever your iPhone "
     "supports your language; otherwise that recording may be sent to Apple to transcribe. "
     "The notes are written by Apple's models, never by an outside AI service: on iOS 27 "
     "the transcript goes to Apple's Private Cloud Compute, which does not keep it, and on "
     "earlier iPhones the notes are written on the device."),
    ("Do I need an account?",
     "No. Recording, transcripts and notes all work without one. Signing in "
     "keeps your purchase with you, and with Premium it backs up every tape so "
     "it comes back on a new iPhone."),
    ("What goes in the notes?",
     "A short summary, the highlights worth remembering, and the action items "
     "with owners and due dates when they are mentioned, plus a follow-up email "
     "draft for the people who came up."),
    ("Which iPhones does it work on?",
     "Any iPhone on iOS 17 or later. Notes by Apple Intelligence need an iPhone "
     "that supports it; other iPhones get simpler notes, written on the device."),
    ("Can I share what it writes?",
     "Yes. Copy a whole tab in one tap, or save the email, the notes or the "
     "transcript as a PDF or a Word document."),
    ("Does it keep recording with the screen off?",
     "Yes. Lock your iPhone or switch apps and the tape keeps rolling. A phone "
     "call pauses it, and you pick up where you left off."),
    ("How do I delete my recordings?",
     "Open a tape and press Delete, or press and hold it on the shelf. Deleting "
     "your account removes every backed-up recording, transcript and note too."),
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
    """The JSON-LD script tags for /cassette, as one string."""
    import json
    return "".join(
        '<script type="application/ld+json">%s</script>'
        % json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        for d in (SOFTWARE_APP, FAQ_PAGE))


def prerelease(h):
    """Rewrite every Cassette App Store link in the site source into honest
    "coming soon" copy. Applied by seo-build.py while RELEASED is False. Every
    replacement must match exactly once, so a source edit that moves one of
    these fails the build loudly instead of shipping a dead link."""
    import re

    def once(h, old, new):
        assert h.count(old) == 1, "cassette prerelease: expected once: " + old[:70]
        return h.replace(old, new)

    def once_re(h, pat, new):
        h2, n = re.subn(pat, new, h)
        assert n == 1, "cassette prerelease: expected once: " + pat[:70]
        return h2

    # nav pill
    h = once(h, 'class="brand">Cassette<em>Live</em></a>',
                'class="brand">Cassette<em>Soon</em></a>')
    # Organization graph: the Cassette brand's only sameAs is the store URL
    h = once(h, ',"sameAs":["https://apps.apple.com/us/app/cassette-ai-note-taker/id6812001404"]}', '}')
    # hero: the button becomes the demo, the demo link becomes the status line
    h = once(h, '<div class="lh-cta"><a href="https://apps.apple.com/us/app/cassette-ai-note-taker/id6812001404?ct=web_hero" class="btn-light" target="_blank" rel="noopener">Download on the App Store <span class="arrow">&rarr;</span></a></div>',
                '<div class="lh-cta"><a href="#try" class="btn-light">Try the deck <span class="arrow">&rarr;</span></a></div>')
    h = once(h, '<div class="cas-try-link"><a href="#try">Or try the deck right here</a></div>',
                '<div class="cas-try-link">Coming soon to the App Store for iPhone</div>')
    # both QR codes encode the store URL
    h = once_re(h, r'\s*<div class="lh-qr" aria-hidden="false">\s*<div class="qr-code"><img src="/cassette/cassette-qr\.svg"[^>]*></div>\s*<span>Scan with your iPhone</span>\s*</div>', '')
    h = once_re(h, r'\s*<div class="qr"><div class="qr-code"><img src="/cassette/cassette-qr\.svg"[^>]*></div><span>Scan to download</span></div>', '')
    # Get section
    h = once(h, '>Download</p>\n      <h2>Get Cassette.</h2>', '>Coming Soon</p>\n      <h2>Get Cassette.</h2>')
    h = once(h, 'Free to download on the App Store. Scan the code or tap the badge.',
                'Coming soon to the App Store, free to download. Until then, try the deck above.')
    badge_open = '<a href="https://apps.apple.com/us/app/cassette-ai-note-taker/id6812001404?ct=web_badge" class="store-badge" target="_blank" rel="noopener" aria-label="Download Cassette on the App Store">'
    h = once(h, badge_open, '<span class="store-badge is-soon" aria-label="Cassette is coming soon to the App Store">')
    i = h.index('aria-label="Cassette is coming soon to the App Store">')
    close_old = '<span><small>Download on the</small><b>App Store</b></span></a>'
    j = h.index(close_old, i)
    h = h[:j] + '<span><small>Coming soon to the</small><b>App Store</b></span></span>' + h[j + len(close_old):]
    h = once(h, 'On the App Store for iPhone, iOS 17 or later.',
                'Coming soon to the App Store for iPhone, iOS 17 or later.')
    assert "id6812001404" not in h, "cassette prerelease: a store link survived"
    return h
