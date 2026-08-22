#!/usr/bin/env python3
# Generates a static, crawlable HTML file per route, each with its own
# title / description / canonical / OG, ONLY its own page markup, and real hrefs.
#
# EDIT `_source.html`, NOT `index.html`.
# _source.html is the master template holding every page section. index.html is a
# BUILD OUTPUT (the home route) and is overwritten on every run, exactly like the
# other routes. Editing index.html directly means your change is silently lost the
# next time this runs.
#
# Run after editing:  python3 seo-build.py
import re, os
ROOT=os.path.dirname(os.path.abspath(__file__))
BASE="https://onelifeco.app"
SRC_FILE=os.path.join(ROOT,"_source.html")
if not os.path.exists(SRC_FILE):   # first run after the split: seed it from index.html
    SRC_FILE=os.path.join(ROOT,"index.html")
src=open(SRC_FILE,encoding="utf-8").read()

# per-route: (page id suffix, title, description, extra JSON-LD or None)
# Structured data for /luten now lives in luten_ld.py. It had grown into two
# unreadable one-line literals, and its content is a factual claim about the
# product: the FAQ was still telling Google the app launches on August 18 and
# offering a free-for-life waitlist that no longer exists.
import luten_ld
LUTEN_LD=luten_ld.blocks()
ROUTES={
 "luten":("Sound for ADHD, Focus &amp; Sleep That Learns You | Luten",
   "Luten is a sound-first iOS app for a busy mind: ADHD focus, study, deep sleep and calm. Tell it how you feel and press play. Not another meditation app.", LUTEN_LD),
 "about":("About &middot; One Life",
   "One Life is a quiet company building simple apps that make daily life simpler. We stay invisible so the apps can shine. Meet the company behind Luten.", None),
 "contact":("Contact &middot; One Life",
   "Questions, ideas, or feedback? Get in touch with One Life. We read everything.", None),
 "termsofservice":("Terms of Service &middot; One Life",
   "The Terms of Service for One Life and its apps, including Luten.", None),
 "privacypolicy":("Privacy Policy &middot; One Life",
   "How One Life handles your data: local-first, privacy-respecting, and transparent.", None),
}
# home <div id> for each route (page-home is active in source)
PAGEID={"home":"page-home","luten":"page-luten","about":"page-about","contact":"page-contact",
        "termsofservice":"page-terms","privacypolicy":"page-privacy"}

HOME_TITLE="One Life &middot; We light the way."
HOME_DESC="One Life is a quiet company building simple apps for the life you actually want to live. Starting with Luten, sound for sleep, focus, ADHD and stress."

ALL_PAGE_IDS=["page-home","page-luten","page-about","page-contact","page-terms","page-privacy"]

def _remove_div_block(h, pid):
    """Remove <div ... id="pid"> ... </div> including nested divs."""
    m=re.search(r'<div class="page[^"]*" id="'+re.escape(pid)+r'"[^>]*>', h)
    if not m: return h
    start, i, depth = m.start(), m.end(), 1
    while i < len(h) and depth > 0:
        nd = h.find('<div', i)
        nc = h.find('</div>', i)
        if nc == -1: return h            # unbalanced, leave the document untouched
        if nd != -1 and nd < nc:
            depth += 1; i = nd + 4
        else:
            depth -= 1; i = nc + 6
    return h[:start] + h[i:]

def strip_other_pages(h, keep_pid):
    for pid in ALL_PAGE_IDS:
        if pid != keep_pid:
            h=_remove_div_block(h, pid)
    return h

def real_hrefs(h):
    """<a href="#" data-route="luten"> -> <a href="/luten" data-route="luten">"""
    def sub(m):
        tag, route = m.group(0), m.group(1)
        return tag.replace('href="#"', 'href="'+('/' if route=='home' else '/'+route)+'"')
    return re.sub(r'<a [^>]*href="#"[^>]*data-route="([a-z]+)"[^>]*>', sub, h)

def build(route, title, desc, extra_ld):
    h=src
    # The home route lives at the site root. Computing this here (rather than after
    # the meta rewrites) matters: canonical and og:url are written below, so getting
    # it wrong emits <link rel="canonical" href="/home">, a URL that does not exist.
    # TRAILING SLASH MATTERS. Netlify 301s /luten to /luten/, so a canonical of
    # "/luten" names a URL that redirects rather than the one that serves 200.
    # Google follows it, but a self-referencing canonical that does not
    # self-reference wastes crawl budget and muddies which URL is the real one.
    url=BASE+"/" if route=="home" else BASE+"/"+route+"/"
    # title (appears in <title>, og:title, twitter:title)
    h=re.sub(r'<title>.*?</title>', '<title>'+title+'</title>', h, count=1)
    h=re.sub(r'(<meta property="og:title" content=").*?(")', r'\g<1>'+title+r'\g<2>', h, count=1)
    h=re.sub(r'(<meta name="twitter:title" content=").*?(")', r'\g<1>'+title+r'\g<2>', h, count=1)
    # description (meta, og, twitter)
    h=re.sub(r'(<meta name="description" content=").*?(")', r'\g<1>'+desc+r'\g<2>', h, count=1)
    h=re.sub(r'(<meta property="og:description" content=").*?(")', r'\g<1>'+desc+r'\g<2>', h, count=1)
    h=re.sub(r'(<meta name="twitter:description" content=").*?(")', r'\g<1>'+desc+r'\g<2>', h, count=1)
    # canonical + og:url (exact root only, not og:image)
    h=h.replace('<link rel="canonical" href="https://onelifeco.app/" />','<link rel="canonical" href="'+url+'" />')
    h=h.replace('<meta property="og:url" content="https://onelifeco.app/" />','<meta property="og:url" content="'+url+'" />')
    # extra JSON-LD (Luten SoftwareApplication) right after the structured-data graph
    if extra_ld:
        h=h.replace('<!-- fonts -->', extra_ld+'\n<!-- fonts -->', 1)
    # toggle active page: home off, this route on
    h=h.replace('<div class="page active" id="page-home">','<div class="page" id="page-home">')
    pid=PAGEID[route]
    h=h.replace('<div class="page" id="'+pid+'">','<div class="page active" id="'+pid+'">')
    # SEO: ship ONLY this route's page markup.
    # Previously every generated route contained all six page divs and merely toggled
    # CSS visibility, so all six URLs served byte-identical body content (~6,000 words,
    # 5 <h1>s). Google treats that as duplicate content and cannot tell what any single
    # URL is about, which is fatal for ranking /luten on its own terms.
    h=strip_other_pages(h, pid)
    # SEO: real hrefs in the RAW html. script.js sets these at runtime, but that makes
    # the internal link graph dependent on JS execution. Emitting them statically means
    # crawlers see a normal linked site.
    h=real_hrefs(h)
    if route=="home":                       # the home route is the site root
        outpath=os.path.join(ROOT,"index.html")
    else:
        outdir=os.path.join(ROOT,route); os.makedirs(outdir,exist_ok=True)
        outpath=os.path.join(outdir,"index.html")
    open(outpath,"w",encoding="utf-8").write(h)
    return url

made=[]
for r,(t,d,ld) in ROUTES.items():
    made.append(build(r,t,d,ld))
# The homepage is built too, so it also ships only its own markup and real hrefs.
# Previously it was the raw source: all six pages inline (duplicating every other
# route) and every internal link still href="#", so it passed no crawlable link
# equity to /luten despite being the strongest page on the domain.
made.append(build("home", HOME_TITLE, HOME_DESC, None))
print("generated per-route pages:")
for u in made: print("  "+u)
