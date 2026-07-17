# Updating the site

The site is built with [Quarto](https://quarto.org/). Source files are `.qmd` (Quarto Markdown). Quarto renders them to `_site/`, which is the final output.

## Prerequisites

Quarto 1.5.57 or later. Check: `quarto --version`.

## Preview and build

```bash
# live preview with auto-reload
quarto preview

# full build to _site/
quarto render
```

`quarto preview` watches for changes and refreshes the browser automatically. Use it while writing.

## Layout

```
_quarto.yml             site config: navbar, footer, theme, render scope
index.qmd               home page (hero, about, cards, selected papers, latest writing)
papers.qmd              publications grouped by year
blog.qmd                blog listing (auto-built from posts/)
projects.qmd            4 project cards
contact.qmd             contact details
posts/<slug>/
  index.qmd             one folder per post
  image.png             images sit beside the post file
theme/
  custom.scss           all styles: CSS variables at top, then rules
  listing.ejs           template for a blog listing row
  listing-home.ejs      template for the home "Latest Writing" rows
  fonts.html            font <link> tags injected into <head>
assets/
  logo.svg              site logo / favicon
  avatar.png            portrait used on the home page
scripts/
  check_site.py         verifies internal links and image paths
  enhance_redirects.py  strengthens the redirect stubs (see Old URLs)
.github/workflows/
  publish.yml           builds and deploys the site on every push
```

Nav, footer, and brand are defined once in `_quarto.yml`. Theme palette, fonts, and spacing are CSS variables at the top of `theme/custom.scss`.

## Add a blog post

1. Create a folder under `posts/`:

   ```bash
   mkdir posts/my-new-post
   ```

2. Create `posts/my-new-post/index.qmd` with this front matter:

   ```yaml
   ---
   title: "Post title"
   date: YYYY-MM-DD
   categories: [Tag1, Tag2]
   description: "One-line summary shown in the listing."
   ---
   ```

   **Categories must come from this fixed set:** R, Python, AI/ML, LLMs, Remote Sensing, Conservation, Teaching, Savannas, Fynbos, Forecasting, Ecosystem Condition, Ultra running, Biodiversity monitoring.

3. Put images in the same folder (`posts/my-new-post/photo.png`) and reference them by bare filename:

   ```markdown
   ![Caption](photo.png)
   ```

4. Write the body using this structure:

   ```markdown
   ::: {.article}

   [← Back to blog](../../blog.qmd){.text-link}

   ::: {.article__head}
   <div class="article__meta"><span>YYYY · MM · DD</span><span>·</span><span>N min read</span><span>·</span><span style="color:var(--accent);">Tag</span></div>

   # Post title

   <p class="hero__tag" style="text-align:left; margin:0; max-width:62ch;">Lead sentence or two.</p>
   :::

   ::: {.prose}

   Post body goes here.

   :::

   :::
   ```

5. **Code blocks.** Use plain fences for static display:

   ````markdown
   ```r
   x <- 1 + 1
   ```
   ````

   Use executable chunks to run code at render time (output is included in the page):

   ````markdown
   ```{r}
   x <- 1 + 1
   x
   ```
   ````

   Both R and Python are supported. Executed output is frozen after the first render (`execute: freeze: auto` in `_quarto.yml`), so re-renders are fast unless the chunk changes.

The post appears automatically in the blog listing and, if it is recent, in the home page "Latest Writing" section. No manual index update is needed.

## Edit the site

- **Text and content:** edit the relevant `.qmd` file directly.
- **Papers:** add a row to the right year group in `papers.qmd`, then update that group's paper count.
- **Nav, footer, brand:** edit `_quarto.yml`. One change applies everywhere.
- **Look and feel:** edit `theme/custom.scss`. Palette, fonts, and spacing are CSS variables near the top; change them once and they apply everywhere.

### Raw HTML in top-level pages

Top-level pages (`index.qmd`, `papers.qmd`, etc.) contain blocks of raw HTML. Wrap any raw HTML in a ```` ```{=html} ```` block, or Pandoc will treat indented HTML as a code listing:

````markdown
```{=html}
<div class="my-block">...</div>
```
````

Posts that use `::: {.prose}` divs do not need this.

## Publish

Push to `master`. That is the whole process.

```bash
git add -A
git commit -m "your message"
git push
```

`.github/workflows/publish.yml` renders the site and deploys it to
<https://gmoncrieff.github.io/>, usually within a minute. Do not run
`quarto publish gh-pages`: there is no `gh-pages` branch, and the source on
`master` is the only thing that decides what is live.

Watch a build:

```bash
gh run watch
```

If the build fails the live site is left untouched, so a broken render never
reaches visitors. The build also runs `scripts/check_site.py`, so a dead
internal link or a missing image fails the run rather than shipping.

## Old URLs

The site this replaced used different post slugs. Each renamed post carries an
`aliases:` entry naming its old URL, which makes Quarto write a small redirect
page there:

```yaml
---
title: "EMMA wins the UN Data for Climate Action challenge"
aliases:
  - /posts/emma/
---
```

Quarto's own stub redirects with JavaScript only and sets no canonical link, so
`scripts/enhance_redirects.py` rewrites every stub after each render to lead
with `rel=canonical` and a meta refresh, keeping the JavaScript for `#anchor`
links. It is wired in as a `post-render` step in `_quarto.yml` and needs no
attention.

If you ever rename a post folder, add its previous URL to `aliases:` in the same
edit. That is what keeps old links and search results working.

## Notes

- After a render, open `_site/index.html` in a browser or run `python3 -m http.server 8000` in `_site/` to check it locally.
- The checker script (`python3 scripts/check_site.py`) verifies internal links and image paths across the built site.
- **Writing style** (Glenn's preference for his own copy): plain language, no em dashes, no marketing-speak.
