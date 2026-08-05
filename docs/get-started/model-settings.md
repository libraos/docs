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
allowance. If you're happy paying per token, you can skip the rest of this
section.

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
pay-as-you-go rather than drawing from the allowance. The current covered list
is published on your plan's subscription page.

**Audio is covered too:** transcription with `Systran/faster-whisper-large-v3`
at `POST /v1/audio/transcriptions` on the same gateway draws from the same
allowance (billed per second).

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
