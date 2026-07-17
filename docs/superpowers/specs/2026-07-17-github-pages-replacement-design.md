# Design: Replace GMoncrieff.github.io with the Quarto site

**Date:** 2026-07-17
**Status:** Approved (design phase)

## Goal

Make `https://gmoncrieff.github.io/` serve the Quarto site built in this repo,
replacing the R Markdown / distill site that is live today. Preserve inbound
links to the old blog posts, preserve the old commit history, and remove the
`background/` working material from the public repo.

## Starting state (verified)

- **Live site:** `GMoncrieff.github.io`, public, Pages `build_type: legacy`,
  source `master` branch root, no CNAME, HTTPS enforced. Built from distill with
  `output_dir: "."`, so source `.Rmd` and rendered `.html` share the repo root.
- **This repo (`glenn_website`):** the Quarto site. Branch `main`. **No git
  remote.** History is unrelated to the live repo's history.
- **`context/`:** a clone of `GMoncrieff.github.io` at `193f594`, working tree
  clean. Local reference material only.
- **`background/`:** 69 tracked files (CV LaTeX, post drafts, old static site
  assets, plus a bare gitlink at mode 160000 pointing to `193f594`). Renamed to
  `context/` on disk, so git shows the tracked copies as deleted.
- **No post contains executable `{r}` or `{python}` chunks.** Every post is
  static markdown, so building the site needs Quarto alone. No R, no Python.
- **Toolchain:** Quarto 1.5.57 local, `gh` authed as GMoncrieff with `repo` and
  `workflow` scopes, repo admin rights, Actions enabled, `git-filter-repo` 2.47.0.

## Decisions (confirmed with user)

1. **Topology:** source on `master`, GitHub Actions renders and deploys. Pages
   `build_type` moves from `legacy` to `workflow`. No `gh-pages` branch. Chosen
   so the source and the live site cannot drift.
2. **Old history:** preserve it. Join the two unrelated histories with
   `git merge -s ours --allow-unrelated-histories`, which keeps the Quarto tree
   as the content while leaving every old distill commit reachable. Normal push,
   no force.
3. **Redirects:** add all 9. Eight renamed posts get Quarto `aliases:`, and
   `/about.html` gets a stub pointing at the home page.
4. **`background/`:** untrack it **and** purge it from history with
   `git filter-repo`. Files stay on disk. Every commit SHA in this repo changes.
5. **Branch name:** rename local `main` to `master` so local and remote agree.

## URL mapping

Eight of the nine published post URLs change. Each old URL becomes an alias on
the corresponding new post.

| Old URL (live today) | New URL |
| --- | --- |
| `/posts/2020-08-12-advi-vs-mcmc/` | `/posts/advi-vs-mcmc/` |
| `/posts/2021-09-22-sheduled-earth-engine/` | `/posts/scheduled-earth-engine/` |
| `/posts/2022-10-11-ml-for-vegetation-monitoring/` | `/posts/ml-vegetation-monitoring/` |
| `/posts/dc-ethiopia/` | `/posts/data-carpentry-ethiopia/` |
| `/posts/emma/` | `/posts/emma-un-challenge/` |
| `/posts/fynbos_id/` | `/posts/fynbos-id/` |
| `/posts/repro-r-1/` | `/posts/reproducible-r-1/` |
| `/posts/thicket_change/` | `/posts/thicket-change/` |
| `/posts/wiped-off-the-map/` | unchanged |
| `/about.html` | `/` (stub redirect; the new home page carries the about copy) |

`0-to-100km` and `planet-labs-r` are new and have no old URL.

GitHub Pages cannot serve real HTTP 301s from a static branch. Quarto aliases
emit a meta-refresh page with a `<link rel="canonical">`, which search engines
treat as a soft 301 and which transfers ranking to the new URL.

## Architecture

```
GMoncrieff.github.io (public), one branch:

master
├── _quarto.yml  index.qmd  papers.qmd  blog.qmd  projects.qmd  contact.qmd
├── posts/<slug>/index.qmd          11 posts
├── theme/  assets/  scripts/  docs/
└── .github/workflows/publish.yml
          │  on: push to master
          ▼
   quarto render  ->  _site/  ->  upload-pages-artifact  ->  deploy-pages
                                                                  │
                                                                  ▼
                                                  https://gmoncrieff.github.io/
```

The workflow pins Quarto to 1.5.57 to match local. It installs no language
runtime, because no post executes code.

## Plan

**Phase 1, clean the source repo (local, reversible)**

1. Back up: full directory copy plus `git bundle --all`. Verify both.
2. Untrack `.DS_Store`. Add `/context/` to `.gitignore`.
3. Update the stale render exclusion in `_quarto.yml`: `!background/` becomes
   `!context/`.
4. Commit, then `git filter-repo --path background/ --invert-paths --force`.
5. Rename `main` to `master`.

**Phase 2, redirects**

6. Add `aliases:` front matter to the 8 renamed posts.
7. Add the `/about.html` stub.
8. Render and confirm all 9 redirect files exist and point at the right targets.

**Phase 3, CI**

9. Add `.github/workflows/publish.yml`.

**Phase 4, join histories and push**

10. Add the remote. This must happen **after** filter-repo, which deletes remotes
    on exit as a guard against pushing rewritten history.
11. `git fetch origin`, then
    `git merge -s ours --allow-unrelated-histories origin/master`.
12. Inspect the merged tree, then push without force.

**Phase 5, flip Pages and verify**

13. Set `build_type: workflow` via the API.
14. Watch the run.
15. Verify the live site.

## Verification

Nothing is called done without command output to back it up.

- `python3 scripts/check_site.py` against the build, for internal links and
  image paths.
- Every one of the 9 old URLs fetched from the live site, expecting a redirect
  to the mapped new URL.
- All 11 new post URLs plus the 5 nav pages fetched, expecting 200.
- `git log` on the pushed branch showing old distill commits still reachable.
- `git log --all -- background/` returning nothing.

## Risks and rollback

| Risk | Mitigation |
| --- | --- |
| filter-repo rewrite goes wrong | Verified backup copy and bundle taken first. Repo has no remote, so no shared SHAs exist. |
| `-s ours` merge keeps the wrong tree | Inspect the tree before pushing. Reset is local and free. |
| Pages flip breaks the live site | Reversible to `legacy` / `master` in one API call. |
| Old site lost | Recoverable from the `context/` clone and from the preserved history. |

## Out of scope

- Purging `.DS_Store` from history. It is untracked going forward, but left in
  old commits to keep the rewrite scoped to what was agreed.
- Moving the repo default branch to `main`.
- Any change to site content, design, or copy.
