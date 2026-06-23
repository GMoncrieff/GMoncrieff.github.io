# Quarto Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hand-written static HTML site in `site/` with a Quarto website that renders to a visually faithful copy of the current site, while enabling markdown authoring, code execution, and Quarto-managed content.

**Architecture:** A Quarto `website` project at the repo root. The current `assets/style.css` is ported into a Quarto SCSS theme so the look carries over unchanged. Nav and footer are defined once in `_quarto.yml`. Bespoke layouts (hero, cards, project cards, contact fields) are kept as raw HTML inside `.qmd` files. The blog is a Quarto **listing** with a custom EJS template that emits the existing `.row` markup, plus native category filtering. Old posts are frozen: their text and pre-rendered images are kept and their code is shown as static (non-executed) fenced blocks.

**Tech Stack:** Quarto 1.5.57, SCSS (Bootstrap-based theme layers), EJS listing templates, Python 3.11 (verification script only). No runtime JavaScript we author (Quarto's listing JS handles filtering).

## Global Constraints

- **Visual fidelity:** match the current design exactly — fonts Space Grotesk (display) / IBM Plex Sans (body) / IBM Plex Mono (mono); accent `oklch(0.52 0.13 152)` botanical green; hexagon brand mark; **light mode only** (no dark toggle, no search).
- **Ported post content is verbatim.** Do not reword, summarize, or "improve" any existing post prose. Convert HTML to markdown faithfully.
- **Any new copy I author** (not ported content): plain language, **no em dashes**, no marketing-speak, no LLM-isms.
- **Tags come only from this fixed set:** R, Python, AI/ML, LLMs, Remote Sensing, Conservation, Teaching, Savannas, Fynbos, Forecasting, Ecosystem Condition, Ultra running, Biodiversity monitoring.
- **Identity (must stay exact):** email `glennmoncrieff@gmail.com`; socials GitHub `https://github.com/GMoncrieff`, Google Scholar `https://scholar.google.co.za/citations?user=_FFdaCUAAAAJ`, LinkedIn `https://www.linkedin.com/in/glenn-moncrieff-a50879227`; nav brand subtitle "biodiversity data science"; footer "© 2026 Glenn Moncrieff" and "Cape Town · South Africa".
- **Per-task verification bar:** `quarto render` completes with no errors; the page loads in a browser with a clean console; layout matches the corresponding old page. The old site stays in `site/` as the reference for comparison until Task 14.
- **Commit cadence:** one commit per task (per post inside the post tasks). Work happens on the `quarto-migration` branch.

---

## File Structure

Created by this plan (all paths relative to repo root):

```
_quarto.yml                 # site config: project, navbar, footer, theme, execute
.gitignore                  # ignore _site/ and .quarto/
theme/custom.scss           # ported style.css + framework overrides
theme/fonts.html            # Google Fonts <link> tags (include-in-header)
theme/listing.ejs           # blog listing template -> .row markup (with tags)
theme/listing-home.ejs      # home "Latest Writing" template -> .row markup (no tags)
assets/logo.svg             # hexagon brand mark (navbar logo + favicon)
assets/avatar.png           # copied from site/assets/avatar.png
scripts/check_site.py       # link/asset verification (the automated test)
index.qmd                   # home
papers.qmd                  # publications grouped by year
projects.qmd                # 4 project cards
contact.qmd                 # contact fields + "for students"
blog.qmd                    # Quarto listing of posts/
posts/_metadata.yml         # shared post defaults
posts/<slug>/index.qmd      # one folder per post (11 total) + that post's images
```

The 11 post slugs: `fynbos-id`, `advi-vs-mcmc`, `scheduled-earth-engine`, `planet-labs-r`, `reproducible-r-1`, `0-to-100km`, `ml-vegetation-monitoring`, `emma-un-challenge`, `data-carpentry-ethiopia`, `thicket-change`, `wiped-off-the-map`. Source HTML is at `site/posts/<slug>.html`; source images at `site/assets/posts/<slug>/` (note `planet-labs-r` has no image folder).

---

## Task 1: Site shell (project config, theme, assets)

Deliverable: `quarto render` builds a `_site/` whose background, fonts, navbar, and footer match the current design, using a minimal placeholder home page.

**Files:**
- Create: `_quarto.yml`, `.gitignore`, `theme/custom.scss`, `theme/fonts.html`, `assets/logo.svg`, `assets/avatar.png`, `index.qmd` (placeholder)
- Reference (read, do not modify): `site/assets/style.css`, `site/index.html`

**Interfaces:**
- Produces: the theme classes from `style.css` (`.wrap`, `.section`, `.hero`, `.card`, `.row`, `.chip`, `.prose`, `.page-head`, `.field`, etc.) available site-wide; CSS custom properties in `:root` (`--bg`, `--accent`, `--text`, ...); navbar/footer chrome. All later tasks rely on these classes.

- [ ] **Step 1: Create `.gitignore`**

```
/_site/
/.quarto/
.DS_Store
```

(Do not ignore `_freeze/` — Quarto's freeze cache should be committed so renders are reproducible.)

- [ ] **Step 2: Copy the avatar and extract the logo**

```bash
mkdir -p assets
cp site/assets/avatar.png assets/avatar.png
```

Create `assets/logo.svg` (the navbar hexagon mark, with concrete colors since a standalone file cannot use `currentColor`/CSS vars; `#15181b` = `--text`, `#3f8f5f` ≈ the green accent):

```svg
<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polygon points="90,50 70,84.64 30,84.64 10,50 30,15.36 70,15.36" stroke="#15181b" stroke-width="3" stroke-linejoin="round" opacity="0.85"/>
  <line x1="50" y1="33" x2="37" y2="61" stroke="#15181b" stroke-width="2.4" opacity="0.5"/>
  <line x1="50" y1="33" x2="63" y2="61" stroke="#15181b" stroke-width="2.4" opacity="0.5"/>
  <line x1="37" y1="61" x2="63" y2="61" stroke="#15181b" stroke-width="2.4" opacity="0.5"/>
  <circle cx="50" cy="33" r="6" fill="#3f8f5f"/>
  <circle cx="37" cy="61" r="6" fill="#15181b"/>
  <circle cx="63" cy="61" r="6" fill="#15181b"/>
</svg>
```

- [ ] **Step 3: Create `theme/fonts.html`** (robust web-font loading via header include)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
```

- [ ] **Step 4: Create `theme/custom.scss`**

Structure: a `defaults` layer that aligns Bootstrap's base variables to our palette, then a `rules` layer that is the **verbatim contents of `site/assets/style.css`** (including its `:root {}` block and the `@import url(...)` line removed, since fonts now load via `fonts.html`), followed by framework-override rules.

Write the file as:

```scss
/*-- scss:defaults --*/
$font-family-sans-serif: 'IBM Plex Sans', system-ui, sans-serif;
$font-family-monospace:  'IBM Plex Mono', ui-monospace, monospace;
$headings-font-family:   'Space Grotesk', system-ui, sans-serif;
$body-bg:    #f6f6f3;
$body-color: #15181b;
$primary:    #3f8f5f;
$link-color: inherit;
$link-decoration: none;
// let our own .wrap control width; widen Bootstrap container so it never clips
$max-width: 1120px;

/*-- scss:rules --*/

/* ===== ported verbatim from site/assets/style.css =====
   (paste the ENTIRE file here, EXCEPT delete its first line, the
   `@import url('https://fonts.googleapis.com/...')` — fonts load via fonts.html.
   Keep the :root {} variable block and every rule unchanged.) */

/* ===== Quarto framework overrides ===== */

/* let our .wrap / .section classes own the layout */
#quarto-content > *, main.content { padding-left: 0; padding-right: 0; }
main.content { margin-top: 0; }

/* hide Quarto's auto title block — every page supplies its own header */
header#title-block-header { display: none; }

/* navbar -> reproduce the current sticky translucent .nav */
.navbar {
  position: sticky; top: 0; z-index: 50;
  background: rgba(246, 246, 243, 0.72);
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--hairline);
  padding: 14px 0;
}
.navbar > .container-fluid, .navbar > .container { max-width: var(--maxw); padding-inline: var(--gutter); }
.navbar-brand { display: flex; align-items: center; gap: 12px; font-family: var(--font-display); font-weight: 600; font-size: 0.98rem; letter-spacing: -0.01em; color: var(--text); }
.navbar-brand img { width: 30px; height: 30px; }
/* two-tone brand subtitle, added cosmetically after the title text */
.navbar-brand::after { content: "· biodiversity data science"; color: var(--text-3); font-weight: 500; }
.navbar-nav { gap: 30px; }
.navbar-nav .nav-link { font-family: var(--font-body); font-size: 0.93rem; color: var(--text-2); padding-block: 4px; position: relative; }
.navbar-nav .nav-link:hover { color: var(--text); }
.navbar-nav .nav-link.active { color: var(--text); }
.navbar-nav .nav-link.active::after { content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 1px; background: var(--accent); }

/* footer -> reproduce .footer */
.nav-footer { border-top: 1px solid var(--hairline); background: transparent; }
.nav-footer .nav-footer-left, .nav-footer .nav-footer-center, .nav-footer .nav-footer-right { font-family: var(--font-mono); font-size: 0.76rem; color: var(--text-faint); }
.nav-footer a { color: var(--text-3); font-family: var(--font-body); font-size: 0.88rem; }
.nav-footer a:hover { color: var(--text); }

/* code highlighting -> nudge pandoc tokens toward the old palette */
pre.sourceCode, .sourceCode pre { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }
code span.co { color: var(--text-faint); font-style: italic; }   /* comments */
code span.st, code span.ss { color: var(--accent); }            /* strings */
code span.kw, code span.cf { color: var(--text); font-weight: 600; } /* keywords */
code span.dv, code span.fl, code span.bn { color: var(--text); } /* numbers */
```

- [ ] **Step 5: Create `_quarto.yml`**

```yaml
project:
  type: website
  output-dir: _site

website:
  title: "Glenn Moncrieff"
  favicon: assets/logo.svg
  navbar:
    logo: assets/logo.svg
    title: "Glenn Moncrieff"
    right:
      - text: "Home"
        href: index.qmd
      - text: "Papers"
        href: papers.qmd
      - text: "Blog"
        href: blog.qmd
      - text: "Projects"
        href: projects.qmd
      - text: "Contact"
        href: contact.qmd
  page-footer:
    left: "© 2026 Glenn Moncrieff"
    center:
      - text: "Papers"
        href: papers.qmd
      - text: "Blog"
        href: blog.qmd
      - text: "Projects"
        href: projects.qmd
      - text: "Contact"
        href: contact.qmd
    right: "Cape Town · South Africa"

format:
  html:
    theme: theme/custom.scss
    include-in-header: theme/fonts.html
    page-layout: full
    toc: false
    anchor-sections: false
    highlight-style: github
    grid:
      body-width: 1120px

execute:
  freeze: auto
```

- [ ] **Step 6: Create placeholder `index.qmd`**

```markdown
---
title: "Glenn Moncrieff"
pagetitle: "Glenn Moncrieff — Conservation Data Science"
---

<header class="hero wrap"><h1>Glenn Moncrieff</h1></header>
```

- [ ] **Step 7: Render and verify**

Run: `quarto render`
Expected: completes with no error; `_site/index.html`, `_site/site_libs/` exist.

Then preview and eyeball the chrome:

Run: `quarto preview --no-browser --port 4321` (stop it after checking)
Load `http://localhost:4321` in a browser. Confirm: cream `#f6f6f3` background, Space Grotesk heading, sticky translucent navbar showing the hexagon logo + "Glenn Moncrieff · biodiversity data science" + the five right-aligned links, footer with the three regions, console clean. Compare the navbar/footer against `site/index.html` opened side by side.

- [ ] **Step 8: Commit**

```bash
git add _quarto.yml .gitignore theme assets index.qmd
git commit -m "feat: scaffold Quarto site shell with ported theme and chrome"
```

---

## Task 2: Link & asset verification script

Deliverable: a script that walks the built `_site/` and fails if any local `href`/`src` does not resolve. This is the automated test reused by every later task (broken relative paths are the top migration risk).

**Files:**
- Create: `scripts/check_site.py`

**Interfaces:**
- Produces: CLI `python3 scripts/check_site.py` — exit 0 with "OK" when all local links/assets resolve, exit 1 listing broken ones.

- [ ] **Step 1: Write the script**

```python
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
```

- [ ] **Step 2: Run it against the current build**

Run: `quarto render && python3 scripts/check_site.py`
Expected: `OK: all local links and assets resolve.` (exit 0)

- [ ] **Step 3: Commit**

```bash
git add scripts/check_site.py
git commit -m "test: add local link/asset checker for the built site"
```

---

## Task 3: Home page (static sections)

Deliverable: the home page hero, About block, "What I Work On" cards, and "Selected Papers" rows render identically to the top of `site/index.html`. (The "Latest Writing" listing is added in Task 12.)

**Files:**
- Modify: `index.qmd`
- Reference: `site/index.html` (lines 36-147 are the body content to port)

**Interfaces:**
- Consumes: theme classes from Task 1.

- [ ] **Step 1: Replace `index.qmd` body**

Keep the front matter, then paste the **body content of `site/index.html`** from the `<header class="hero wrap">` block through the end of the "Selected Papers" `</section>` (source lines 36-147), **omitting** the nav, the "Latest Writing" section, the footer, and the trailing `<script>`. Asset paths already match (`assets/avatar.png`). The result:

```markdown
---
title: "Glenn Moncrieff"
pagetitle: "Glenn Moncrieff — Conservation Data Science"
---

<!-- HERO: paste lines 37-55 of site/index.html (the <header class="hero wrap"> ... </header>) -->

<!-- ABOUT: paste lines 58-79 (the <section class="section--tight wrap"> two-col block) -->

<!-- WHAT I WORK ON: paste lines 82-101 (the cards section) -->

<!-- SELECTED PAPERS: paste lines 113-147 (the Selected Papers section) -->
```

Paste the actual HTML from those line ranges (it is block-level HTML; pandoc passes it through unchanged).

- [ ] **Step 2: Render and verify**

Run: `quarto render index.qmd && python3 scripts/check_site.py`
Expected: render OK; checker OK.
Browser-check `_site/index.html` against `site/index.html`: hero hexagon + heading + tagline + three social pills; avatar + About text; three numbered cards; three Selected Papers rows linking to the right DOIs. Console clean.

- [ ] **Step 3: Commit**

```bash
git add index.qmd
git commit -m "feat: port home page hero, about, cards, selected papers"
```

---

## Task 4: Papers page

Deliverable: `papers.qmd` renders the 34 publications grouped by year, identical to `site/papers.html`.

**Files:**
- Create: `papers.qmd`
- Reference: `site/papers.html`

- [ ] **Step 1: Create `papers.qmd`**

Front matter, then paste the **body of `site/papers.html`** from `<header class="page-head wrap">` through the last year `</section>` (everything between `</nav>` and `<footer>`):

```markdown
---
title: "Papers"
pagetitle: "Papers — Glenn Moncrieff"
---

<!-- paste site/papers.html body: the <header class="page-head wrap"> block
     and every <section class="section--tight wrap"> year group, verbatim -->
```

Do not invent DOIs; keep only the links present in the source (4 papers intentionally have no DOI link).

- [ ] **Step 2: Render and verify**

Run: `quarto render papers.qmd && python3 scripts/check_site.py`
Expected: render OK; checker OK.
Browser-check: year headings with correct per-year counts; 34 entries total; italic venues; "G. Moncrieff" bolded in author lists; external links open. Compare against `site/papers.html`.

- [ ] **Step 3: Commit**

```bash
git add papers.qmd
git commit -m "feat: port papers page (34 publications by year)"
```

---

## Task 5: Projects page

Deliverable: `projects.qmd` renders the 4 project cards identical to `site/projects.html`.

**Files:**
- Create: `projects.qmd`
- Reference: `site/projects.html`

- [ ] **Step 1: Create `projects.qmd`**

```markdown
---
title: "Projects"
pagetitle: "Projects — Glenn Moncrieff"
---

<!-- paste site/projects.html body: the <header class="page-head wrap"> block
     and the <section class="section--tight wrap"> with the four <div class="res">
     cards, verbatim (between </nav> and <footer>) -->
```

- [ ] **Step 2: Render and verify**

Run: `quarto render projects.qmd && python3 scripts/check_site.py`
Expected: render OK; checker OK.
Browser-check: four cards (Human modification forecasting, SciArgus, Remote sensing of fynbos biodiversity, Global Renosterveld Watch) with their SVG icons, tag chips, and link rows. Console clean.

- [ ] **Step 3: Commit**

```bash
git add projects.qmd
git commit -m "feat: port projects page (4 cards)"
```

---

## Task 6: Contact page

Deliverable: `contact.qmd` renders the contact field list and "for students" block identical to `site/contact.html`.

**Files:**
- Create: `contact.qmd`
- Reference: `site/contact.html`

- [ ] **Step 1: Create `contact.qmd`**

```markdown
---
title: "Contact"
pagetitle: "Contact — Glenn Moncrieff"
---

<!-- paste site/contact.html body: the <header class="page-head wrap"> block and
     the <section class="section wrap"> contact-grid, verbatim (between </nav> and <footer>).
     Asset path assets/avatar.png already matches. -->
```

- [ ] **Step 2: Render and verify**

Run: `quarto render contact.qmd && python3 scripts/check_site.py`
Expected: render OK; checker OK.
Browser-check: six fields (Email, Affiliation, Based in, GitHub, Scholar, LinkedIn), the avatar, the "for students" paragraph, and the "Write me an email" button (mailto). Console clean.

- [ ] **Step 3: Commit**

```bash
git add contact.qmd
git commit -m "feat: port contact page"
```

---

## Task 7: Post infrastructure + exemplar post (fynbos-id)

Deliverable: the post-conversion pattern is established and the `fynbos-id` post (prose + code + figures) renders faithfully. Establishes the recipe reused in Tasks 8-9.

**Files:**
- Create: `posts/_metadata.yml`, `posts/fynbos-id/index.qmd`, and copy `posts/fynbos-id/<images>`
- Reference: `site/posts/fynbos-id.html`, `site/assets/posts/fynbos-id/`

**Interfaces:**
- Produces: front-matter contract every post uses — `title`, `date` (YYYY-MM-DD), `author`, `categories` (from the fixed tag set), `description`, optional `image`. Consumed by the listings in Tasks 11-12.

- [ ] **Step 1: Create `posts/_metadata.yml`** (shared defaults for all posts)

```yaml
author: "Glenn Moncrieff"
title-block-style: none
```

- [ ] **Step 2: Copy the post's images**

```bash
mkdir -p posts/fynbos-id
cp site/assets/posts/fynbos-id/* posts/fynbos-id/
```

- [ ] **Step 3: Write `posts/fynbos-id/index.qmd` using the conversion recipe**

The recipe (apply to every post):
1. Front matter: `title` = the **blog-row title** from `site/blog.html` (so the listing matches today), `date`, `author`, `categories`, `description` = the blog-row summary, and `image:` only if the source post has a `<div class="article__cover">` (fynbos-id does not).
2. Body wrapped in `::: {.article}` then a `::: {.article__head}` block (raw-HTML meta line copied verbatim from the source `.article__meta`, then the source's own `<h1>` as a markdown `#` heading, then the lead `<p class="hero__tag">` line), then `::: {.prose}` containing the converted body.
3. Convert `<p>` to markdown paragraphs (verbatim text). Convert `<a href>` to `[text](url)`. Convert `<figure><img src="../assets/posts/<slug>/x"><figcaption>cap</figcaption></figure>` to `![cap](x)` (image now sits beside the .qmd, so drop the `../assets/posts/<slug>/` prefix). Convert `<pre><code class="language-r">` to a ```` ```r ```` fence (and `language-python`->`python`, `language-bash`->`bash`, `language-json`->`json`); **unescape** `&lt;`->`<`, `&gt;`->`>`, `&amp;`->`&` inside code. Convert inline `<code>` to backticks and `<strong>`/`<em>` to `**`/`*`.
4. Top link: `[← Back to blog](../../blog.qmd){.text-link}` above the head.

The file shape:

```markdown
---
title: "Automated fynbos identification using iNaturalist and deep learning"
date: 2018-03-10
categories: [Python, R, AI/ML, Fynbos]
description: "Identifying Proteas and Restios from photos with a convolutional neural network."
---

::: {.article}

[← Back to blog](../../blog.qmd){.text-link}

::: {.article__head}
<div class="article__meta"><span>2018 · 03 · 10</span><span>·</span><span>7 min read</span><span>·</span><span style="color:var(--accent);">AI/ML</span></div>

# Automated fynbos identification using iNaturalist and deep learning

<p class="hero__tag" style="text-align:left; margin:0; max-width:62ch;">Identifying Proteas and Restios from photos using TensorFlow and transfer learning.</p>
:::

::: {.prose}

A lack of knowledge of neural networks... <!-- continue converting site/posts/fynbos-id.html prose verbatim -->

## Step 1: Getting the Data

... [iNaturalist](https://www.inaturalist.org/) ...

![Elegia filacea. photo: Ronald Flipphi CC BY-NC](Elegia_filacea_ronald_flipphi.jpeg)

```r
#load rinit library
library(rinat)
setwd("~/science/image_net")
#rough bounding box for the fynbos biome
bounds <- c(-32.86,20,-34.3,24)
Proteas <- get_inat_obs(taxon_name = "Protea",bounds=bounds)
Restios <- get_inat_obs(taxon_name = "Restionaceae",bounds=bounds)
# ... rest of the block, entities unescaped ...
```

<!-- ...continue to the end of the post... -->

:::

:::
```

- [ ] **Step 4: Render and verify**

Run: `quarto render posts/fynbos-id/index.qmd && python3 scripts/check_site.py`
Expected: render OK; checker OK (all five images resolve).
Browser-check `_site/posts/fynbos-id/index.html` against `site/posts/fynbos-id.html`: the meta line (date · 7 min read · AI/ML in green), the H1 and lead, prose at `.prose` width (~720px), the two R/Python code blocks highlighted, all figures with captions, the "Back to blog" link. Confirm the code blocks are **rendered as static** (no execution) and the console is clean.

- [ ] **Step 5: Commit**

```bash
git add posts/_metadata.yml posts/fynbos-id
git commit -m "feat: add post conversion pattern and fynbos-id post"
```

---

## Task 8: Remaining code posts

Deliverable: the four other code-bearing posts render faithfully. Apply the Task 7 recipe to each. One step + one commit per post.

**Files (per post):**
- Create: `posts/<slug>/index.qmd`; copy `posts/<slug>/<images>` from `site/assets/posts/<slug>/` (skip the copy for `planet-labs-r`, which has none)
- Reference: `site/posts/<slug>.html`

Conversion recipe (same as Task 7): wrap in `::: {.article}` > `::: {.article__head}` (verbatim meta line + source `<h1>` + lead) > `::: {.prose}` (verbatim prose; links to `[]()`; figures to `![cap](file)` with the `../assets/...` prefix dropped; `<pre><code class="language-X">` to ```` ```X ```` fences with entities unescaped). `title` = blog-row title; `description` = blog-row summary.

- [ ] **Step 1: `advi-vs-mcmc`** — front matter:

```yaml
title: "ADVI vs MCMC"
date: 2020-08-11
categories: [R, Remote Sensing, Fynbos, Forecasting]
description: "Two ways to fit a Bayesian model of post-fire vegetation recovery, and when each is worth it."
```
`cp site/assets/posts/advi-vs-mcmc/* posts/advi-vs-mcmc/`. Convert body. Render, run checker, browser-check, then `git add posts/advi-vs-mcmc && git commit -m "feat: add advi-vs-mcmc post"`.

- [ ] **Step 2: `scheduled-earth-engine`** — front matter:

```yaml
title: "Automate your Google Earth Engine analyses"
date: 2021-11-27
categories: [Python, Remote Sensing]
description: "How to schedule Earth Engine scripts so your analyses run on their own."
```
`cp site/assets/posts/scheduled-earth-engine/* posts/scheduled-earth-engine/`. Convert, render, checker, browser-check, commit `"feat: add scheduled-earth-engine post"`.

- [ ] **Step 3: `planet-labs-r`** — front matter:

```yaml
title: "Accessing the Planet Labs data API from R"
date: 2018-02-22
categories: [R, Remote Sensing]
description: "Querying and downloading Planet satellite imagery directly from R."
```
No images to copy. Convert, render, checker, browser-check, commit `"feat: add planet-labs-r post"`.

- [ ] **Step 4: `reproducible-r-1`** — front matter:

```yaml
title: "Reproducible R, part 1"
date: 2020-04-16
categories: [R, Teaching]
description: "Tools for making an R analysis reproducible by a stranger: renv, holepunch, and Binder."
```
`cp site/assets/posts/reproducible-r-1/* posts/reproducible-r-1/`. Convert, render, checker, browser-check, commit `"feat: add reproducible-r-1 post"`.

---

## Task 9: Prose and special posts

Deliverable: the remaining six posts render faithfully, including the two with embedded media. Same recipe; one step + one commit per post.

**Files (per post):** Create `posts/<slug>/index.qmd`; copy images from `site/assets/posts/<slug>/`. Reference `site/posts/<slug>.html`.

- [ ] **Step 1: `0-to-100km`** — front matter:

```yaml
title: "0 to 100km"
date: 2026-05-29
categories: [Ultra running]
description: "Two years of trail running, two injuries, and getting to the start line of my first 100km."
```
`cp site/assets/posts/0-to-100km/* posts/0-to-100km/`. Convert, render, checker, browser-check, commit `"feat: add 0-to-100km post"`.

- [ ] **Step 2: `ml-vegetation-monitoring`** — front matter:

```yaml
title: "Machine learning for vegetation monitoring"
date: 2022-06-01
categories: [AI/ML, Remote Sensing, Biodiversity monitoring, Teaching]
description: "A seminar on using machine learning and satellite data to monitor vegetation."
```
`cp site/assets/posts/ml-vegetation-monitoring/* posts/ml-vegetation-monitoring/`. The source embeds a talk/video — preserve whatever embed/iframe or link the source uses, verbatim. Convert, render, checker, browser-check, commit `"feat: add ml-vegetation-monitoring post"`.

- [ ] **Step 3: `emma-un-challenge`** — front matter:

```yaml
title: "EMMA wins the UN Data for Climate Action challenge"
date: 2017-11-15
categories: [Remote Sensing, Conservation, Biodiversity monitoring]
description: "A vegetation monitoring tool for the Cape that won a UN open-data prize."
```
`cp site/assets/posts/emma-un-challenge/* posts/emma-un-challenge/`. Convert, render, checker, browser-check, commit `"feat: add emma-un-challenge post"`.

- [ ] **Step 4: `data-carpentry-ethiopia`** — front matter:

```yaml
title: "Data Carpentry in Ethiopia"
date: 2017-10-02
categories: [Teaching]
description: "Teaching reproducible data skills to researchers at a workshop in Ethiopia."
```
`cp site/assets/posts/data-carpentry-ethiopia/* posts/data-carpentry-ethiopia/`. Convert, render, checker, browser-check, commit `"feat: add data-carpentry-ethiopia post"`.

- [ ] **Step 5: `thicket-change`** (special — Juxtapose iframe) — front matter:

```yaml
title: "Real-time detection of land cover change"
date: 2018-10-31
categories: [Remote Sensing, Conservation, Biodiversity monitoring]
description: "Detecting vegetation clearing within days using Sentinel-2 and Planet time series."
```
`cp site/assets/posts/thicket-change/* posts/thicket-change/`. Preserve the Knightlab Juxtapose `<iframe>` verbatim (paste as raw HTML inside `.prose`). Convert the rest. Render, checker, browser-check (the iframe loads; the benign cross-origin console notice only appears under `file://`, not under the preview server), commit `"feat: add thicket-change post"`.

- [ ] **Step 6: `wiped-off-the-map`** (special — static map + link) — front matter:

```yaml
title: "Wiped off the map"
date: 2019-09-24
categories: [Remote Sensing]
description: "Historical aerial photographs document the communities that apartheid tried to erase."
```
`cp site/assets/posts/wiped-off-the-map/* posts/wiped-off-the-map/`. Keep the existing static map image plus its "view the interactive version" link to `gmoncrieff.github.io/posts/wiped-off-the-map/`, exactly as the source does (the Leaflet maps were not portable and are already a static image + link). Convert the rest. Render, checker, browser-check, commit `"feat: add wiped-off-the-map post"`.

---

## Task 10: (reserved — no work)

All 11 posts are complete after Task 9. Proceed to Task 11.

---

## Task 11: Blog listing page

Deliverable: `blog.qmd` renders a Quarto listing that reproduces the current blog index — `.row` entries newest-first with date, title, summary, tag chips, and a working tag filter — replacing `site/blog.html` and its JS.

**Files:**
- Create: `blog.qmd`, `theme/listing.ejs`
- Modify: `theme/custom.scss` (add listing-filter CSS)
- Reference: `site/blog.html`

**Interfaces:**
- Consumes: post front matter (`title`, `date`, `categories`, `description`) from Tasks 7-9.
- Produces: a styled native listing + category filter.

- [ ] **Step 1: Create `theme/listing.ejs`** (emits the `.row` markup; `metadataAttrs(item)` carries the data Quarto's listing JS needs for category filtering)

```ejs
<div class="rows" id="postRows">
<% for (const item of items) { %>
  <a class="row" href="<%- item.path %>" <%= metadataAttrs(item) %>>
    <span class="row__date"><%= item.date %></span>
    <div class="row__main">
      <h3><%= item.title %></h3>
      <p><%= item.description %></p>
      <% if (item.categories && item.categories.length) { %>
      <div class="row__tags">
        <% for (const c of item.categories) { %><span class="chip"><%= c %></span><% } %>
      </div>
      <% } %>
    </div>
    <span class="row__arrow">&rarr;</span>
  </a>
<% } %>
</div>
```

- [ ] **Step 2: Create `blog.qmd`**

```markdown
---
pagetitle: "Blog — Glenn Moncrieff"
listing:
  id: posts
  contents: posts
  sort: "date desc"
  type: default
  template: theme/listing.ejs
  categories: true
  sort-ui: false
  filter-ui: false
  date-format: "YYYY · MM · DD"
  fields: [date, title, description, categories]
---

<header class="page-head wrap">
  <span class="mono">// Notes &amp; write-ups</span>
  <h1>Blog</h1>
  <p>Tutorials, project write-ups, and notes on remote sensing, machine learning, and monitoring vegetation. Most of these were written between 2017 and 2022.</p>
</header>

<section class="section--tight wrap">

::: {#posts}
:::

</section>
```

- [ ] **Step 3: Add listing-filter CSS to `theme/custom.scss`** (map Quarto's category markup to the `.filter` chip bar; reuse the existing `.row`/`.chip` rules already ported)

```scss
/* blog listing category filter -> match the .filter chip bar */
.quarto-listing-category { display: flex; flex-wrap: wrap; gap: 9px; align-items: center; margin-bottom: 8px; }
.quarto-listing-category .category {
  font-family: var(--font-mono); font-size: 0.74rem; letter-spacing: 0.04em;
  color: var(--text-2); border: 1px solid var(--border); border-radius: 999px;
  padding: 7px 14px; cursor: pointer; transition: color .18s, border-color .18s, background .18s;
}
.quarto-listing-category .category:hover { color: var(--text); border-color: var(--border-strong); }
.quarto-listing-category .category.active { color: var(--bg); background: var(--accent); border-color: var(--accent); }
.quarto-listing-category .quarto-category-count, .quarto-listing-category .category .quarto-category-count { color: var(--text-faint); margin-left: 5px; }
```

- [ ] **Step 4: Render and verify**

Run: `quarto render && python3 scripts/check_site.py`
Expected: render OK; checker OK.
Browser-check `_site/blog.html` against `site/blog.html`: 11 rows newest-first (0-to-100km at top), each with date / title / summary / chips / arrow; rows link to the posts; the category filter sits above the list as chips. Click a category (e.g. "Fynbos") and confirm the list filters; click it again / "All" to clear. Console clean.
If the filter does not respond, confirm the helper name in Quarto's bundled default templates (`quarto/share/projects/website/listing/*.ejs`) and match the attribute helper used there.

- [ ] **Step 5: Commit**

```bash
git add blog.qmd theme/listing.ejs theme/custom.scss
git commit -m "feat: add Quarto blog listing with native tag filter"
```

---

## Task 12: Home "Latest Writing" listing

Deliverable: the home page shows the 3 most recent posts as `.row` entries (no chips), matching the current "Latest Writing" block (behavior change accepted in the spec: 3 most recent, dropping the 2-year cutoff).

**Files:**
- Modify: `index.qmd`
- Create: `theme/listing-home.ejs`
- Reference: `site/index.html` (lines 104-110 for the section header)

- [ ] **Step 1: Create `theme/listing-home.ejs`** (same as `listing.ejs` but without the `.row__tags` block)

```ejs
<div class="rows">
<% for (const item of items) { %>
  <a class="row" href="<%- item.path %>" <%= metadataAttrs(item) %>>
    <span class="row__date"><%= item.date %></span>
    <div class="row__main">
      <h3><%= item.title %></h3>
      <p><%= item.description %></p>
    </div>
    <span class="row__arrow">&rarr;</span>
  </a>
<% } %>
</div>
```

- [ ] **Step 2: Add the listing to `index.qmd`**

Add to the front matter:

```yaml
listing:
  - id: latest
    contents: posts
    sort: "date desc"
    type: default
    template: theme/listing-home.ejs
    max-items: 3
    categories: false
    sort-ui: false
    filter-ui: false
    date-format: "YYYY · MM · DD"
    fields: [date, title, description]
```

And insert this section between the "What I Work On" and "Selected Papers" sections (mirrors `site/index.html` placement):

```markdown
<section class="section--tight wrap">
  <div class="sec-head">
    <h2>Latest Writing</h2>
    <a class="mono" href="blog.html" style="color:var(--text-3);">All posts &rarr;</a>
  </div>

::: {#latest}
:::

</section>
```

- [ ] **Step 3: Render and verify**

Run: `quarto render && python3 scripts/check_site.py`
Expected: render OK; checker OK.
Browser-check `_site/index.html`: "Latest Writing" shows the 3 newest posts (0-to-100km, ml-vegetation-monitoring, scheduled-earth-engine) as rows without chips, each linking to its post; "All posts" links to the blog. Console clean.

- [ ] **Step 4: Commit**

```bash
git add index.qmd theme/listing-home.ejs
git commit -m "feat: add Latest Writing listing to home page"
```

---

## Task 13: Full-site verification and parity check

Deliverable: a clean render of the whole site with every page and a sample of posts confirmed against the old site; no broken links; clean consoles.

**Files:** none created; may make small fixes to any prior file.

- [ ] **Step 1: Clean render + checker**

Run: `rm -rf _site .quarto && quarto render && python3 scripts/check_site.py`
Expected: render completes with no errors/warnings about missing files; checker prints `OK`.

- [ ] **Step 2: Browser walk**

Serve: `quarto preview --no-browser --port 4321`
Visit each of `/`, `/papers.html`, `/blog.html`, `/projects.html`, `/contact.html`, and at least `fynbos-id`, `thicket-change`, `wiped-off-the-map`, `0-to-100km`. For each, confirm against the matching `site/...` page: layout, fonts, colors, images present, links work, console clean. Verify the blog filter and the navbar active-underline on each section.

- [ ] **Step 3: Fix any discrepancies**

For each mismatch, fix the responsible file (`theme/custom.scss` for styling, the page/post `.qmd` for content/paths), re-render, re-check. Commit fixes:

```bash
git add -A
git commit -m "fix: resolve parity issues found in full-site verification"
```

(If nothing needed fixing, skip the commit.)

---

## Task 14: Documentation and retire the old site

Deliverable: `updating.md` describes the Quarto workflow; the old static site is moved out of the way; final commit.

**Files:**
- Modify: `updating.md`
- Move: `site/` -> `background/old-static-site/`

- [ ] **Step 1: Rewrite `updating.md`** for the Quarto workflow. Cover: prerequisites (Quarto); `quarto preview` to develop and `quarto render` to build to `_site/`; adding a blog post (`posts/<slug>/index.qmd` with front matter from the fixed tag set, images beside it, code in ```` ```{r} ````/```` ```{python} ```` for live execution or plain ```` ```r ```` for static); editing nav/footer/theme in one place (`_quarto.yml`, `theme/custom.scss`); the fixed tag set; and that publishing is `quarto publish` (or pushing `_site/` to any static host). Plain language, no em dashes.

- [ ] **Step 2: Move the old site to the reference area** (now that parity is verified)

```bash
mkdir -p background
git mv site background/old-static-site
```

- [ ] **Step 3: Final render to confirm nothing referenced `site/`**

Run: `rm -rf _site .quarto && quarto render && python3 scripts/check_site.py`
Expected: render OK; checker OK.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs: rewrite updating.md for Quarto; archive old static site"
```

---

## Self-Review

**Spec coverage** (each spec section maps to a task):
- Project structure -> Task 1 (config/theme/assets), structure realized across all tasks.
- Theme (ported SCSS, defaults+rules, navbar overrides, light-only) -> Task 1.
- Nav & footer defined once -> Task 1 (`_quarto.yml`).
- Pages (raw-HTML faithful: index/papers/projects/contact) -> Tasks 3-6.
- Blog listing (native, custom template, categories) -> Task 11; home Latest Writing (3 most recent) -> Task 12.
- Posts frozen (markdown body, static code, existing figures; special cases) -> Tasks 7-9.
- Code execution capability (`execute: freeze: auto`, engine auto-detect) -> Task 1 config; documented in Task 14.
- Verification (render + browser + clean console) -> per-task bars + Task 2 checker + Task 13.
- Documentation / retire old site -> Task 14.
- Out of scope (deploy, dark mode, search, data-driven papers) -> not planned. Correct.

**Placeholder scan:** content-porting steps reference exact source files/line ranges to copy verbatim rather than re-pasting hundreds of lines; this is intentional (the source lives in the repo) and each gives exact paths, front matter, and conversion rules — not vague "port the content." New artifacts (YAML, SCSS, EJS, checker) are given in full. No TBD/TODO.

**Type/name consistency:** post front-matter fields (`title`/`date`/`categories`/`description`/`image`) are identical across Tasks 7-9 and consumed unchanged by the listings in Tasks 11-12. Listing ids (`posts`, `latest`) match their `::: {#id}` divs. Template paths (`theme/listing.ejs`, `theme/listing-home.ejs`) match `_quarto.yml`/front-matter references. `metadataAttrs(item)` used identically in both templates.

**One known verification point:** the EJS helper for filter attributes (`metadataAttrs`) and the exact category-filter classes are confirmed by a browser interaction step in Task 11, with a concrete fallback (consult Quarto's bundled listing templates) if names differ across the 1.5.x line.
