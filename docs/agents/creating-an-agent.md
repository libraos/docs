---
slug: /creating-an-agent
sidebar_position: 2
title: Create your first agent
description: Create an executable agent with the Python SDK, send a message, and read the response.
---

# Create your first agent

This tutorial creates a standalone persona agent and sends it a message.
An employee record is optional. Add one when several agents need shared
configuration; see [Employees and agents in YAML](/employee-yaml).

## Prerequisites

- A running server with working model settings: [Getting started](/getting-started).
- Python 3.10 or newer and `pip install libraos-sdk`.
- A credential authorized to create and invoke agents. The SDK's `api_key`
  parameter accepts the bearer token issued by your deployment.

```bash
export LIBRA_OS_URL=http://localhost:8900
export LIBRA_OS_API_KEY='your-bearer-token'
```

The SDK source and examples are in [libraos/sdk](https://github.com/libraos/sdk).

## Create and call

Save as `first_agent.py`:

```python
import asyncio
import os

from libraos import Client


async def main() -> None:
    async with Client(
        base_url=os.environ["LIBRA_OS_URL"],
        api_key=os.environ["LIBRA_OS_API_KEY"],
    ) as client:
        agent = await client.agents.create(
            name="my-first-agent",
            agent_type="persona",
            system="You are a helpful assistant. Answer concisely.",
        )
        agent_id = agent["id"]
        response = await client.messages.create(
            agent_id=agent_id,
            messages=[{"role": "user", "content": "What are you good at?"}],
        )
        print(response.text)


asyncio.run(main())
```

```bash
python first_agent.py
```

The first call creates the definition; the second invokes it. The model is
omitted so the agent uses your server's configured default. No documents or
tools are attached yet, so this is a basic model answer, not a knowledge-grounded
answer. Exact wording varies by model.

Save the returned agent ID in your application. On subsequent runs, call that
ID without creating it again; creating the same name again can return a conflict.

The prompt field for this API is **`system`**. The SDK also accepts
`system_prompt` as an alias. `instructions` is not the supported field.

## Continue the conversation

For a client-managed conversation, retain the messages and append both sides:

```python
history = [{"role": "user", "content": "My project is called Atlas."}]
response = await client.messages.create(agent_id=agent_id, messages=history)
history.append({"role": "assistant", "content": response.text})
history.append({"role": "user", "content": "What is my project called?"})
response = await client.messages.create(agent_id=agent_id, messages=history)
```

This fragment runs inside the async client context above. Reusing an agent ID
alone does not resend previous turns. For server-stored threads and longer-lived
facts, see [Managing memory](/managing-memory).

`response["content"]` is an array of content blocks. `response.text` joins text
blocks for display; preserve the full response when your application needs
tool blocks or metadata. [Calling agents](/calling-agents) compares the wire formats.

## Add an employee when you need shared defaults

Use `data/employees/frontdesk.md` for the employee and set
`owner_employee: frontdesk` in an agent's Markdown frontmatter. The
[YAML guide](/employee-yaml) shows both files and the call that runs the agent.

The current managed-agent create/update handler supports a subset of the file
schema. In particular, do not assume that passing `owner_employee`,
`model_config`, or `callback` through `agents.create(**fields)` applies those
settings: the inspected handler does not persist them. Use the file-based path
for those fields and check your installed release's API contract.

## Add knowledge and tools

- Bind a [knowledge collection](/workspaces-memory) to retrieve from your documents.
- Configure [custom tools](/employee-yaml#skills-and-tools) to call your application.
- Enable [web search](/web-search) when the deployment has a search backend.
- Use [background tasks](/durable-runs) when a request should outlive its connection.

The [customer support guide](/guides/customer-support) combines these pieces.

## Already building agents with Anthropic's tooling?

The Messages-compatible endpoint accepts requests at `/v1/messages`.
Select the registered agent with `metadata.agent_id`; the `model` field has
a separate role. See the exact request in [Calling agents](/calling-agents).

The SDK also exposes managed-agent APIs. Direct HTTP callers need the
`anthropic-beta: managed-agents-2026-04-01` header on `/v1/agents`; the Libra OS
SDK supplies it automatically. Compatibility is limited to the fields and
behaviors implemented by your server release.

For integrations, see the SDK's
[compatibility reference](https://github.com/libraos/sdk/blob/main/docs/anthropic-compat.md)
and [examples](https://github.com/libraos/sdk/tree/main/python/examples).
