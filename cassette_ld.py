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
