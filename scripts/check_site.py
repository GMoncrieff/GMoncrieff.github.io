#!/usr/bin/env python3
"""Fail if any local href/src in the built _site/ does not resolve to a file."""
import os
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "_site"))


class LinkFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for attr in ("href", "src"):
            if d.get(attr):
                self.links.append(d[attr])


def is_local(url):
    p = urlparse(url)
    return (not p.scheme and not p.netloc
            and not url.startswith("#") and not url.startswith("mailto:"))


def main():
    if not os.path.isdir(SITE):
        print(f"No _site/ at {SITE}; run `quarto render` first.")
        sys.exit(1)
    problems = []
    for root, _, files in os.walk(SITE):
        for f in files:
            if not f.endswith(".html"):
                continue
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                p = LinkFinder()
                p.feed(fh.read())
            for link in p.links:
                if not is_local(link):
                    continue
                target = link.split("#")[0].split("?")[0]
                if not target:
                    continue
                if target.startswith("/"):
                    resolved = os.path.join(SITE, target.lstrip("/"))
                else:
                    resolved = os.path.normpath(os.path.join(root, unquote(target)))
                if os.path.isdir(resolved):
                    resolved = os.path.join(resolved, "index.html")
                if not os.path.exists(resolved):
                    problems.append(f"{os.path.relpath(path, SITE)} -> {link}")
    if problems:
        print("BROKEN LOCAL LINKS/ASSETS:")
        for pr in sorted(set(problems)):
            print("  " + pr)
        sys.exit(1)
    print("OK: all local links and assets resolve.")


if __name__ == "__main__":
    main()
