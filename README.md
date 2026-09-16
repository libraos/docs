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
4. Run `npm run build`, then open a PR. CI validates pull requests; a push to
   `main` also deploys when deployment secrets are configured.

Blog posts go in `blog/` (one Markdown file or a dated folder; authors in
`blog/authors.yml`).

## Local development

```bash
npm install
npm start          # dev server with hot reload
npm run build      # production build into ./build (also emits llms.txt)
npm run serve      # preview the production build
```

To check Python/YAML/shell examples and exercise the Python SDK request shapes
without contacting a server, use Python 3.10+ with `libraos-sdk` and `PyYAML`
installed, then run `python3 tools/check_examples.py`. To test a specific SDK
checkout, set `PYTHONPATH=/path/to/sdk/python`. The script mocks HTTP responses;
it does not replace a live integration test against your server release.

## Developer documentation conventions

- Call the executable behavior an **agent**. An **employee record** owns agents
  and provides shared defaults. In Desk, explicitly say **human member** where
  employee refers to a person.
- State the endpoint and its agent selector next to every HTTP example.
  Messages uses `metadata.agent_id`; OpenAI chat uses `model` for an agent;
  native chat puts the agent route ID in the URL.
- Keep YAML fields separate from fields accepted by management APIs. Verify
  the handler and SDK signature before claiming equivalence.
- Distinguish message history, conversation persistence, observations, and
  structured field storage. Identity headers are not authorization grants.
- Examples should create their own agent or name installation prerequisites.
  Do not depend on a fixed set of presets, a fixed binary size, or assumed
  provider model availability.
- Describe data storage separately from model, embedding, search, and callback
  processing. Avoid unconditional claims about citations, privacy, and approval.
- Label fragments and application-specific adapters. Async SDK calls need
  `await`; Messages `content` is a block array, while `response.text` is a helper.
- Keep internal links under the docs base path. The build rejects broken links
  and anchors and generates the LLM feeds from the same source.

## Deployment

Pushing to `main` runs `.github/workflows/deploy.yml`: it builds the static
site and publishes it to <https://libraos.com/docs/>. Deploys only run on
pushes to `main` by maintainers — the publish credentials live in repo
secrets (`DEPLOY_SSH_KEY`, `DEPLOY_TARGET`), which pull requests from forks
never receive. Without them, CI still **builds** (and warns) but skips the
deploy — so external PRs get build validation without deployment access.

## License

Docs and blog content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Site build code: MIT. See [LICENSE](LICENSE). The Libra OS name and logo are
trademarks of Nebula Nova Inc.
