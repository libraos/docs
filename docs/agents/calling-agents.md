---
slug: /calling-agents
sidebar_position: 3
title: Calling agents
description: Choose an API, select the correct agent, read the response format, and retain conversation context.
---

# Calling agents

Applications invoke an **agent ID**. An employee ID identifies shared
configuration; it is not a runnable route. Use an agent you created or one
your operator made available, and verify it with [Listing agents](/listing-agents).

## Choose the interface

| Interface | Agent selector | Text in a successful non-streaming response |
| --- | --- | --- |
| Python `client.messages.create(...)` | `agent_id="intake"` | `response.text` (SDK helper) |
| `POST /v1/messages` | `metadata.agent_id` | Text blocks in `content[]` |
| `POST /v1/chat/completions` | `model: "intake"` for a registered agent | `choices[0].message.content` |
| `POST /agents/v1/intake/chat` | Agent route ID in the path | `response` |
| `POST /agents/v1/intake/jobs` | Agent route ID in the path | Returns a job receipt; retrieve the result later |

These endpoints do not share one request or response schema. In particular,
the Python parameter `agent_id` becomes `metadata.agent_id` on the Messages
wire format. A top-level `agent_id` is not valid for `/v1/messages`.

## Messages-compatible request

Set `LIBRA_OS_URL` to your server URL and `LIBRA_OS_API_KEY` to an authorized
bearer credential. This example assumes an agent named `intake` already exists:

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/v1/messages" \
  -H "Authorization: Bearer $LIBRA_OS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "intake",
    "max_tokens": 500,
    "metadata": {"agent_id": "intake"},
    "messages": [{"role": "user", "content": "What can you help me with?"}]
  }'
```

Here `metadata.agent_id` selects the behavior and `model` repeats the agent
ID so its configured model can be used. A supported provider model ID in
`model` can instead override the answer model for that call; it does not select
the agent or change all planner/skill tiers. Omitting `metadata.agent_id`
selects the server's default agent, even if `model` looks like another agent ID.

To read text from the raw response:

```python
text = "".join(
    block.get("text", "")
    for block in response["content"]
    if block.get("type") == "text"
)
```

Keep non-text blocks when using tools. Do not parse the entire `content`
array as a string or discard tool results your application needs.

## Native chat request

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/agents/v1/intake/chat" \
  -H "Authorization: Bearer $LIBRA_OS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"message":"What can you help me with?"}'
```

Native chat uses `message` for a simple text turn and returns fields such as
`response`, `agent_id`, `conversation_id`, `retrieved_chunks`, `cited_sources`,
and `grounding`. `cited_sources` is always present: an empty list when the
answer cited nothing. A retrieved document counts as cited when the answer
names it by its source, its title, or its file name without the extension, with
dashes and underscores read as spaces: `shipping-policy.md` is cited by
"Shipping policy, clause 2.1" (whole phrase, any case; names shorter than 4
characters or made only of digits are not matched).

### Continuing a conversation

Save the returned `conversation_id` and send it with the next `message` to
continue that thread:

```json
{
  "conversation_id": "chat_4f1c9a0e7b2d4c6a8e3f5b1d9c7a2e60",
  "message": "Translate that into French."
}
```

The model then sees the thread's earlier user and assistant turns in front of
the new message. Only the newest turns that fit a token budget are sent; older
turns are dropped whole, never cut in half. The budget is an operator setting,
`LIBRA_OS_CONVERSATION_REPLAY_MAX_TOKENS` (default `8000`; `0` turns replay
off).

A conversation belongs to the caller who started it **and** to the agent it was
recorded with. A request that names another user's conversation, or a
conversation recorded with a different agent, is refused with the same `404`
before the turn runs, whether it sends `message` or `messages[]`. A
conversation continues only on the agent it was recorded with; an agent's
built-in tool loop counts as that agent, but a separately defined agent never
does, whatever its name. Conversations recorded before agents were tracked are
accepted on any agent, but nothing from them is replayed. When you send no
conversation ID, the one the server issues is random (`chat_` followed by 32
hex characters), so it cannot be guessed.

If you send `messages[]` instead of `message`, you are supplying the history
yourself and nothing stored is added. Use one approach or the other.

Replay re-sends each earlier `message` exactly as it was sent, including any
context your backend assembled into it. If you build each turn's `message`
from selected pages, operator guidance or drafting instructions, every later
turn gets those earlier assemblies back too, including pages the user has
since deselected and guidance meant for an earlier draft. Such a backend should
send the history it wants in `messages[]`, or set `"no_history": true` to skip
replay for that turn. The model then sees only the current message, and the
turn is still recorded in the conversation.

When the request names a conversation, the response carries two counts:

- `history_replayed`: the number of earlier user and assistant messages that
  were added (`0` on a first turn, a `messages[]` request, with
  `no_history: true`, or with replay off).
- `history_dropped`: the number of earlier messages left out because they did
  not fit the budget. A single turn larger than the whole budget is left out,
  not cut, so `history_replayed: 0` with `history_dropped` above `0` means the
  history exists but did not fit.

Both are absent when the request names no conversation. Streaming turns carry
them on the final `done` event.

Optional request fields for backends that assemble their own prompts:

| Field | Type | Effect |
| --- | --- | --- |
| `retrieval_query` | string | What to search the knowledge base for, when that differs from the message. Empty or absent: the query is derived from the message (see below). |
| `no_history` | boolean | Do not replay the conversation's earlier turns on this turn. The turn is still recorded. See [Continuing a conversation](#continuing-a-conversation). |
| `no_tools` | boolean | Run the turn with no tools attached, even when the agent declares direct tools. Knowledge retrieval before the turn still runs. |
| `no_memory` | boolean | Observational memory is neither read nor written on this turn. |
| `no_retrieval` | boolean | No knowledge-base retrieval on this turn: no excerpts are added before the turn, the knowledge search tool is not offered, and the automatic search before saying "not found" does not run. Attachments sent in the conversation can still be read. |

Without `retrieval_query`, a long or multi-line message is searched by one line
taken from it, normally its last line that is not an instruction. If that
search finds nothing, the full message is searched once. If your backend sends
a ticket followed by instructions, the line chosen may still be the wrong one,
and the full-message search is a blunter fallback. Set `retrieval_query` to the
question you want answered from the knowledge base; a query you supply is
searched as given and never replaced:

```json
{
  "message": "Ticket:\n...\n\nDraft a reply in our house style.",
  "retrieval_query": "Late delivery: can I get a refund for an order that arrived two weeks late?",
  "no_tools": true,
  "no_memory": true
}
```

Use `no_retrieval` when your backend puts all the context the answer may use
into the message and wants "this isn't covered" to come back as written. Without
it, an agent with bound collections searches them anyway: on a knowledge-bound
agent, a draft that says the material isn't there, written when no knowledge
search ran on that turn, is not returned. The runtime has the model search once
and then keeps whatever it answers. That is usually what you want, but it
overrides a caller that asked for an answer from its own pages only.

These fields exist only on native chat; `/v1/messages` and
`/v1/chat/completions` do not accept them.

Native chat responses (and the final `done` event of a streaming turn) also
carry these fields:

| Field | Meaning |
| --- | --- |
| `history_replayed` | Earlier messages replayed in front of this turn. Present when the request names a conversation. |
| `history_dropped` | Earlier messages left out by the replay budget. Present when the request names a conversation. |
| `retrieval.query` | The text the knowledge base was searched for on this turn. |
| `retrieval.query_source` | Where that text came from: `explicit` (your `retrieval_query`), `derived` (one line taken from the message), `full_message_fallback` (the derived line found nothing, so the full message was searched), or `message` (the message as sent). |
| `cited_sources` | Retrieved documents the answer cites, by source, title or file name. Always present; an empty list when nothing was cited. |
| `grounding` | How the answer relates to evidence. `retrieval_not_attempted` means no knowledge search ran on this turn, because the agent has no bound collections or the request set `no_retrieval`. |

`retrieval.query` and `retrieval.query_source` are omitted when no retrieval
ran. Read them when an answer says the material isn't there: they show what was
actually searched.

## Authentication, context, and memory

The credential identifies the caller and its permissions. A conversation ID
identifies a thread. An agent ID selects executable behavior. None substitutes
for another.

With the Python Messages API, sending message history explicitly is a portable
way to continue a conversation. For stored Messages threads, the server also
accepts `metadata.conversation_id`; use a stable, authorized ID and follow
the endpoint's history behavior. Observational memory is separately enabled
and identity-scoped. See [Managing memory](/managing-memory).

Backend integrations serving several people must use the deployment's
authorized identity mechanism. `X-End-User` is honored only for callers with
the relevant impersonation capability; see [API keys](#api-keys). Never treat
an employee ownership link or a client-supplied ID as a grant of access.

### API keys

An admin can mint two kinds of API key for backend integrations:

- **Agent keys**, `POST /api/agents/{id}/keys`, reach one agent's
  `/agents/v1/{agent}/...` routes.
- **Service keys**, `POST /api/service-keys`, are organization-wide keys for
  inference.

The key's secret is returned once, in the mint response; store it then.

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/api/agents/intake/keys" \
  -H "Authorization: Bearer $LIBRA_OS_ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ticket-backend",
    "owner_user_id": "<service-account user id>",
    "allow_impersonation": true
  }'
```

A key acts as its owner. By default it cannot act for anyone else:

- `allow_impersonation` (both endpoints, default `false`): only a key minted
  with `"allow_impersonation": true` **and** owned by an admin may set
  `X-End-User` or `X-Canonical-User` to act for other end users. A
  shared-credential backend that serves many people through one key needs it.
  Keys that existed before this option was added kept the capability. Key list
  responses show `allow_impersonation` for each key.
- `owner_user_id` (agent keys only): mint the key for another user, typically a
  service account, instead of the admin making the call. The user must exist,
  be active, and belong to the same organization (`404` otherwise, `400` when
  inactive). A key owned by a non-admin never impersonates, whatever its
  `allow_impersonation` says.

Your operator can narrow impersonation further by key type.

## Handle outcomes

| Outcome | What to check |
| --- | --- |
| `401` / `403` | Credential validity and permission for the endpoint, agent, and resource. |
| `404` | Correct route/agent ID and visibility; an upstream model can also be unavailable. |
| `409` creating an agent | The name may already exist; reuse or deliberately update the agent. |
| `426` on `/v1/agents` | Supply the managed-agent beta header or use the SDK. |
| Answer has no sources | Check knowledge bindings, ingestion, retrieval capabilities, and grounding metadata. |
| Tool action awaits approval | Follow the action's decision/execution status; a completed chat is not evidence that the action executed. |

For asynchronous progress, reconnect rules, and job statuses, use the
[background-task guide](/durable-runs).
