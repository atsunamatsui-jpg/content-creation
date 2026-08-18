#!/usr/bin/env python3
"""
Extract a Chrome bookmark folder (default: "Influencer Platforms") into a
platform list this toolkit can work from.

Runs on YOUR machine, where your Chrome profile actually lives.

Accepts either:
  * Chrome's live `Bookmarks` file (JSON, no extension), or
  * an exported bookmarks HTML file (Chrome -> Bookmark Manager -> Export)

Usage:
    python3 scripts/parse_bookmarks.py                      # auto-locate Chrome
    python3 scripts/parse_bookmarks.py path/to/bookmarks.html
    python3 scripts/parse_bookmarks.py --folder "Brand Deals"
    python3 scripts/parse_bookmarks.py --stubs               # also write platform notes

Outputs:
    platforms/discovered.md   human-readable checklist
    platforms/discovered.csv  machine-readable, feeds the campaign tracker
"""
import argparse
import csv
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
DEFAULT_FOLDER = "Influencer Platforms"

# Chrome profile locations by platform. First match wins.
# Proper display names for platforms whose domain does not capitalize cleanly.
# Extend freely — anything not listed falls back to the domain heuristic.
KNOWN_PLATFORMS = {
    "aspire.io": "Aspire",
    "aspireiq.com": "Aspire",
    "grin.co": "GRIN",
    "later.com": "Later Influence",
    "mavrck.co": "Later Influence (Mavrck)",
    "upfluence.com": "Upfluence",
    "levanta.io": "Levanta",
    "shareasale.com": "ShareASale",
    "impact.com": "Impact",
    "cj.com": "CJ Affiliate",
    "rakutenadvertising.com": "Rakuten Advertising",
    "shopmy.us": "ShopMy",
    "shopltk.com": "LTK",
    "rewardstyle.com": "LTK (rewardStyle)",
    "creator.co": "Creator.co",
    "collabstr.com": "Collabstr",
    "insense.pro": "Insense",
    "billo.app": "Billo",
    "trend.io": "Trend.io",
    "joinbrands.com": "JoinBrands",
    "popularpays.com": "Popular Pays",
    "captiv8.io": "Captiv8",
    "izea.com": "IZEA",
    "tribegroup.co": "Tribe",
    "skeepers.io": "Skeepers",
    "brandbassador.com": "Brandbassador",
    "afluencer.com": "Afluencer",
    "intellifluence.com": "Intellifluence",
    "cohley.com": "Cohley",
    "socialnative.com": "Social Native",
    "thecriqle.com": "The Criqle",
    "massivesway.com": "Massive Sway",
    "swaygroup.com": "Massive Sway (Sway Group)",
    "inmar.com": "Inmar Intelligence",
    "fohr.co": "Fohr",
    "activate.social": "Activate",
    "stackinfluence.com": "Stack Influence",
    "mavely.com": "Mavely",
    "planethowl.com": "Howl",
    "creatormarketplace.tiktok.com": "TikTok Creator Marketplace",
    "tiktok.com": "TikTok Creator Marketplace",
    "affiliate-program.amazon.com": "Amazon Associates",
    "affiliate-program.amazon.co.jp": "Amazon Associates JP",
    "amazon.com": "Amazon Influencer Program",
    "youtube.com": "YouTube BrandConnect",
    "facebook.com": "Meta Creator Marketplace",
    "instagram.com": "Instagram Creator Marketplace",
    "whalar.com": "Whalar",
    "ubiquitousinfluence.com": "Ubiquitous",
}

# Second-level TLDs where the registrable label sits one position further left.
MULTI_TLDS = {"co.uk", "co.jp", "com.au", "co.nz", "com.br", "co.kr", "com.mx", "co.za"}

CHROME_PATHS = [
    "~/Library/Application Support/Google/Chrome/Default/Bookmarks",
    "~/Library/Application Support/Google/Chrome/Profile 1/Bookmarks",
    "~/Library/Application Support/Chromium/Default/Bookmarks",
    "~/.config/google-chrome/Default/Bookmarks",
    "~/.config/google-chrome/Profile 1/Bookmarks",
    "~/.config/chromium/Default/Bookmarks",
    "~/AppData/Local/Google/Chrome/User Data/Default/Bookmarks",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks"),
]


class NetscapeBookmarkParser(HTMLParser):
    """Parses the Netscape bookmark format Chrome exports.

    The format nests a <DL> under each <H3> folder heading and never closes
    its <DT> tags, so we track folder depth off <DL> open/close instead.
    """

    def __init__(self):
        super().__init__()
        self.root = {"name": "__root__", "children": []}
        self.stack = [self.root]
        self.pending_folder = None
        self.in_h3 = False
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h3":
            self.in_h3 = True
            self.pending_folder = {"name": "", "children": []}
        elif tag == "dl":
            # A <DL> right after an <H3> is that folder's body.
            if self.pending_folder is not None:
                self.stack[-1]["children"].append(self.pending_folder)
                self.stack.append(self.pending_folder)
                self.pending_folder = None
            else:
                self.stack.append(self.stack[-1])
        elif tag == "a" and attrs.get("href"):
            self.current_link = {"name": "", "url": attrs["href"]}

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_h3 = False
        elif tag == "dl":
            if len(self.stack) > 1:
                self.stack.pop()
        elif tag == "a" and self.current_link:
            self.stack[-1]["children"].append(self.current_link)
            self.current_link = None

    def handle_data(self, data):
        if self.in_h3 and self.pending_folder is not None:
            self.pending_folder["name"] += data.strip()
        elif self.current_link is not None:
            self.current_link["name"] += data.strip()


def load_chrome_json(path):
    """Normalize Chrome's Bookmarks JSON into our {name, children|url} shape."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    def walk(node):
        if node.get("type") == "folder":
            return {
                "name": node.get("name", ""),
                "children": [walk(c) for c in node.get("children", [])],
            }
        return {"name": node.get("name", ""), "url": node.get("url", "")}

    roots = data.get("roots", {})
    children = [
        walk(v) for k, v in roots.items() if isinstance(v, dict) and "children" in v
    ]
    return {"name": "__root__", "children": children}


def load_html(path):
    parser = NetscapeBookmarkParser()
    with open(path, encoding="utf-8", errors="replace") as fh:
        parser.feed(fh.read())
    return parser.root


def find_folder(node, target):
    """Depth-first search for a folder by name, case-insensitive."""
    if node.get("name", "").strip().lower() == target.strip().lower() and "children" in node:
        return node
    for child in node.get("children", []):
        if "children" in child:
            hit = find_folder(child, target)
            if hit:
                return hit
    return None


def collect_links(node, out=None):
    """Flatten a folder to its bookmarks, including any subfolders."""
    out = [] if out is None else out
    for child in node.get("children", []):
        if "url" in child and child["url"].startswith(("http://", "https://")):
            out.append(child)
        elif "children" in child:
            collect_links(child, out)
    return out


def list_folders(node, depth=0, out=None):
    out = [] if out is None else out
    for child in node.get("children", []):
        if "children" in child:
            out.append(("  " * depth) + (child.get("name") or "(unnamed)"))
            list_folders(child, depth + 1, out)
    return out


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def platform_name(link):
    """Prefer a clean domain over the bookmark title, which is often a page name."""
    host = urlparse(link["url"]).netloc.lower()
    host = re.sub(r"^www\.", "", host)

    if host in KNOWN_PLATFORMS:
        return KNOWN_PLATFORMS[host], host
    # A known platform reached via a subdomain, e.g. creators.aspire.io
    parts = host.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[i:])
        if parent in KNOWN_PLATFORMS:
            return KNOWN_PLATFORMS[parent], host

    # Fall back to the registrable label: the one just left of the public suffix.
    suffix_len = 2 if ".".join(parts[-2:]) in MULTI_TLDS else 1
    idx = len(parts) - suffix_len - 1
    base = parts[idx] if idx >= 0 else parts[0]
    return base.replace("-", " ").title(), host


def autolocate():
    for candidate in CHROME_PATHS:
        path = Path(os.path.expanduser(candidate))
        if path.is_file():
            return path
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?", help="Bookmarks JSON or exported HTML. Omit to auto-locate Chrome.")
    ap.add_argument("--folder", default=DEFAULT_FOLDER, help=f'Folder name (default: "{DEFAULT_FOLDER}")')
    ap.add_argument("--stubs", action="store_true", help="Write a research-notes stub per platform")
    ap.add_argument("--list-folders", action="store_true", help="Print every folder name and exit")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite discovered.md even though it has been edited")
    args = ap.parse_args()

    source = Path(args.source) if args.source else autolocate()
    if not source or not source.is_file():
        sys.exit(
            "Could not find a bookmarks file.\n"
            "Pass one explicitly, or export from Chrome:\n"
            "  Bookmark Manager -> the : menu -> Export bookmarks\n"
            "  python3 scripts/parse_bookmarks.py ~/Downloads/bookmarks.html"
        )

    # Chrome's live file is JSON with no extension; exports are HTML.
    if source.suffix.lower() in (".html", ".htm"):
        tree = load_html(source)
    else:
        try:
            tree = load_chrome_json(source)
        except (json.JSONDecodeError, UnicodeDecodeError):
            tree = load_html(source)

    if args.list_folders:
        print(f"Folders in {source}:")
        for line in list_folders(tree):
            print(" ", line)
        return

    folder = find_folder(tree, args.folder)
    if not folder:
        print(f'No folder named "{args.folder}" found in {source}.', file=sys.stderr)
        print("\nFolders that do exist:", file=sys.stderr)
        for line in list_folders(tree):
            print("  " + line, file=sys.stderr)
        sys.exit(1)

    links = collect_links(folder)
    if not links:
        sys.exit(f'Folder "{args.folder}" has no http(s) bookmarks in it.')

    # Collapse multiple bookmarks pointing at the same platform.
    seen = {}
    for link in links:
        name, host = platform_name(link)
        seen.setdefault(host, {"name": name, "host": host, "urls": [], "titles": []})
        seen[host]["urls"].append(link["url"])
        seen[host]["titles"].append(link["name"])
    platforms = sorted(seen.values(), key=lambda p: p["name"].lower())

    csv_path = REPO / "platforms" / "discovered.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["platform", "domain", "primary_url", "bookmark_title", "slug"])
        for p in platforms:
            writer.writerow([p["name"], p["host"], p["urls"][0], p["titles"][0], slugify(p["name"])])

    md_path = REPO / "platforms" / "discovered.md"
    # discovered.md carries ticked checkboxes once you start using it. Never
    # silently throw that away.
    if md_path.exists() and not args.force:
        print(f"{md_path.relative_to(REPO)} already exists — not overwriting.")
        print(f"Wrote {csv_path.relative_to(REPO)} only. Re-run with --force to replace it.")
        return
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(f"# Platforms from your \"{args.folder}\" bookmark folder\n\n")
        fh.write(f"Extracted from `{source}` — {len(platforms)} platforms, {len(links)} bookmarks.\n\n")
        fh.write("| # | Platform | URL | Profile complete | Applied to a campaign |\n")
        fh.write("|---|----------|-----|------------------|----------------------|\n")
        for i, p in enumerate(platforms, 1):
            fh.write(f"| {i} | {p['name']} | <{p['urls'][0]}> | [ ] | [ ] |\n")
        fh.write("\nNext: `platforms/notes/` for what each application form asks for.\n")

    if args.stubs:
        notes = REPO / "platforms" / "notes"
        notes.mkdir(exist_ok=True)
        for p in platforms:
            stub = notes / f"{slugify(p['name'])}.md"
            if stub.exists():
                continue  # never clobber research you have already done
            stub.write_text(
                f"# {p['name']}\n\n"
                f"- **URL:** {p['urls'][0]}\n"
                f"- **Account created:** [ ]\n- **Profile complete:** [ ]\n\n"
                f"## What the application form asks for\n\n"
                f"_Fill in the first time you apply, then never re-derive it._\n\n"
                f"## Campaigns applied to\n\n| Date | Brand | Status |\n|---|---|---|\n",
                encoding="utf-8",
            )
        print(f"Wrote {len(platforms)} stubs to platforms/notes/")

    print(f"Found {len(platforms)} platforms in \"{args.folder}\".")
    print(f"  {md_path.relative_to(REPO)}")
    print(f"  {csv_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
