---
slug: /listing-agents
sidebar_position: 5
title: Listing agents
description: Choose the managed-agent API or operator registry, distinguish definition sources, and inspect available agents.
---

# Listing agents

Two endpoints return agents. They are deliberately different, and picking the
wrong one is the most common mistake when building an admin surface — because
the difference is not obvious from the names.

| | `GET /v1/agents` | `GET /api/agents` |
| --- | --- | --- |
| purpose | managed agents, for applications | the loaded registry, for operators |
| auth | authorized credential + managed-agent beta header | **admin only** |
| distinguishes definition source | no `source` field | `source: custom \| preset` (not ownership) |
| tells you what an agent runs on | `model` | `model`, `model_override`, `model_source` |

If you are **building an application**, use `/v1/agents`.
If you are **building an admin page over the registry**, use `/api/agents`.
For direct HTTP calls to the former, include
`anthropic-beta: managed-agents-2026-04-01`; the Python SDK adds it.
Neither response lists employee identity records. See [Calling agents](/calling-agents)
to invoke an ID you discover.

## The mistake worth avoiding

Depending on release and configuration, the registry can include bundled
agents, tool agents, setup-generated agents, and definitions created by API.
Do not hardcode their names or assume a fixed number of employees. An unfiltered
operator list can mix built-in behavior with application-created agents.

Filter server-side:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$LIBRA_OS_URL/api/agents?source=custom"
```

`source` accepts `custom` or `preset`. Omit it to get both.

This is a **definition-location** classification: runtime-directory entries are
`custom`; definitions outside it are classified as `preset`. A hand-authored
file can therefore report `preset`. The filter does not establish who owns an
agent, which tenant it belongs to, or what a caller is allowed to invoke.

**An unrecognised value is rejected, not ignored.** `?source=everything`
returns `400 invalid_source` rather than quietly returning every agent —
a filter that silently widens its result set is how a preset ends up on a
tenant's page.

**An unrecognised parameter is reported.** `?owner=me` returns 200 with:

```json
{
  "agents": [],
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

Read `model` for the registry's reported model and `model_override` for the
explicit legacy pin. This summary is not a trace of all resolved model slots:
an employee's `model_config`, a planner/skill tier, or a per-call override can
require inspecting the definition and execution record.

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

The published OpenAPI contract
([`libra-os-partner.v1.yaml`](https://github.com/libraos/sdk/blob/main/openapi/libra-os-partner.v1.yaml))
describes the APIs. `listRegistryAgents` and `RegistryAgent` describe the
operator registry, not the managed-agent response. That is the
authority for field-level detail; this page covers which endpoint to call and
why.
