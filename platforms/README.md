# Platforms

## Get your actual list in here first

This folder ships with research on the platforms creators most commonly bookmark.
To replace that with *your* list, run the parser on your own machine:

```bash
# Option A — point it at Chrome directly (it auto-locates your profile)
python3 scripts/parse_bookmarks.py --stubs

# Option B — Chrome > Bookmark Manager > ⋮ > Export bookmarks, then:
python3 scripts/parse_bookmarks.py ~/Downloads/bookmarks.html --stubs

# Not sure of the exact folder name?
python3 scripts/parse_bookmarks.py --list-folders
```

That writes `discovered.md` (a checklist) and `discovered.csv` (feeds the tracker),
and with `--stubs`, a note file per platform under `notes/`.

## The one thing that saves the most time

**Influencer platforms fall into four categories, and only two of them accept
applications.** Creators routinely burn weeks trying to "apply" to platforms
that structurally cannot be applied to. Before you spend time on any platform,
work out which bucket it's in — `platform-guide.md` has the breakdown.

| Category | Can you apply? | Where your effort goes |
|---|---|---|
| **1. Creator marketplaces** | Yes — open campaign boards | Volume. Apply to many, fast. This is the toolkit's main use case. |
| **2. Native platform marketplaces** | Yes — if you meet the threshold | Meet the eligibility bar, then keep the profile warm |
| **3. Brand-side discovery CRMs** | **No** — brands search, you get invited | Make yourself *findable*. Do not cold-apply. |
| **4. Affiliate / commission networks** | Yes — but it's not a campaign | Set up once, then it's passive |

Category 3 is the trap. GRIN, Upfluence, Captiv8 and similar are software brands
buy to *find* creators — there is often no creator-side application at all. The
winning move there is a complete, keyword-rich public profile and connected
analytics, so their search surfaces you.

## Priority order when starting from zero

1. **Native marketplaces first** (TikTok Creator Marketplace, YouTube BrandConnect,
   Instagram's). Free, highest-trust, and brands filter by real analytics.
2. **Two or three creator marketplaces** — not ten. Depth beats breadth; a complete
   profile with portfolio pieces outperforms eight abandoned ones.
3. **One affiliate network** relevant to your niche, so ungated content still earns.
4. **Then** optimize for category-3 discoverability.
