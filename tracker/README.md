# Campaign tracker

`campaigns.csv` is the log. Open it in any spreadsheet app, or drive it with
`scripts/track.py`.

Why bother: the money in this is almost entirely in the follow-up. Most creators
apply, hear nothing, and move on — while the reply rate on follow-up #1 is
routinely the highest of any message you send. A tracker exists so that never
depends on memory.

## Columns

| Column | Meaning |
|---|---|
| `date_applied` | YYYY-MM-DD |
| `platform` | Where you applied — matches `platforms/discovered.csv` |
| `brand` / `campaign` | Who and what |
| `deliverables` | What you offered |
| `rate_quoted` / `currency` | What you asked for. Fill even when gifted — you want this history when raising rates. |
| `status` | `applied` → `in_talks` → `negotiating` → `won` / `lost` / `ghosted` |
| `followup_1_due` / `followup_2_due` | Auto-computed at +6 and +21 days |
| `outcome` | Final result, and the fee if won |
| `notes` | Contact name, what they said, why it died |

## Usage

```bash
python3 scripts/track.py add --platform Aspire --brand Muji \
    --campaign "Spring kitchenware" --deliverables "1 TikTok + 2 Stories" \
    --rate 80000 --currency JPY

python3 scripts/track.py due        # what needs a follow-up today
python3 scripts/track.py stats      # win rate, by platform
python3 scripts/track.py status --brand Muji --set won --outcome "80000 JPY"
```

## The habit that matters

Run `python3 scripts/track.py due` on a fixed day each week. Anything it lists,
send `templates/follow-up.md` for. That single loop is worth more than any
individual pitch improvement.
