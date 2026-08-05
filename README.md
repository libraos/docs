# Libra OS — Docs & Blog

Developer-editable documentation and blog for **Libra OS**, built with
[Docusaurus](https://docusaurus.io). SEO-friendly static output, Google Analytics
on every page, and an auto-generated **`llms.txt`** so AI agents (and our own
help widget) can read the docs cleanly.

- **Docs** publish to `https://libraos.com/docs/`
- **Blog** publishes to `https://libraos.com/docs/blog/`
- **Agent feed**: `https://libraos.com/docs/llms.txt` (+ `llms-full.txt`)

This repo is **private**. Only the built static site is published — the product
source stays closed. Editing docs never exposes anything but the docs.

## Editing docs (for developers)

1. Add or edit a Markdown file under `docs/` — e.g. `docs/user-guide/backups.md`.
2. Optional frontmatter to control ordering / titles:
   ```md
   ---
   sidebar_position: 3
   title: Backups & restore
   ---
   ```
3. The sidebar is **auto-generated** — new files appear automatically. Group pages
   by folder (add a `_category_.json` to name the group).
4. Open a PR or push to `main`. CI builds and deploys.

Blog posts go in `blog/` (one Markdown file or a dated folder; authors in
`blog/authors.yml`).

## Local development

```bash
npm install
npm start          # dev server with hot reload
npm run build      # production build into ./build (also emits llms.txt)
npm run serve      # preview the production build
```

## Deployment

Pushing to `main` runs `.github/workflows/deploy.yml`: it builds the static
site and publishes it to <https://libraos.com/docs/>. Deploys only run on
pushes to `main` by maintainers — the publish credentials live in repo
secrets (`DEPLOY_SSH_KEY`, `DEPLOY_TARGET`), which pull requests from forks
never receive. Without them, CI still **builds** (and warns) but skips the
deploy — so external PRs get full build validation.

## License

Docs and blog content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Site build code: MIT. See [LICENSE](LICENSE). The Libra OS name and logo are
trademarks of Nebula Nova Inc.
