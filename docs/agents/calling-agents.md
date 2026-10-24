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
answer cited nothing.

### Continuing a conversation

Save the returned `conversation_id` and send it with the next `message` to
continue that thread:

```json
{
  "conversation_id": "chat_1786552728460381358",
  "message": "Translate that into French."
}
```

The model then sees the thread's earlier user and assistant turns in front of
the new message. Only the newest turns that fit a token budget are sent; older
turns are dropped whole, never cut in half. The budget is an operator setting,
`LIBRA_OS_CONVERSATION_REPLAY_MAX_TOKENS` (default `8000`; `0` turns replay
off). Only a conversation the caller owns is continued; another user's
conversation ID is refused with `404`.

If you send `messages[]` instead of `message`, you are supplying the history
yourself and nothing stored is added. Use one approach or the other.

When the request names a conversation, the response carries
`history_replayed`: the number of earlier user and assistant messages that were
added (`0` on a first turn, a `messages[]` request, or with replay off). The
field is absent when the request names no conversation. Streaming turns carry
it on the final `done` event.

Optional request fields for backends that assemble their own prompts:

| Field | Type | Effect |
| --- | --- | --- |
| `retrieval_query` | string | What to search the knowledge base for, when that differs from the message. Empty or absent: the query is derived from the message. |
| `no_tools` | boolean | Run the turn with no tools attached, even when the agent declares direct tools. Knowledge retrieval before the turn still runs. |
| `no_memory` | boolean | Observational memory is neither read nor written on this turn. |
| `no_retrieval` | boolean | No knowledge-base retrieval on this turn: no excerpts are added before the turn, the knowledge search tool is not offered, and the automatic search before saying "not found" does not run. Attachments sent in the conversation can still be read. |

Without `retrieval_query`, a long or multi-line message is reduced to one line
for search, normally its last line. If your backend sends a ticket followed by
instructions, that last line is an instruction and retrieval can come back
empty. Set `retrieval_query` to the question you want answered from the
knowledge base:

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
the relevant impersonation capability. Never treat an employee ownership link
or a client-supplied ID as a grant of access.

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
