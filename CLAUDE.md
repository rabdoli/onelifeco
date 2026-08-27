# onelifeco.app

The One Life website: the company pages and the Luten product page. Deployed by
Netlify from `main` on every push, usually live within about fifteen seconds.

**This is the SECOND of two repos.** The app, the marketing docs and the rest of
the standing rules live in `~/luten-app` (github.com/rabdoli/luten-app), and its
`CLAUDE.md` is the fuller version of what follows. A sweep run only over there
misses this repo completely, which is how a banned line survived in `luten_ld.py`
for four hours after it was purged everywhere else on 2026-08-27. **When you fix
published copy, grep both repos.** Keep the two files in step.

## Published copy: two things that are never said

**Never publish the free tier or the catalogue size.** Not the number of sounds,
not how many are free, not what a subscription unlocks. Not "16 sounds are free
forever", not "two free sounds in every section", not "unlocks the rest", not
"the full library", not "hundreds of sounds". "Free download, optional
subscription, 7-day trial on the annual plan" is the most that is ever said about
pricing mechanics. A count is not a "pricing term". The point is that someone
should open the app and find out, not weigh a number against the price before
they have heard anything.

**Never make a health claim**, and treat "what works" phrasing as a claim.
Describing content is fine ("brown noise, rain, low held tones"); saying it works
is not, including soft forms like "delta tones work best for sleep". Never
prescribe a listening duration or attach an outcome to one.

Also standing: **no em dashes or en dashes anywhere.** "Luten" in title case in
all running text; lowercase "luten" only as a styled wordmark; never all-caps.

## Edit the sources, never the build outputs

    _source.html    the master template holding all six page sections
    seo-build.py    per-route title, description, canonical, og:image
    luten_ld.py     the SoftwareApplication and FAQPage JSON-LD for /luten

    index.html, luten/index.html, about/index.html, contact/index.html,
    termsofservice/index.html, privacypolicy/index.html   ALL BUILD OUTPUTS

After editing a source, run `python3 seo-build.py`, then commit the sources and
the regenerated outputs together.

**Two traps, both of which have already cost a session:**

1. **A clean page can hide a dirty generator.** `luten/index.html` had a correct
   FAQ because someone hand-edited it; `luten_ld.py` still generated the banned
   free-tier line and would have restored it on the next build. Grep the
   generators, not just the pages.
2. **`_source.html` must exist.** If it is missing, `seo-build.py` silently seeds
   from `index.html`, which is the home route output and holds only `page-home`.
   Running the build in that state overwrites every other route with homepage
   markup. It was deleted once, on 2026-08-27, and only luck kept anyone from
   running the build before it was rebuilt.

To verify a build: every route must ship only its own `page-*` section, keep its
own title and canonical, keep `/luten` on `og-luten.png`, parse as valid JSON-LD,
and carry no banned copy.

## The Luten page carries launch badges

Fazier, Uneed, Product Hunt and SaaSHub, in `_source.html`. Add a new one only
once that listing is actually live, and check the image URL returns 200.
AlternativeTo is submitted and awaiting review; add its badge when it approves.
