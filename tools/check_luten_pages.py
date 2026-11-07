#!/usr/bin/env python3
"""Reads Luten's public pages for the copy rules, because a sweep is a moment and copy keeps being written.

    python3 tools/check_luten_pages.py    exit 1 and print each hit, exit 0 when clean

The guide generator only reads guides, so /luten, the hand-written pages and the press kit could drift without anyone
noticing. On 2026-11-06 /luten still said "to help you sleep, focus and de-stress". If this fails, fix the sentence,
never the check. Phrases that refuse a claim are allowed through ALLOW. Only the press kit may state prices.
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PAGES = ["luten/index.html", "luten/white-noise/index.html", "luten/rain-sounds/index.html", "luten/fan-sounds/index.html",
         "luten/3am/index.html", "luten/no-talking/index.html", "luten/quiz/index.html", "luten/press.html"]

# From the guide generator and the app's healthClaims test: the phrasing these pages were caught using.
BANNED = [
    (r"[–—]", "em or en dash"),
    (r"\b\d[\d,]*\+?\s+(free\s+|premium\s+|original\s+|different\s+)?(sounds?|tracks?|soundscapes?|mixes)\b", "catalogue size or free tier"),
    (r"\b(hundreds|thousands|dozens|tons|lots)\s+of\s+(sounds?|tracks?|soundscapes?)\b", "catalogue size in words"),
    (r"\bfree\s+(sounds?|tracks?|tier|plan|version|forever)\b|\bsounds?\s+(are|is)\s+free\b|\bfor free\b", "the free tier"),
    (r"\bunlock(s|ed|ing)?\b|\bpaywall\b|\bpremium\s+(sounds?|tracks?|only)\b|\bany tier\b", "the free tier"),
    (r"\b(helps?|helping|lets?|makes?|gets?|puts?|sends?)\s+(you\s+|your\s+\w+\s+|people\s+)?(to\s+)?(fall\s+asleep|sleep|focus|relax|calm|concentrate|unwind|drift|study)\b", "says what a sound does"),
    (r"\bhelp(s|ing)?\b.{0,30}\b(settle|focus|sleep|calm|concentrate|wind down|de-stress)\b", "says what a sound does"),
    (r"\b(better|deeper|faster|longer|improved|quality|restful|restorative)\s+(sleep|focus|rest|concentration)\b|\bsleep\s+(better|faster|longer|deeper)\b", "promises better sleep or focus"),
    (r"\b(reduc|lower|boost|rais|improv|relie|eas|sooth|quiet|calm)(e|es|ed|ing|ve|ves|ved|ving|s)?\s+(your\s+|the\s+)?(stress|anxiety|cortisol|dopamine|blood pressure|heart rate|mood|tinnitus)\b", "claims an effect"),
    (r"\b(stress|anxiety|pain|tinnitus)\s+relief\b", "a claimed relief"),
    (r"\bcalming\b|\bsoothing\b|\bwhat (calms|settles|works)\b|\bactually settles\b|\bde-stress\b|\bsound for adhd\b|\bspecially good for\b", "credits a sound with a result"),
    (r"\bright sounds?\b|\byour sound companion\b|\bsound does the work\b|\bquiet anchor\b|\bcarry you\b|\bbring you back down\b", "promises a result"),
    (r"\byour brain\b|\byour nervous system\b|\bmelatonin\b|\bcortisol\b|\bdopamine\b|\bdeep sleep\b|\bsleep cycle", "a mechanism stated as fact"),
    (r"\bstop(s|ped)? (noticing|hearing)\b|\beasier to (leave alone|ignore)\b|\bto stop noticing\b|\bone you stop hearing\b", "says what a sound does to attention"),
    (r"\b(within|after|in|over) (a|an|one|two|three|four|five|six|ten|about a|a few) (min|minute|minutes|hour|hours|night|nights|week|weeks)\b", "attaches an outcome to a length of time"),
    (r"\b(every|each)\s+night\b|\bnightly\b", "a prescribed routine"),
    (r"\bof adults\b", "a health statistic with no source"),
    (r"\bcompanion\b", "Sona is not called a companion"),
    (r"\boffline\b|\bairplane mode\b|\bdownload(ed|s)? (the )?sounds?\b|\bsounds? (can be )?download", "offline needs a subscription, which can't be said without the free tier"),
    (r"\bno vocals\b|\bzero vocals\b|\bevery sound is instrumental\b|\bvoice or lyrics\b", "untrue: a few tracks have wordless voices or a cafe murmur"),
    (r"\buniform (loudness|mastering)\b|\bevery track is mastered\b", "say nearly every track, never every"),
    (r"\bguarantee[sd]?\b|\bnever wake\b|\bwon't wake\b|\bclinically\b|\bscientifically\b|\bmedically proven\b", "a promise the app can't keep"),
]

# Sentences that say the opposite of a claim, allowed word for word. Add one only when it refuses a claim.
ALLOW = [
    "no one telling you to relax",
    'the same as "no vocals"',  # the no-talking page explains the two terms, and says nothing about Luten here
    "No vocals also rules out",
]


def page_text(path):
    raw = open(os.path.join(ROOT, path), encoding="utf-8").read()
    if path == "luten/index.html":
        start = raw.find('id="page-luten"')
        end = raw.find('<footer class="footer">', start)
        head = raw[:raw.find("<body")]
        raw = head + raw[start:end]
    meta = " ".join(re.findall(r'<meta[^>]+content="([^"]*)"', raw))
    faq = " ".join(re.findall(r'"(?:name|text|description)":\s*"([^"]*)"', raw))
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", raw, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body) + " " + meta + " " + faq)
    return re.sub(r"\s+", " ", text)


def main():
    hits = 0
    for path in PAGES:
        text = page_text(path)
        for phrase in ALLOW:
            text = text.replace(phrase, " ")
        if path != "luten/press.html":  # journalists need the prices; everyone else gets them from the store
            for m in re.finditer(r"\$\s?\d", text):
                hits += 1
                print(f"{path}: a price: ...{text[max(0, m.start() - 40):m.end() + 30]}...")
        for pat, why in BANNED:
            for m in re.finditer(pat, text, re.I):
                hits += 1
                print(f"{path}: {why}: ...{text[max(0, m.start() - 50):m.end() + 40]}...")
    if hits:
        print(f"{hits} hits. Fix the sentence, never this check.")
        return 1
    print(f"checked {len(PAGES)} Luten pages: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
