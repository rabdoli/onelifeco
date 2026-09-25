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

**Grep the CONCEPT, not the string.** The 2026-08-27 sweep grepped for `16` and
the exact banned sentences, and on 2026-08-29 BetaList published **"Sixteen
sounds are free forever"** anyway, because the number was spelled out as a word.
Two prepared-copy files had it as a paraphrase ("two sounds in each section",
"two sounds per section are free"). The check that actually works:

    grep -rniE "sixteen|[0-9]+ sounds|two (free )?sounds|sounds (are|is) free|free forever|unlocks the|full library|hundreds of sounds"

Run it over BOTH repos and over every live listing, not just the one you came
for. Internal engineering notes and tests are exempt; anything a stranger could
read is not.


**Never make a health claim**, and treat "what works" phrasing as a claim.
Describing content is fine ("brown noise, rain, low held tones"); saying it works
is not, including soft forms like "delta tones work best for sleep". Never
prescribe a listening duration or attach an outcome to one.

Also standing: **no em dashes or en dashes anywhere.** "Luten" in title case in
all running text; lowercase "luten" only as a styled wordmark; never all-caps.

## Edit the sources, never the build outputs

    _source.html    the master template holding every page section
    seo-build.py    per-route title, description, canonical, og:image
    luten_ld.py     the SoftwareApplication and FAQPage JSON-LD for /luten
    cassette_ld.py  the same for /cassette (its FAQ must match the page word for word)

    index.html, luten/index.html, cassette/index.html, apps/spend/index.html,
    about/index.html, contact/index.html, termsofservice/index.html,
    privacypolicy/index.html                               ALL BUILD OUTPUTS

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
**AlternativeTo is approved and live** (verified 2026-08-30) but gets NO badge,
because AlternativeTo does not offer one. Their listing page carries no badge or
embed link and they publish no widget. Do not go looking again, and do not
improvise an image URL to fill the gap: a hotlinked unofficial graphic is worse
than four badges. Link to https://alternativeto.net/software/luten/ in text if it
is ever worth surfacing.

## The Cassette page (added 2026-09-16)

`/cassette` is the second product page, built on the Luten page's classes with a
maroon tint scoped to `#page-cassette`, a Cassette station on the home walk right
after Luten, and a working "try the deck" demo in script.js (section 6b) that
replays a sample meeting and never touches the microphone.

- **Cassette's free tier IS published, on purpose.** Reza approved "transcripts
  and notes free for 5 tapes a month" on 2026-09-16; it matches the App Store
  description. The never-publish-the-free-tier rule above is Luten's alone. Do
  not "fix" the Cassette page by removing it, and do not copy the wording onto
  anything Luten.
- Every image under `cassette/` and every `icons/cassette-*.svg` comes from
  `tools/make_cassette_assets.py` (icon, social card, App Store QR with
  ct=web_qr, gallery screens, feature orbs, hero waveform). Regenerate, never
  hand-edit.
- New build sources at the repo root need a forced 404 in netlify.toml, as
  `cassette_ld.py` has. Anything under `/tools/` is already blocked.
- **Store links are gated by `cassette_ld.RELEASED`** (False until Apple's lookup lists
  the app). While False, seo-build.py runs `cassette_ld.prerelease()`, which turns every
  App Store link, badge and QR on /cassette into "coming soon" copy, sets the nav pill to
  Soon, and drops the store URL from the structured data; each rewrite must match exactly
  once, so moving one of those elements fails the build instead of shipping a 404.
  `tools/cassette_release.py apply` flips the flag, updates llms.txt and the press kit,
  rebuilds and commits in one step (rehearsed 2026-09-25). Never flip it by hand.
- No social profiles exist for Cassette yet (checked with Reza). Add them to
  `cassette_ld.py` SAME_AS only once they are live.
- `/cassette/press` is `cassette/press.html`, hand-written like `luten/press.html`
  and NOT built by seo-build.py, so its PostHog block is another hand-kept copy.
  Its downloads live in `cassette/media/` (from make_cassette_assets.py). **Update
  its "Release" row the day App Review approves Cassette**; until then it says the
  app was submitted on 2026-09-16 with the date to follow.

## AI visibility files (added 2026-09-25)

- **The /luten FAQ has ONE source: `luten_ld.FAQ`.** `_source.html` holds only a
  `<!--LUTEN_FAQ ...-->` marker; seo-build.py renders the list into the page and
  into the FAQPage markup, so the two are the same words by construction (they had
  drifted: different answers, and a question in the markup that was not on the
  page). Add or edit a question in `luten_ld.py`, never in `_source.html`.
- **`llms.txt`** at the root is hand-written. It states each app's status, Luten's
  features, pricing and privacy stance. Update it the same day any of those change
  (Cassette's release, Android, a new app), and keep it inside both copy rules.
- **`robots.txt`** names the AI crawlers explicitly and allows everything.
- **`/apps/spend/`** is a coming-soon page (`page-spend`) with a Netlify Forms
  waitlist (`spend-waitlist`). Route keys in seo-build.py may contain a slash.
- **script.js no longer overwrites `document.title`.** Each built route ships only
  its own page, so render() only runs for that route, and the old overwrite put a
  short label in place of the SEO title in the rendered DOM that Google indexes.
- `/privacy` and `/terms` 301 to the real legal URLs (netlify.toml).
