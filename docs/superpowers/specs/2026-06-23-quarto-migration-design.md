# Design: Port glenn_website to Quarto

**Date:** 2026-06-23
**Status:** Approved (design phase)

## Goal

Port the existing pure-HTML personal site (`site/`) to a **Quarto website** so the
site can be authored in markdown, execute code in posts, and be managed with
Quarto's content tooling. Keep the new site **as visually faithful as possible**
to the current one.

## Decisions (confirmed with user)

1. **Blog listing:** use Quarto's **native listing** (auto-generated from each
   post's front matter, with clickable category filters), styled to closely match
   the current tag-chip filter. Not a verbatim port of the custom filter JS.
2. **Old posts:** **freeze** them. Convert each to Quarto markdown keeping the
   current text, images, and code shown as **static (non-executed) blocks**.
   Rendered output looks identical to today. Live code execution is reserved for
   new posts going forward.

## Current site (what we are preserving)

- Pure static HTML in `site/`, no build step.
- Pages: `index`, `papers`, `blog`, `projects`, `contact`.
- 11 posts in `site/posts/<slug>.html`; per-post images in
  `site/assets/posts/<slug>/`.
- Bespoke design in one shared `site/assets/style.css`:
  - Fonts: Space Grotesk (display), IBM Plex Sans (body), IBM Plex Mono (mono).
  - Accent: oklch botanical green; full palette + spacing as CSS variables in
    `:root`.
  - Custom hexagon SVG brand mark (nav, hero, footer).
- Three pieces of JavaScript: the blog tag-chip filter, the home "Latest Writing"
  widget (3 most recent posts from the last 2 years), and highlight.js for code
  posts.
- Nav + footer hand-copied into every page.

## Toolchain (verified present)

Quarto 1.5.57, Python 3.11.6, R 4.3.1. Git repo; work proceeds on the
`quarto-migration` branch.

## Target structure

Quarto website project at the repo root. The old `site/` stays untouched as a
reference until the new build is verified, then it is retired. `background/`
(source material) stays as-is.

```
_quarto.yml          # site config: navbar, footer, theme, listing defaults
index.qmd            # home: hero + about + cards + latest-writing + selected papers
papers.qmd           # 34 publications grouped by year
projects.qmd         # 4 project cards
contact.qmd          # contact fields + "for students"
blog.qmd             # Quarto listing (replaces blog.html + its JS)
posts/
  _metadata.yml      # shared post defaults
  0-to-100km/index.qmd   + images
  fynbos-id/index.qmd    + images
  ...                # all 11 posts, one folder each
theme/
  custom.scss        # ported style.css (defaults + rules layers)
  listing.ejs        # custom template so listings render the .row markup
assets/
  avatar.png, logo.svg (hexagon), favicon
_site/               # build output (gitignored)
```

## Components

### Theme (`theme/custom.scss`)
- The `:root` CSS variables and all custom rules (`.nav`, `.hero`, `.card`,
  `.row`, `.prose`, etc.) move over **unchanged** into the SCSS `rules` layer.
- A small `defaults` layer maps Bootstrap base variables (body background, text
  color, font families, container width, `$primary` = the green) to the existing
  tokens, so Quarto-generated chrome (listing, navbar) inherits the palette.
- Targeted CSS over Quarto's navbar reproduces the sticky translucent bar,
  hairline border, and active-link underline.
- **Light mode only** (faithful to today). No dark toggle, no search.

### Nav & footer (`_quarto.yml`, defined once)
- Navbar: hexagon `logo.svg` + title "Glenn Moncrieff · biodiversity data
  science", right-aligned links Home / Papers / Blog / Projects / Contact.
- Page footer: © 2026 mark (left), page links (center), "Cape Town · South
  Africa" (right).
- This removes the copy-paste-into-every-file nav/footer maintenance problem.

### Pages (raw-HTML faithful)
- `index`, `papers`, `projects`, `contact` keep their exact current markup inside
  `.qmd` files (Quarto passes HTML through).
- Papers stays as the hand-grouped-by-year list (low-risk faithful port). A
  data-driven version from a `.bib` is possible later but out of scope now.

### Blog listing (`blog.qmd` + `theme/listing.ejs`)
- A `listing` over `posts/`, using a custom EJS template that emits the existing
  `.row / .row__date / .row__main / .chip / .row__arrow` structure. Sorted
  newest-first.
- Post tags become Quarto **categories**; Quarto generates the clickable filter,
  styled to match the current chip bar.
- Home "Latest Writing" becomes an embedded listing showing the **3 most recent**
  posts. Behavior change: the old "within last 2 years" rule is dropped (so 3
  posts show instead of today's 1). Accepted as an improvement.

### Posts (frozen)
- Each post -> `posts/<slug>/index.qmd` with front matter (`title`, `date`,
  `author`, `categories`, `image` cover, `description`) and a markdown body:
  prose, images (moved into the post folder), and code as **static fenced
  blocks** (shown, not executed).
- Quarto's built-in syntax highlighter replaces highlight.js, themed to the
  palette.
- Special cases preserved: "Wiped off the map" keeps its static map image + link;
  "thicket-change" keeps its Juxtapose iframe.
- The 11 slugs: `0-to-100km`, `ml-vegetation-monitoring`, `scheduled-earth-engine`,
  `advi-vs-mcmc`, `reproducible-r-1`, `wiped-off-the-map`, `thicket-change`,
  `fynbos-id`, `planet-labs-r`, `emma-un-challenge`, `data-carpentry-ethiopia`
  (`planet-labs-r` has no images).

### Code execution (new capability)
- Old posts: static, nothing runs.
- New posts: live R (knitr) or Python (jupyter) chunks, engine auto-detected.
- `execute: freeze: auto` so results are cached and builds stay reproducible.

## Data flow

Content authored in `.qmd` / `.md` -> `quarto render` -> static site in `_site/`.
Preview during development with `quarto preview`.

## Error handling / risks

- Broken links or missing images after the move: caught by browser verification.
- Render failures: each page/post must render cleanly before it is considered
  done.
- The Juxtapose iframe logs a benign cross-origin notice under `file://`; fine on
  a real server.

## Testing / verification

- `quarto render` completes with no errors.
- Walk every page and a sample of posts in a browser: images load, links work,
  the listing filter works, and the console is clean. Same bar the current site
  was held to.

## Documentation

- Rewrite `updating.md` (or a README) for the new Quarto workflow: add a post =
  new folder + front matter; nav/footer/theme edited once.

## Out of scope (for now)

Deployment (Quarto -> GitHub Pages / Netlify is a later one-command step), dark
mode, site search, data-driven papers page.
