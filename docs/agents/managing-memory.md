---
slug: /managing-memory
sidebar_position: 7
title: Managing memory
description: Choose conversation history, observations, persisted fields, or an employee house profile, and understand their identity scopes.
---

# Managing memory

[Workspaces & memory](/workspaces-memory) explains *where* your company's
context lives. This page is the operator's half: what actually persists, who
it belongs to, and how to control each piece.

Four different things persist, and they are worth keeping straight — they have
different lifetimes, different scopes, and different switches.

| What | Lifetime | Scoped to |
| --- | --- | --- |
| **Conversation** | Stored according to the conversation store's retention | Authorized caller + `conversation_id` |
| **Observational memory** | Until removed or handled by configured retention | Resolved caller identity + agent + applicable context scope |
| **Persisted fields** | Until reset or removed | Session, or resolved person + agent |
| **House profile** | Until updated or removed | Employee and applicable corporate context |

Knowledge collections are deliberately not in this table. They are documents
you put there on purpose — see [Workspaces & memory](/workspaces-memory).

## Conversation threads

For native chat, save the returned `conversation_id` and pass it on the next
turn under the same authorized identity:

```json
{
  "conversation_id": "case-4471",
  "message": "What information is still missing?"
}
```

This body belongs to `/agents/v1/{agent}/chat`. For `/v1/messages`, send the
`messages` array; a stable `conversation_id` (also accepted in metadata) opts
into conversation persistence. The Python SDK can pass
`metadata={"conversation_id": "case-4471"}`. Explicitly sending the required
history is the portable approach across compatible clients.

A thread ID does not grant access to another user's conversation. Ending a
thread does not erase its stored transcript. Conversation history and extracted
observations are separate stores; see [Calling agents](/calling-agents).

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

Observation and reflection run as background work. Facts may not be available
immediately after a turn. Choose a model that can extract accurate facts at your
expected volume; stored observations may influence later decisions.

### Who the memory belongs to

The server resolves memory identity from the authenticated caller, the agent,
and the endpoint's context. Storage includes legacy platform/end-user/agent
keys and canonical authenticated-user identity. It is not accurately described
as one universal `(API key, end user, agent)` key.

For normal signed-in users, the authenticated identity is authoritative.
`X-End-User` and `X-Canonical-User` overrides are honored only for callers with
the deployment's impersonation capability. An authorized backend can supply
those selectors; an arbitrary browser header cannot grant that authority.
`X-Platform-User` is a legacy memory selector, not a tenant authorization claim.

A shared service credential does not by itself distinguish your customers.
Have the operator configure and verify the supported end-user mapping, then
test two users across two conversations before enabling long-term memory.
Do not assume that adding only `X-End-User` establishes every required identity
axis: canonical identity can also affect which observations are read.

Different agents keep distinct observation scopes. Personal/corporate context
separation, where enabled, adds another boundary. Sharing `owner_employee`
does not merge the agents' observations.

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
`end_user_agent` keeps them for that resolved person and agent until they are
reset or removed. The example is a configuration fragment: define the matching
output schema too, so `collected_params` is part of the agent's validated output.

Use this instead of observational memory when the thing you need is a specific
slot rather than a general impression. It is deterministic — a field is set or
it is not — which matters when the value drives a decision.

## House profile

A per-employee markdown document — playbook, house style, escalation rules —
available to agents through their employee association. It is how a firm's
operating instructions reach agents without editing each prompt. When dual
personal/corporate scopes are enabled, house-profile injection applies in
corporate context; personal context omits it. This is separate from the
employee file's descriptive Markdown body.

```text
GET  /v1/managed/employees/{id}/house-profile
PUT  /v1/managed/employees/{id}/house-profile
```

No profile means no injection and no behaviour change. It is capped at 8 KB;
it is meant to be read and edited by a person, so keep it short enough that
someone will.

## Retention and deletion

Disabling observational memory stops its use; it is not a deletion request.
Conversation transcripts, observation logs, structured fields, house profiles,
job results, and backups are separate data sets. Confirm the deletion mechanism
and identity scope for each store in your installed release before promising
that one operation removes all of a person's data.

## Choosing between them

- The user asks a follow-up question → **conversation thread**
- The agent should recall this person's situation next month → **observational
  memory**
- You need a specific value to survive, exactly → **persisted fields**
- Everyone's agents should follow the same house rules → **house profile**
- The knowledge is documents → not memory at all, use
  [collections](/workspaces-memory)

## What leaves the deployment

The observation logs, persisted values, and house profile are stored in your
deployment. Their contents can enter model prompts. The worker model sees turn content in order to
summarize it, so if that tier is a hosted model, the summarization prompt goes
where that model runs — point `LIBRA_OS_MEMORY_WORKER_MODEL` at a local model
if that matters to you. See the [security model](/security) and
[Local models](/model-settings#local-models).
