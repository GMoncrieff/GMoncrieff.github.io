# Updating the site

The site is plain static HTML in `site/`. **There is no build step and no framework** — the `.html` files *are* the final output. "Rerendering" just means reloading the page in a browser after you save.

## Layout

```
site/
  index.html          home (hero, about, What I Work On, Latest Writing, Selected Papers)
  papers.html         publications, grouped by year
  blog.html           blog index (post rows + tag filter)
  projects.html       4 project cards
  contact.html        contact details
  posts/<slug>.html   one file per blog post
  assets/
    style.css         shared styles (all colours/fonts/spacing are CSS variables in :root)
    avatar.png        portrait
    highlight.min.js  self-hosted syntax highlighter (code posts only)
    posts/<slug>/     images for that post
```

The nav bar and footer are copied into every page (no includes). A change to them is site-wide only if you edit every file — see "Site-wide changes" below.

## Preview locally ("rerender")

No compile step. Either:

```bash
# simplest: open the file directly
open site/index.html

# better: serve it, so links/paths behave like production
cd site && python3 -m http.server 8000
# then visit http://localhost:8000
```

After editing CSS or JS, hard-refresh (Cmd+Shift+R) to bypass the browser cache.

## Add a blog post

1. **Copy an existing post as a template.** For a normal prose post, copy `posts/0-to-100km.html` (prose + one image, no code). For a post with code, copy `posts/fynbos-id.html`.

   ```bash
   cp site/posts/0-to-100km.html site/posts/my-new-post.html
   ```

   In the new file, update: the `<title>`, the meta line (`YYYY · MM · DD`, read time, and the accent tag), the `<h1>`, the lead paragraph (`.hero__tag`), and the body inside `<div class="prose">`. Leave the nav and footer as they are.

2. **Add images** (if any) to `site/assets/posts/my-new-post/`, and reference them from the post with a `../` prefix (posts sit one folder deep):

   ```html
   <figure>
     <img src="../assets/posts/my-new-post/photo.png" alt="..." />
     <figcaption>Caption.</figcaption>
   </figure>
   ```

3. **Add a row to `blog.html`** at the top of `<div class="rows" id="postRows">` (newest first):

   ```html
   <a class="row" href="posts/my-new-post.html">
     <span class="row__date">YYYY · MM · DD</span>
     <div class="row__main">
       <h3>Title</h3>
       <p>One-line summary.</p>
       <div class="row__tags"><span class="chip">Tag</span></div>
     </div>
     <span class="row__arrow">&rarr;</span>
   </a>
   ```

   Then bump the number in `<span id="entryCount">N entries</span>`. The filter bar builds itself from the chips, so no other change is needed.

   **Tags must come from this fixed set:** R, Python, AI/ML, LLMs, Remote Sensing, Conservation, Teaching, Savannas, Fynbos, Forecasting, Ecosystem Condition, Ultra running, Biodiversity monitoring.

4. **(Optional) Show it on the home page.** "Latest Writing" auto-shows the 3 most recent posts from the last 2 years. To make a post eligible, add it to the array in the `<script>` near the bottom of `index.html` (newest first):

   ```js
   { date: 'YYYY-MM-DD', href: 'posts/my-new-post.html', title: 'Title', summary: 'One-line summary.' },
   ```

5. **Code highlighting.** If the post has code, keep the two `<script>` tags at the bottom of the file and give each block a language: `<pre><code class="language-r">` (or `language-python`, `language-bash`, `language-json`). Inside code, escape `<` `>` `&` as `&lt;` `&gt;` `&amp;`. If the post has no code, delete those two script tags.

## Edit the site

- **Text/content:** edit the relevant page directly (`papers.html`, `projects.html`, etc.).
- **Papers:** add a `<div class="row">` under the right year in `papers.html`, and update that section's count (`NN papers`). Only add a `DOI`/`Code` link if it really exists — don't leave `#` placeholders.
- **Look and feel:** edit `assets/style.css`. The palette, fonts, and spacing are CSS variables at the top (`:root`) — change them once and they apply everywhere.

### Site-wide changes (nav, footer, brand)

Because nav/footer are duplicated, change them everywhere with a find/replace. Example — updating the brand subtitle:

```bash
cd site
python3 - <<'PY'
import glob
old = '<span>· biodiversity data science</span>'
new = '<span>· something new</span>'
for f in glob.glob('**/*.html', recursive=True):
    s = open(f, encoding='utf-8').read()
    if old in s:
        open(f, 'w', encoding='utf-8').write(s.replace(old, new))
PY
```

## Notes

- **Relative paths:** top-level pages use `assets/...`; posts in `posts/` use `../assets/...` and `../blog.html` etc. Copying the wrong template usually means a forgotten `../`.
- **Quick check after editing:** open the page, confirm images load and links work, and check the browser console is clean (no errors).
- **Writing style** (Glenn's preference for his own copy): plain language, no em dashes, no marketing-speak.
- **Publishing:** this is just static files. To put it online, push `site/` to any static host (GitHub Pages, Netlify, Cloudflare Pages). No build command needed.
