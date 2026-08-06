---
slug: /model-settings
sidebar_position: 5
title: Model settings & token plans
description: Point the routing tiers at any OpenAI-compatible endpoint — or at your token plan's covered models.
---

# Model settings & token plans

Libra OS routes work across three model tiers. Each tier is just a model id
behind an OpenAI-compatible endpoint, so configuration is a key, a base URL, and
your model ids — nothing else.

| Tier | What it does | Setting |
| --- | --- | --- |
| **Brain** | Plans the task and makes the hard calls | `LIBRA_OS_BRAIN_MODEL` |
| **Skill** | Runs the cheap, high-volume agent steps | `LIBRA_OS_SKILL_MODEL` |
| **Answer / synthesis** | Writes the final grounded answer | `OPENAI_MODEL` |

The gateway itself is set with `OPENAI_API_KEY` and `OPENAI_API_BASE`. The
canonical prefix is `LIBRA_OS_*`; the legacy `NOVA_OS_*` names are bridged and
keep working forever, so renaming existing deployments is optional. Any
OpenAI-compatible provider works — bring your own keys, point the tiers at
local models, or mix per tier.

## Pay-as-you-go or a token plan

Billing through the gateway is **pay-as-you-go by default**: any API key works
immediately, metered per token, no subscription required. A token plan (from
**$249/month** — see [pricing](https://libraos.com/pricing/)) is the optional
flat-rate alternative — a monthly fee that includes an enterprise-model usage
allowance, with usage running on the enterprise-grade `-Ent` model endpoints.

For business deployments the token plan is **strongly recommended**: the
covered `-Ent` ids carry enterprise-level security and data handling, on top
of predictable billing. If you're evaluating or happy paying per token,
pay-as-you-go works fine and you can skip the rest of this section.

## Using your token plan

To draw from your plan's allowance instead of paying per token:

**1. Use the plan key.** Your subscription page provisions a dedicated API key
when the plan activates. The allowance only applies to that key — usage on any
other key, even for the same models, is billed pay-as-you-go.

**2. Set the base URL** to the bare gateway host, without `/v1`:

```bash
OPENAI_API_KEY=sk-<your plan key>
OPENAI_API_BASE=https://api.meganova.ai
LIBRA_OS_BRAIN_MODEL=anthropic/claude-opus-5-Ent
LIBRA_OS_SKILL_MODEL=gemini/gemini-2.5-flash-lite-Ent
OPENAI_MODEL=gemini/gemini-2.5-pro-Ent
```

**3. Use only covered model ids**, in the full `provider/...-Ent` form. Bare
names are rejected, and any non-covered model called with the plan key is billed
pay-as-you-go rather than drawing from the allowance.

The covered list:

| Provider | Model id |
| --- | --- |
| Anthropic | `anthropic/claude-opus-5-Ent` |
| Anthropic | `anthropic/claude-sonnet-5-Ent` |
| Anthropic | `anthropic/claude-opus-4-8-Ent` |
| Anthropic | `anthropic/claude-opus-4-7-Ent` |
| Anthropic | `anthropic/claude-sonnet-4-6-Ent` |
| Anthropic | `anthropic/claude-haiku-4-5-20251001-Ent` |
| Gemini | `gemini/gemini-3.6-flash-Ent` |
| Gemini | `gemini/gemini-3.5-flash-Ent` |
| Gemini | `gemini/gemini-3.5-flash-lite-Ent` |
| Gemini | `gemini/gemini-3.1-pro-preview-Ent` |
| Gemini | `gemini/gemini-3.1-flash-lite-Ent` |
| Gemini | `gemini/gemini-3-flash-preview-Ent` |
| Gemini | `gemini/gemini-2.5-pro-Ent` |
| Gemini | `gemini/gemini-2.5-flash-Ent` |
| Gemini | `gemini/gemini-2.5-flash-lite-Ent` |

The list grows over time — your plan's subscription page always shows the
current version. Map the brain / skill / synthesis tiers to ids from this
list to stretch the allowance: a `-pro-Ent` (or Opus-class) model for the
brain and synthesis tiers, a `-flash-lite-Ent` for the cheap, high-volume
skill tier — as in the example above.

**Audio is covered too:** transcription with `Systran/faster-whisper-large-v3`
at `POST /v1/audio/transcriptions` on the same gateway draws from the same
allowance (billed per second of audio). This is a single public model id for
speech-to-text — not an `-Ent` variant, and not one of the LLM tiers above.
On any non-plan key it stays pay-as-you-go as usual.

## Local models

Everything above also runs fully local — the tiers point at a local
OpenAI-compatible server instead of a hosted gateway. This is the usual
configuration for air-gapped deployments, and there is no billing involved
at all.

**Generation (the LLM tiers).** Ollama and similar local servers expose an
OpenAI-compatible API. Point the gateway settings at it and use the server's
bare model names — locally-run Ollama is the one case that takes no vendor
prefix:

```bash
OPENAI_API_BASE=http://localhost:11434/v1   # Ollama's OpenAI-compatible endpoint
OPENAI_API_KEY=ollama                       # any non-empty value
LIBRA_OS_BRAIN_MODEL=qwen3:32b
LIBRA_OS_SKILL_MODEL=llama3.2:3b
OPENAI_MODEL=qwen3:32b
```

**Embeddings.** Knowledge-base embeddings are configured independently of
the generation endpoint, because a local generation server usually serves no
embedder:

- **Local embeddings via Ollama:** set `LIBRA_OS_OLLAMA_URL`
  (e.g. `http://localhost:11434`). The default embedding model is
  `snowflake-arctic-embed:l`; override with `LIBRA_OS_OLLAMA_EMBED_MODEL`.
  Note the deliberate precedence rule: if a gateway embedding model is
  pinned via `LIBRA_OS_EMBEDDING_MODEL`, it wins — the Ollama opt-in only
  applies when no gateway model is set, so an Ollama URL configured for
  other purposes can't silently reroute embeddings to the slower local path.
- **Remote embeddings with local generation:** set
  `LIBRA_OS_EMBEDDING_API_BASE` (and `LIBRA_OS_EMBEDDING_API_KEY`) to keep
  embeddings on a dedicated endpoint while `OPENAI_API_BASE` points at your
  local generation server.

**Embedding dimensions must match the model.** Set `LIBRA_OS_EMBED_DIM` to
the model's output size — `qwen3-embedding:8b` → 4096, `bge-m3` → 1024,
`snowflake-arctic-embed:l` → 1024, `nomic-embed-text` → 768. The vector
index is created at that dimension, so switching to a model with a different
dimension means re-ingesting the knowledge base.

## Hot reload — change models without a restart

Settings persist and reload at runtime via the settings API:

```bash
curl -X PUT http://localhost:8000/api/config/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "openai_api_key": "sk-<your plan key>",
    "openai_api_base": "https://api.meganova.ai",
    "synthesis_model": "gemini/gemini-2.5-pro-Ent"
  }'
```

This is also how key rotation works: regenerate the key on the subscription
page, then hot-reload the new value — the old key stops working immediately.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| Requests billed pay-as-you-go instead of the allowance | Wrong key, or a non-covered model id |
| `404` on model calls | Missing `provider/` prefix, or base URL includes `/v1` |
| Requests hard-stop mid-month | Allowance exhausted and extra usage not enabled — enable it (with a monthly cap) on the subscription page |

The allowance resets at the start of each billing period. Overage is opt-in and
capped — it is never charged automatically.
