#!/usr/bin/env python3
# Generates a static, crawlable HTML file per route from index.html (the home source),
# each with its own title / description / canonical / OG + the right .page active.
# Run this after editing index.html:  python3 seo-build.py
import re, os
ROOT=os.path.dirname(os.path.abspath(__file__))
BASE="https://onelifeco.app"
src=open(os.path.join(ROOT,"index.html"),encoding="utf-8").read()

# per-route: (page id suffix, title, description, extra JSON-LD or None)
LUTEN_LD='<script type="application/ld+json">{"@context":"https://schema.org","@type":"SoftwareApplication","name":"Luten","applicationCategory":"HealthApplication","operatingSystem":"iOS","url":"%s/luten","description":"A sound-first iOS app: the right sound for how you feel. Sleep, focus, calm, and a real soft spot for ADHD. Not meditation, just press play.","publisher":{"@type":"Organization","name":"One Life"}}</script>'%BASE
ROUTES={
 "luten":("Luten &middot; Sound for the mind. | One Life",
   "Luten is a sound-first iOS app: the right sound for how you feel. Sleep, focus, calm, and a real soft spot for ADHD. Not meditation, just press play.", LUTEN_LD),
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
PAGEID={"luten":"page-luten","about":"page-about","contact":"page-contact",
        "termsofservice":"page-terms","privacypolicy":"page-privacy"}

def build(route, title, desc, extra_ld):
    h=src
    url=BASE+"/"+route
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
    outdir=os.path.join(ROOT,route); os.makedirs(outdir,exist_ok=True)
    open(os.path.join(outdir,"index.html"),"w",encoding="utf-8").write(h)
    return url

made=[]
for r,(t,d,ld) in ROUTES.items():
    made.append(build(r,t,d,ld))
print("generated per-route pages:")
for u in made: print("  "+u)
