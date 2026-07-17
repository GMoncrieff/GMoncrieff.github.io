#!/usr/bin/env python3
"""Strengthen the redirect stubs Quarto generates for `aliases:`.

Quarto emits a JavaScript-only redirect, which only works for clients that run
JS and which carries no canonical link. These stubs stand in for URLs the old
distill site published, so they need to survive contact with crawlers and
archivers that do not run JS, and they need to hand ranking to the new URL.

This rewrites each stub to use, in order:
  1. <link rel="canonical">          so search engines consolidate on the new URL
  2. <meta http-equiv="refresh">     a soft 301 that needs no JS
  3. Quarto's original JS            preserves #anchor handling
  4. a visible link                  last resort for anything else

Run by Quarto via `project: post-render:` in _quarto.yml, so it applies on every
build, locally and in CI. Idempotent: an already-enhanced stub is left alone.
"""
import json
import os
import re
import sys
from pathlib import Path

SITE = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
BASE = "https://gmoncrieff.github.io/"

REDIRECT_MAP = re.compile(r'var redirects = (\{.*?\});')
MARKER = "<!-- enhanced-redirect -->"

TEMPLATE = """<!DOCTYPE html>
{marker}
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting to {canonical}</title>
<link rel="canonical" href="{canonical}">
<meta http-equiv="refresh" content="0; url={target}">
<script type="text/javascript">
  var redirects = {redirects};
  var hash = window.location.hash.startsWith('#') ? window.location.hash.slice(1) : window.location.hash;
  window.location.replace(redirects[hash] || redirects[""] || "/");
</script>
</head>
<body>
<p>This page has moved to <a href="{target}">{canonical}</a>.</p>
</body>
</html>
"""


def pretty(path: Path) -> Path:
    """Drop a trailing index.html so URLs stay directory-shaped."""
    return path.parent if path.name == "index.html" else path


def main() -> int:
    site = SITE.resolve()
    if not site.is_dir():
        print(f"enhance_redirects: no output dir at {site}", file=sys.stderr)
        return 1

    enhanced = skipped = 0
    for html in sorted(site.rglob("*.html")):
        text = html.read_text()
        if MARKER in text:
            skipped += 1
            continue
        if "<title>Redirect</title>" not in text:
            continue
        match = REDIRECT_MAP.search(text)
        if not match:
            print(f"enhance_redirects: stub without redirect map: {html}", file=sys.stderr)
            return 1

        raw = json.loads(match.group(1))
        rewritten = {}
        for frag, dest in raw.items():
            resolved = pretty((html.parent / dest).resolve())
            rel = os.path.relpath(resolved, html.parent)
            rewritten[frag] = "./" if rel == "." else rel + "/"

        default = pretty((html.parent / raw[""]).resolve()).relative_to(site)
        # Path(".") means the target is the site root, which is BASE itself.
        canonical = BASE if default == Path(".") else f"{BASE}{default}/"

        html.write_text(TEMPLATE.format(
            marker=MARKER,
            canonical=canonical,
            target=rewritten[""],
            redirects=json.dumps(rewritten),
        ))
        print(f"  redirect {str(html.relative_to(site)):48s} -> {canonical}")
        enhanced += 1

    print(f"enhance_redirects: {enhanced} enhanced, {skipped} already done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
