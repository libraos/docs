---
slug: /web-search
sidebar_position: 5
title: Web search
description: Give an agent the live web — the four tools, what a result actually is, how to bound the spend, and how to tell a page that was read from a page that was only found.
---

# Web search

A bound agent answers from your workspace. Some questions need the world
outside it — a rule that changed last month, a price, a public filing. This
page is how you give an agent the live web, and how to trust what comes back.

The hard part is not fetching. It is knowing **what you got**: a page the
system actually read, a snippet a search engine showed it, or a model's prose
*about* a page it never opened. Libra OS labels all three, and the labels are
the point.

## Turn it on

Web access is a capability an agent declares. Nothing reaches the internet
unless an agent is given a tool that does.

```yaml
capabilities:
  - search_web      # search, with optional page content
  - fetch_url       # read one specific URL
  - research_query  # high-accuracy lookup for a single question
  - deep_research   # multi-aspect research with synthesis
```

Give an agent the least of these that does its job. `search_web` and
`fetch_url` cover most work. `deep_research` plans several angles, runs them
in parallel and synthesizes — powerful, and the most expensive thing on this
page.

## Choose a backend

Search runs through a provider. The managed gateway is the supported path and
needs one credential:

```bash
MEGANOVA_CLOUD_KEY=...
```

That is the whole configuration. If you would rather bring your own provider
keys, set them and they are used as a fallback chain behind the gateway; with
no gateway key they become the primary. Pin one explicitly with
`LIBRA_OS_WEB_SEARCH`.

Page fetching is separate from search and is chosen with
`LIBRA_OS_WEB_FETCHER`. The default is fine unless you self-host a crawler.

## What a result actually is

Every result declares what its text **is** and what happened to it. Read these
two fields before you trust a quote.

| `representation` | Meaning |
| --- | --- |
| `search_snippet` | The snippet a search engine returned |
| `provider_excerpt` | Page text the provider's crawler fetched |
| `page_extract` | Page text **Libra OS itself** fetched |
| `provider_summary` | The provider's generated prose *about* the page |
| `model_answer` | A model's answer to your query — not a source at all |

The first three are page-derived: they are words that appear on the page. The
last two are model-generated. A `provider_summary` can be accurate and still
be the wrong thing to quote, because nobody guarantees the page says it.

| `status` | Meaning |
| --- | --- |
| `opened` | The page was read |
| *(empty)* | The result was found and nothing more was attempted |
| `blocked_policy` | We declined to read it — publisher policy or robots.txt |
| `blocked_soft` | The site served an anti-bot challenge instead of the page |
| `blocked_target` | The URL was refused by the SSRF guard |
| `fetch_failed` | A fetch was attempted and returned nothing |

**Found and opened are different claims.** An answer citing ten results where
none has `status: opened` was assembled from snippets.

A model answer never sits among your results. It travels separately as
`provider_answer`, so it cannot be mistaken for a hit.

## Bound the spend

Research is the one capability that can run away with a turn. Two per-call
controls:

```jsonc
{
  "metadata": {
    "max_searches": 3,          // hard cap on searches this turn
    "research_query": "..."     // the question to research
  }
}
```

`max_searches` is a ceiling across every search the turn makes — the planner's
fan-out, the tools, enrichment. Without it a multi-aspect plan can issue
several searches where one would do.

`research_query` matters more than it looks. Applications usually send an
assembled message: a response-language directive, formatting rules,
conversation history, then the user's actual question. Left alone, the planner
decomposes *all of it*, and fragments of your own system prompt can end up as
search queries at a third-party provider. Passing the question as its own
field prevents that. Libra OS also refuses to send assembled-prompt text as a
query, but the explicit field is better than the guard.

Server-side budgets exist for the long paths —
`LIBRA_OS_RESEARCH_SKILL_TIMEOUT`, `LIBRA_OS_DEEP_RESEARCH_TIMEOUT`,
`LIBRA_OS_DEEP_SEARCH_MAX_CONCURRENCY` — so one turn cannot occupy the
deployment.

## Reading the answer

Every chat response carries a `grounding` verdict. For web work these are the
ones to watch:

| Verdict | What happened |
| --- | --- |
| `grounded` | Evidence was retrieved and used |
| `unopened_sources` | It searched, cited what it found, and **opened none of it** |
| `unsupported_claim` | It claimed a source it never consulted |
| `ungrounded_no_chunks` | Nothing was retrieved and no tool ran |

`unopened_sources` is the one worth alerting on. The answer is confident, the
citations look real, and every one is a search snippet — which is not a lie,
but is much weaker than it appears. It usually means fetches were blocked or
failing, and it is the single most useful signal that web research has
silently degraded.

## When a source refuses

Not every page can be read, and Libra OS reports why rather than failing
generically:

- **`blocked_policy`** — the publisher's `robots.txt` disallows this path, or
  the deployment's source policy marks it licensed or manual-only. This is a
  lawful refusal, not an error: it is not retried and it does not count as a
  failure in health metrics.
- **`blocked_soft`** — the site returned an anti-bot challenge with a `200`
  status. The refusal names the vendor where it can be identified.

Libra OS does not evade these. No fingerprint spoofing, no CAPTCHA solving, no
proxy rotation. A wall is reported as a wall — a refusal you can see beats
content you cannot trust.

## A worked example

```bash
curl -s -X POST $KERNEL/v1/messages \
  -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d '{
    "model": "research-assistant",
    "max_tokens": 900,
    "metadata": { "max_searches": 3, "research_query": "What changed in the 2026 filing deadline?" },
    "messages": [{"role": "user", "content": "What changed in the 2026 filing deadline? Cite sources."}]
  }'
```

Check three things in the response: `grounding` is `grounded`, at least one
cited source has `status: opened`, and any text you plan to quote is
page-derived rather than `provider_summary`.

## Where to go next

- [Workspaces & memory](/workspaces-memory) — grounding in **your** documents,
  which is usually the better answer when the knowledge is yours
- [Managing memory](/managing-memory) — what persists across sessions
- [Security model](/security) — what leaves the deployment, and what does not
