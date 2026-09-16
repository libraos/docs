---
slug: /model-settings
sidebar_position: 5
title: Model settings
description: Configure the gateway, distinguish agent IDs from model IDs, and resolve answer, planner, skill, embedding, and memory models.
---

# Model settings

An **agent ID** selects executable behavior. A **model ID** selects an upstream
model served by your configured endpoint. The agent's prompt, tools, and
knowledge bindings remain distinct from that model.

## Configure the server defaults

| Slot | Purpose | Environment setting |
| --- | --- | --- |
| Answer | Generates the response | `OPENAI_MODEL` |
| Planner | Plans or decomposes work when enabled | `LIBRA_OS_BRAIN_MODEL` |
| Skill | Runs delegated skill work | `LIBRA_OS_SKILL_MODEL` |

The gateway is configured with `OPENAI_API_BASE` and `OPENAI_API_KEY`.
Use model IDs available to that endpoint and credential. The values below are
placeholders; replace them before starting:

```bash
export OPENAI_API_BASE=https://api.meganova.ai
export OPENAI_API_KEY='your-gateway-key'
export OPENAI_MODEL='provider/answer-model'
export LIBRA_OS_BRAIN_MODEL='provider/planner-model'
export LIBRA_OS_SKILL_MODEL='provider/skill-model'
```

A routing gateway commonly uses `provider/model` IDs. Other compatible
endpoints use their own model names. Follow the endpoint's supported naming
and base-URL convention; a model listed by one provider is not necessarily
available through another.

The canonical environment prefix is `LIBRA_OS_*`. Legacy `NOVA_OS_*`
aliases remain supported where bridged by the server.

## Override defaults in a definition

Agent and employee Markdown definitions support:

```yaml
model_config:
  answer:
    primary: provider/answer-model
    fallback: [provider/fallback-model]
  planner:
    primary: provider/planner-model
  skill:
    primary: provider/skill-model
```

Resolution is **per slot**: agent → owning employee → server default.
The first slot with a primary model supplies its whole fallback list.
For example, an agent defining only `answer` can still inherit `planner`
and `skill` from its employee. If no employee is linked, resolution skips
that level.

This is a file-definition feature; the managed-agent API does not accept
every YAML field. See [Employee YAML](/employee-yaml) before translating
frontmatter into an API request.

Supported per-call model overrides apply at the endpoint layer. They do not
rebind the employee or change all tiers. See [Calling agents](/calling-agents).

## Local models

Run the model server separately, provision its weights, and configure all
required tiers. For example, with Ollama and models already installed:

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export LIBRA_OS_BRAIN_MODEL=qwen3:32b
export LIBRA_OS_SKILL_MODEL=qwen3:32b
export OPENAI_MODEL=qwen3:32b
```

These are illustrative model names, not downloads performed by Libra OS.
Select models that fit your hardware and support the tools your agents need.
Local generation alone does not make embeddings, search, or callbacks local.

## Embeddings

Knowledge-base embeddings have independent configuration:

- **Local Ollama:** set `LIBRA_OS_OLLAMA_URL` and, if needed,
  `LIBRA_OS_OLLAMA_EMBED_MODEL`. A pinned `LIBRA_OS_EMBEDDING_MODEL`
  takes precedence over the Ollama opt-in.
- **Dedicated embedding endpoint:** set `LIBRA_OS_EMBEDDING_API_BASE`
  and `LIBRA_OS_EMBEDDING_API_KEY` as required.
- **Dimensions:** set `LIBRA_OS_EMBED_DIM` to the selected model's output
  dimension. A change of embedding model or dimension may require reindexing;
  do not reuse an incompatible vector index.

Confirm the selected backend supports semantic retrieval using
[the capabilities check](/portability#knowledge-retrieval).

## Memory worker model

When observational memory is enabled, its Observer and Reflector use a model
to summarize conversation content. Configure `LIBRA_OS_MEMORY_WORKER_MODEL`
for that workload and account for its processing location separately.
See [Managing memory](/managing-memory).

## Web search

Web search is a separate capability from generation. When the LLM and search
services use the same MegaNova gateway host, search can reuse
`OPENAI_API_KEY`. A key for an unrelated provider or local model server does
not enable managed search.

`LIBRA_OS_WEB_SEARCH` selects the general search backend;
`LIBRA_OS_DEEP_SEARCH_BACKEND` controls the deep-research backend.
Supported alternatives require their own configured service or credentials.
`LIBRA_OS_WEB_FETCHER` selects page fetching.
See [Web search](/web-search) for activation, results, and budgets.

## Gateway plans and billing

Billing and model entitlement belong to your gateway account. Confirm the
current model list, covered IDs, key, limits, and prices there. A provider or
`-Ent` suffix alone does not establish a privacy guarantee or entitlement.
The runtime's agent definition does not purchase a plan or make an unavailable
model usable.

## Change settings

An administrator can inspect and update runtime settings through
`/api/config/settings`. Use an authenticated request to your actual server,
and check the accepted fields for the installed release. Some settings reload
live; others require recreating clients or restarting the server.

For example, to inspect configuration:

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/api/config/settings" \
  -H "Authorization: Bearer $LIBRA_OS_API_KEY"
```

Changing the runtime's stored key and revoking a key at the provider are
separate operations.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Upstream model not found | Exact model ID, endpoint URL, and credential entitlement. |
| Wrong agent answers | Endpoint-specific agent selection; see [Calling agents](/calling-agents). |
| Unexpected model | Agent override, employee slot, and server default in that order. |
| Chat works but search does not | Search backend availability; a working model endpoint is insufficient. |
| Retrieval fails after a model change | Embedding dimensions, index compatibility, and ingestion status. |
| Data reaches a hosted service unexpectedly | Every model tier, embeddings, memory worker, search, and callbacks. |
