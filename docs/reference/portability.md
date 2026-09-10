---
slug: /portability
sidebar_position: 4
title: Portability contract
description: What behaves identically everywhere, what degrades by environment, and what is simply absent — stated before you hit the seam rather than after.
---

# Portability contract

Libra OS runs in three shapes: connected to a model gateway, on your own
hardware with local models, and fully air-gapped. **The same binary, the same
agents, the same API — but not the same capabilities.**

This page states which is which. You will meet this seam on day one; it is
better read than discovered.

The rule throughout: **a capability that cannot run is reported, not
simulated.** Libra OS would rather return a refusal you can see than an answer
you cannot trust.

## Identical everywhere

These do not depend on the environment:

- the HTTP surface — chat, agents, jobs, documents, knowledge, OIDC
- agent definitions, employee YAML, `output_type` and `persist_fields`
- conversation threads, [memory scopes](/managing-memory), house profiles
- the firewall and outbound guardrails
- audit trails, `grounding` verdicts, `retrieved_chunks`, `citations_verified`
- role and collection authorization

Write an agent against one shape and it loads in all three. What changes is
what its *tools* can reach.

## Degrades by environment

### Knowledge retrieval

The single most important seam, because it degrades **silently** unless you
look.

| store | vector search | durable |
| --- | --- | --- |
| **SurrealDB** | **yes** — hybrid keyword + vector | yes |
| pgvector | **no** — full-text only, despite the name | yes |
| Qdrant | **no** — payload filter, not similarity | yes |
| in-memory | yes | **no** — wiped on restart |

Only SurrealDB gives you semantic retrieval on a durable store. `pgvector` and
`qdrant` are named for vector databases and are configured through them, but
the current read and write paths use full-text search. A deployment can have
embeddings configured, a healthy boot, and keyword-only retrieval.

**Check rather than assume:**

```bash
curl -s localhost:8900/api/capabilities | jq .retrieval
```

`"vector_search": true` means semantic. When it is false, answers carry
`grounding: degraded_retrieval` so the weakness reaches the reader, not just
the log.

### Web search and page fetch

| environment | behaviour |
| --- | --- |
| gateway configured | full search + page fetch |
| your own provider keys | full, through your provider |
| **no backend** | tools return an explicit *"no search backend configured"* note |

In an air-gapped deployment, `search_web` does not fail the turn and does not
invent results — it returns a note saying no backend is configured, and
`research_query` returns a typed error. An agent that needed the web reports
that it could not reach it.

Answers that searched but opened no page carry `grounding: unopened_sources`.
See [Web search](/web-search).

### Code execution

`code_exec` and `shell` are **fail-closed**. Without a container runtime they
**refuse to execute** rather than run unisolated on the host. That is the
default and it is deliberate: model-authored code running as the server
process, with the server's credentials, is not a degraded mode — it is a
different security posture.

An operator can opt out explicitly, and the choice is logged.

### Models

Any OpenAI-compatible endpoint works, per tier. Point them at a gateway, at
your own vLLM, or at a mix. A fully local deployment sets the planner and
skill tiers at a local endpoint and never calls out.

Embeddings have a local path too — a local embedding server rather than the
gateway — so a deployment where even embeddings must not leave the building is
supported. It is slower; that is the trade.

## Absent without an external service

These have **no local fallback**. In an air-gapped deployment they are
unavailable, and the endpoints say so rather than degrading:

- **OCR for scanned documents** — vision model
- **Image generation** — `/v1/images/*`
- **Speech to text and text to speech** — `/v1/audio/*`
- **Realtime voice** — `/v1/realtime`

Text-to-text does **not** belong on this list. Chat, planning, retrieval and
synthesis all run against whatever endpoint you point them at, including a
local one.

Documents with a text layer parse locally — DOCX, XLSX, PDF-with-text, ODT,
CSV, HTML, email. Only *scanned* documents need the vision path.

## Writing agents that travel

Declare the least you need. An agent with `search_web` in an air-gapped
deployment is not broken — it gets an honest note — but an agent that does not
declare it cannot be surprised.

Read the verdict, not just the answer. `grounding` distinguishes *grounded*,
*degraded_retrieval*, *unopened_sources* and *ungrounded_no_chunks*. An
integration that branches on it behaves correctly in all three shapes without
knowing which one it is in.

Check capabilities at startup rather than inferring from configuration.
`GET /api/capabilities` reports what is **effectively** running — which is not
always what the environment variables say. That gap is the reason the endpoint
exists.

## Where to go next

- [Deployment](/deployment) — the three shapes in practice
- [Security model](/security) — what leaves the deployment
- [Web search](/web-search) · [Managing memory](/managing-memory)
