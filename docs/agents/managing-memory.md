---
slug: /managing-memory
sidebar_position: 6
title: Managing memory
description: The four things that persist across a conversation — and how to turn each on, scope it to the right person, inspect it, and switch it off.
---

# Managing memory

[Workspaces & memory](/workspaces-memory) explains *where* your company's
context lives. This page is the operator's half: what actually persists, who
it belongs to, and how to control each piece.

Four different things persist, and they are worth keeping straight — they have
different lifetimes, different scopes, and different switches.

| What | Lifetime | Scoped to |
| --- | --- | --- |
| **Conversation** | One thread | `conversation_id` |
| **Observational memory** | Indefinite | person + agent |
| **Persisted fields** | Indefinite | session, or person + agent |
| **House profile** | Indefinite | the employee who owns the agent |

Knowledge collections are deliberately not in this table. They are documents
you put there on purpose — see [Workspaces & memory](/workspaces-memory).

## Conversation threads

The simplest form. Pass a `conversation_id` and the turn continues that
thread; omit it and the turn stands alone.

```jsonc
{ "conversation_id": "case-4471", "messages": [ ... ] }
```

Nothing is inferred and nothing is extracted. When the thread ends, it ends.
If all you need is "remember what we just said," this is the whole feature.

## Observational memory

Off unless you turn it on:

```bash
LIBRA_OS_OBSERVATIONAL_MEMORY=1
```

With it on, the runtime watches work as it happens and extracts **durable
facts** — attributes, dates, decisions — into a per-person log, so a later
conversation can start from what is already known instead of re-reading every
transcript. This is not a transcript archive; it is a condensed set of things
worth remembering.

Two background workers keep it small. The **Observer** condenses recent turns
once they exceed a token threshold; the **Reflector** periodically dedupes and
rewrites the whole log:

```bash
LIBRA_OS_OBSERVER_THRESHOLD=8000      # condense after this many tokens
LIBRA_OS_REFLECTOR_THRESHOLD=32000    # dedupe after this many
LIBRA_OS_MEMORY_WORKER_MODEL=...      # a cheap model is the right choice here
```

Both run **after** the response is sent, so they never add latency to a turn.
Point the worker model at your cheap tier — this is high-volume, low-stakes
summarization, not reasoning.

### Who the memory belongs to

This is the part to get right before enabling it. Memory is scoped to a triple
of **platform user, end user, and agent**, taken from request headers:

```
X-Platform-User: acme-corp      # your tenant
X-End-User:      jane@acme.com  # the person
```

The agent is the one being addressed. Same person, different agent means a
different memory — an HR assistant does not accumulate what a support agent
learned.

If you send no identity headers, every caller shares one pool. On a
multi-person deployment that is almost never what you want, and it is the
single most common misconfiguration: one user's context surfacing in another
user's answers. **Set the headers before enabling memory, not after.**

Facts recognized as personal are routed to a per-person pool rather than the
shared one, so private context does not leak into team-visible memory.

### Turning it off

Remove `LIBRA_OS_OBSERVATIONAL_MEMORY` and restart. The runtime falls back to
retrieval over your collections, which is the pre-memory behaviour. Existing
logs are left in place and simply stop being read — the rollback is one
variable, and it is reversible.

## Persisted fields

When an agent needs to *collect* something across turns — a case number, a
policy id, a shipping address — declare it in the agent's YAML and the runtime
carries the values for you:

```yaml
output_type:
  schema_id: intake.v1
  persist_scope: end_user_agent      # or: session
  persist_fields:
    - path: collected_params.case_number
      merge: non_null_overwrite
    - path: collected_params.parties
      merge: append_unique
      max_length: 20
```

Each field names a **path** into the agent's structured output, plus how a new
value merges with the old one: overwrite when non-null, deep-merge, or append
to a list without duplicates.

Known values are injected into the next turn as a small system block, so the
model stops re-asking. `session` scope ties the values to one conversation;
`end_user_agent` keeps them for that person and agent indefinitely.

Use this instead of observational memory when the thing you need is a specific
slot rather than a general impression. It is deterministic — a field is set or
it is not — which matters when the value drives a decision.

## House profile

A per-employee markdown document — playbook, house style, escalation rules —
injected into **every agent that employee owns**. It is how a firm's way of
working reaches its agents without editing each one.

```bash
GET  /v1/managed/employees/{id}/house-profile
PUT  /v1/managed/employees/{id}/house-profile
```

No profile means no injection and no behaviour change. It is capped at 8 KB;
it is meant to be read and edited by a person, so keep it short enough that
someone will.

## Choosing between them

- The user asks a follow-up question → **conversation thread**
- The agent should recall this person's situation next month → **observational
  memory**
- You need a specific value to survive, exactly → **persisted fields**
- Everyone's agents should follow the same house rules → **house profile**
- The knowledge is documents → not memory at all, use
  [collections](/workspaces-memory)

## What leaves the deployment

Nothing here does. The observation logs, the persisted values and the house
profile live in your database. The worker model sees turn content in order to
summarize it, so if that tier is a hosted model, the summarization prompt goes
where that model runs — point `LIBRA_OS_MEMORY_WORKER_MODEL` at a local model
if that matters to you. See the [security model](/security) and
[Local models](/model-settings#local-models).
