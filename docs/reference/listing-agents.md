---
slug: /listing-agents
sidebar_position: 5
title: Listing agents
description: Two endpoints return agents and they answer different questions. Which one to call, and how to tell a tenant's own agents from the bundled presets.
---

# Listing agents

Two endpoints return agents. They are deliberately different, and picking the
wrong one is the most common mistake when building an admin surface — because
the difference is not obvious from the names.

| | `GET /v1/agents` | `GET /api/agents` |
| --- | --- | --- |
| purpose | managed agents, for applications | the loaded registry, for operators |
| auth | your API key | **admin only** |
| tells you which agents are yours | no `source` field | **yes** — `source: custom \| preset` |
| tells you what an agent runs on | `model` | `model`, `model_override`, `model_source` |

If you are **building an application**, use `/v1/agents`.
If you are **building an admin page over the registry**, use `/api/agents`.

## The mistake worth avoiding

A stock deployment ships **more bundled presets than a tenant has agents of its
own**. An admin page that renders `GET /api/agents` unfiltered shows
`skill_docx`, `bi-assistant` and `nova-orchestrator` alongside the tenant's
work, as though the tenant created them.

Filter server-side:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$LIBRA_OS_URL/api/agents?source=custom"
```

`source` accepts `custom` or `preset`. Omit it to get both.

**An unrecognised value is rejected, not ignored.** `?source=everything`
returns `400 invalid_source` rather than quietly returning every agent —
a filter that silently widens its result set is how a preset ends up on a
tenant's page.

**An unrecognised parameter is reported.** `?owner=me` returns 200 with:

```json
{
  "agents": [ ... ],
  "warnings": ["ignored unknown query parameter \"owner\""]
}
```

The list is unfiltered in that case. A parameter that is accepted, ignored, and
still returns 200 is indistinguishable from one that worked, so the response
says which happened.

## What an agent will actually run on

Three fields, and they answer different questions:

```json
{
  "model_override": "anthropic/claude-sonnet-5",
  "model": "anthropic/claude-sonnet-5",
  "model_source": "agent"
}
```

- **`model_override`** — the model pinned in the agent's own definition. Empty
  when the agent pins nothing, which is the case for **every bundled preset**.
- **`model`** — the **effective** model: what the agent will run on, whether
  pinned or inherited.
- **`model_source`** — `agent` when pinned, `server_default` when inherited.

A preset therefore looks like this:

```json
{
  "model": "Qwen/Qwen3.6-35B-A3B",
  "model_source": "server_default"
}
```

Read `model` when you want to show what an agent runs on. Read
`model_override` only when you specifically care whether it was pinned.

### When the model is absent

Both `model` and `model_source` are **omitted** when the effective model cannot
be determined — an agent that pins nothing on a deployment with no server
default configured.

This is deliberate. A deployment can override the default in its settings
store, so reporting a guess would be confidently wrong, and a wrong answer to
"what will this run on" is worse than no answer. Render an absent `model` as
unknown rather than substituting a default of your own.

## Other fields worth knowing

- **`source_path`** — where the definition was loaded from. A runtime file
  overriding a preset id reports `source: custom`, because the runtime file is
  what executes.
- **`editable`** — `false` means the agent is an orphan, not in a managed pack
  directory.
- **`disabled`** — hidden from the model list while staying reachable by
  explicit id.
- **`loaded_skills`** — the *tool packs* the agent has loaded. If your product
  has its own notion of "skills", these are not the same thing.

## Full schema

Both endpoints are in the published OpenAPI contract
([`libra-os-partner.v1.yaml`](https://github.com/libraos/sdk/blob/main/openapi/libra-os-partner.v1.yaml)),
under `listRegistryAgents` and the `RegistryAgent` schema. That is the
authority for field-level detail; this page covers which endpoint to call and
why.
