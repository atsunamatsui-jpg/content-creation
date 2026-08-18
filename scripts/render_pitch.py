#!/usr/bin/env python3
"""
Fill a pitch template from creator-profile.yml plus per-campaign details.

The point: you never retype your follower count, your best-performing post, or
your usage-rights clause again. You supply only what is genuinely campaign
specific, and the rest is substituted from your profile.

Usage:
    python3 scripts/render_pitch.py templates/campaign-application.md \
        --set brand="Muji" \
        --set campaign="Spring kitchenware launch" \
        --set hook="Your donabe is the one pot in my kitchen I use daily"

    # List every placeholder a template needs, without rendering:
    python3 scripts/render_pitch.py templates/cold-pitch-email.md --fields

Placeholders are {{dotted.paths}} into the profile ({{creator.name}},
{{channels.tiktok.followers}}, {{top_content.0.url}}) or free variables you
pass with --set ({{brand}}).
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
PROFILE = REPO / "creator-profile.yml"
PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_.\-]+)\s*\}\}")
COMMENT = re.compile(r"<!--.*?-->\s*", re.DOTALL)


def resolve(path, data):
    """Walk a dotted path into nested dicts/lists. Returns None if absent."""
    node = data
    for part in path.split("."):
        if isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template", help="Template file to render")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="Campaign-specific value, repeatable")
    ap.add_argument("--profile", default=str(PROFILE), help="Profile YAML (default: creator-profile.yml)")
    ap.add_argument("--out", help="Write to a file instead of stdout")
    ap.add_argument("--fields", action="store_true", help="List required placeholders and exit")
    ap.add_argument("--keep-notes", action="store_true",
                    help="Keep the template's HTML-comment usage notes in the output")
    args = ap.parse_args()

    tpl_path = Path(args.template)
    if not tpl_path.is_file():
        sys.exit(f"No such template: {tpl_path}")
    text = tpl_path.read_text(encoding="utf-8")

    if args.fields:
        names = sorted(set(PLACEHOLDER.findall(text)))
        profile = yaml.safe_load(Path(args.profile).read_text(encoding="utf-8")) or {}
        print(f"{tpl_path.name} uses {len(names)} placeholders:\n")
        for n in names:
            src = "profile" if resolve(n, profile) is not None else "--set REQUIRED"
            print(f"  {{{{{n}}}}}".ljust(42) + src)
        return

    profile = yaml.safe_load(Path(args.profile).read_text(encoding="utf-8")) or {}

    overrides = {}
    for pair in args.set:
        if "=" not in pair:
            sys.exit(f"--set expects KEY=VALUE, got: {pair}")
        k, v = pair.split("=", 1)
        overrides[k.strip()] = v

    missing, unfilled = [], []

    def substitute(match):
        key = match.group(1)
        if key in overrides:
            return overrides[key]
        value = resolve(key, profile)
        if value is None:
            missing.append(key)
            return f"<<MISSING:{key}>>"
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        value = str(value)
        if value == "FILL_ME":
            unfilled.append(key)
        return value

    rendered = PLACEHOLDER.sub(substitute, text)
    # The <!-- --> blocks are coaching notes for you, not for the brand.
    if not args.keep_notes:
        rendered = COMMENT.sub("", rendered).strip() + "\n"

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        print(f"Wrote {out}", file=sys.stderr)
    else:
        print(rendered)

    # Warn on stderr so it never contaminates the piped-out pitch text.
    if unfilled:
        print(f"\n[!] Still FILL_ME in creator-profile.yml: {', '.join(sorted(set(unfilled)))}",
              file=sys.stderr)
    if missing:
        print(f"[!] Not in profile, pass with --set: {', '.join(sorted(set(missing)))}",
              file=sys.stderr)
    if unfilled or missing:
        sys.exit(2)   # non-zero so you cannot pipe a half-filled pitch by accident


if __name__ == "__main__":
    main()
