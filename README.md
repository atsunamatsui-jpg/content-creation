# Influencer campaign application toolkit

A working kit for applying to influencer campaigns at volume without retyping
your stats, rewriting the same pitch, or losing track of follow-ups.

**Why it exists:** applying to campaigns is mostly repetitive data entry wrapped
around a small amount of genuinely creative pitching. This automates the
repetitive part so your attention goes to the part that actually wins deals —
the campaign-specific idea.

---

## Quick start

**Fastest path — the console.** `console/application-console.html` is a
fill-once-paste-everywhere tool: open it beside the platform tabs you're signed
into, fill your details once, and every application across all nine platforms
generates itself with copy buttons. Missing fields show as highlighted gaps so
you can't paste a hole by accident. Works offline; saves to your browser.

Each card also has an **operator prompt** for the
[Claude in Chrome](https://chromewebstore.google.com/search/claude) extension —
copy it into the side panel and it drafts the actual form in your logged-in
session. It's built for batch review: Auto mode for the drafting itself, then
one summary of everything it prepared before anything submits — you approve
which ones go out in a single pass instead of per field. It will not press
submit, accept terms, or enter payment/tax details without that approval, and
it's told to treat on-page brief text as data rather than instructions —
campaign briefs are third-party content, which is exactly the surface prompt
injection targets.

The command-line flow below does the same thing, plus follow-up tracking.

```bash
# 1. Read the strategy for your platforms — which ones you can actually apply to
cat platforms/my-platforms.md

# 2. Fill in your details — this is the only place your stats live
$EDITOR creator-profile.yml

# 3. Render a ready-to-paste application
python3 scripts/render_pitch.py templates/campaign-application.md \
    --set brand="Muji" \
    --set campaign="Spring kitchenware launch" \
    --set hook="Your donabe is the one pot in my kitchen that never goes back in the cupboard." \
    --set angle="A 'one pot, five weeknight dinners' series — unglamorous Tuesday cooking, not styled hero shots." \
    --set deliverables="1x TikTok (45-60s) + 2x IG Stories"

# 4. Log it so the follow-up isn't left to memory
python3 scripts/track.py add --platform Aspire --brand Muji \
    --campaign "Spring kitchenware" --rate 80000 --currency JPY

# 5. Once a week, every week
python3 scripts/track.py due
```

Not sure what a template needs?
`python3 scripts/render_pitch.py <template> --fields` lists every placeholder and
tells you which come from your profile and which you must pass with `--set`.

---

## What's here

```
creator-profile.yml        Your stats, rates and terms. Single source of truth.
profile/
  media-kit.md             One-page kit. Render → PDF → attach to pitches.
  faq-answers.md           Canned answers to the nine questions every form asks.
  bio-variants.md          Bios at 80 / 150 / 300 / 500 chars.
templates/
  campaign-application.md  The in-platform application box.
  cold-pitch-email.md      Direct to brand, no platform in between.
  gifting-to-paid.md       Turning a gifted offer into a paid one.
  rate-negotiation.md      Scripts for the five conversations that recur.
  follow-up.md             The two messages that produce most replies.
  rejection-repitch.md     Staying in the file for next quarter.
platforms/
  my-platforms.md          YOUR nine platforms, and which accept applications.
  platform-guide.md        The wider landscape, across all four categories.
  notes/                   One file per platform, pre-filled for your list.
rates/rate-card.md         How to price, and what to price separately.
console/
  application-console.html Fill once, generate all nine applications, copy-paste.
tracker/campaigns.csv      The log.
scripts/
  parse_bookmarks.py       Chrome bookmark folder → platform list.
  render_pitch.py          Profile + template → finished pitch.
  track.py                 Applications, follow-ups due, win rate by platform.
```

---

## The three things that actually move the numbers

Everything here exists to serve these:

**1. Specificity in the pitch.** The free-text box is the only place you compete.
Almost everyone writes "I love your brand and my audience would too." A concrete
content idea — a format, an opening frame, a reason it suits *your* audience —
beats a bigger follower count surprisingly often. That's why `--set hook=` and
`--set angle=` are the only things the template makes you write by hand.

**2. Following up.** Follow-up #1 routinely out-replies the original message.
Most creators never send it. `track.py due` exists solely to make that automatic.

**3. Not underpricing usage rights.** The most expensive mistake in creator work
isn't charging too little per post — it's handing over perpetual, all-channel
usage inside a single-post fee. `rates/rate-card.md` covers pricing it separately.

---

## Honest scope

This toolkit prepares applications. **It does not submit them.** Nothing here logs
into a platform on your behalf or auto-applies to campaigns.

That's partly practical — these platforms sit behind authenticated sessions, and
several prohibit automated access in their terms. But it's mostly that the final
step is the one where being a real person is the whole point. The toolkit removes
the forty minutes of boilerplate so you can spend five minutes on the idea that
actually gets you picked.

Also worth knowing: paid, gifted, *and* affiliate content generally require
disclosure, and the rules differ by country. `rates/rate-card.md` has more.
