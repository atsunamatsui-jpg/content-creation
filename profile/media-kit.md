<!--
MEDIA KIT — render it, export to PDF, attach it to pitches.

  python3 scripts/render_pitch.py profile/media-kit.md --out build/media-kit.md

Keep it to one page. A two-page media kit gets read exactly as much as a
one-page one. Refresh the numbers monthly — a stale kit that overstates your
reach is worse than no kit.
-->

# {{creator.name}} · {{creator.handle}}

**{{creator.one_liner}}**

{{creator.location}} · {{creator.languages}} · {{creator.email}}

---

## Reach

| Channel | Audience | Avg. views | Engagement |
|---|---|---|---|
| TikTok | {{channels.tiktok.followers}} | {{channels.tiktok.avg_views}} | {{channels.tiktok.engagement_rate}} |
| Instagram | {{channels.instagram.followers}} | {{channels.instagram.avg_reel_views}} | {{channels.instagram.engagement_rate}} |
| YouTube | {{channels.youtube.subscribers}} | {{channels.youtube.avg_views}} | — |

## Audience

- **Where:** {{audience.top_countries}}
- **Age:** {{audience.age_range}}
- **Gender:** {{audience.gender_split}}
- **Worth knowing:** {{audience.notable}}

## Selected work

1. {{top_content.0.url}} — **{{top_content.0.result}}**
   {{top_content.0.why}}
2. {{top_content.1.url}} — **{{top_content.1.result}}**
   {{top_content.1.why}}
3. {{top_content.2.url}} — **{{top_content.2.result}}**
   {{top_content.2.why}}

## Why work with me

{{creator.differentiator}}

**Style:** {{creator.content_style}}

## Working together

| | |
|---|---|
| TikTok video | {{rates.currency}} {{rates.tiktok_video}} |
| Instagram Reel | {{rates.currency}} {{rates.instagram_reel}} |
| Story set (3) | {{rates.currency}} {{rates.instagram_story_set}} |
| YouTube integration | {{rates.currency}} {{rates.youtube_integration}} |
| UGC, licensed (not posted) | {{rates.currency}} {{rates.ugc_no_posting}} |

{{rates.bundle_note}}

**Turnaround:** {{terms.turnaround}} · {{terms.revisions}}
**Usage:** {{terms.usage_rights}}
**Payment:** {{terms.payment_terms}}
