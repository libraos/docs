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
`response`, `agent_id`, `conversation_id`, `retrieved_chunks`, and `grounding`.
Save the returned `conversation_id` and send it with subsequent native turns
to continue that thread.

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
