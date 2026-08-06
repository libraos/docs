---
slug: /creating-an-agent
sidebar_position: 2
title: Create your first agent
description: Go from zero to a working agent on Libra OS in three SDK calls — create an employee, attach a skill agent, and talk to it.
---

# Create your first agent

An agent is an application that completes a task by planning its own steps and
calling tools. On Libra OS, agents run inside **your** deployment — grounded in
your documents, screened by the AI firewall, with nothing leaving your network.

**What you'll do:**

1. Set up a project with the Libra OS SDK
2. Create a digital employee and attach an agent to it
3. Send the agent its first message

Total surface from nothing to a working agent: **three SDK calls**.

## Prerequisites

- A running Libra OS deployment — see [Getting started](/getting-started) to
  install one locally (a laptop is fine for this tutorial)
- **Python 3.10+**
- A Libra OS API key (`msk_...`)

## Setup

**1. Install the SDK:**

```bash
pip install libraos-sdk
```

The SDK source, OpenAPI spec, and worked examples live at
[github.com/libraos/sdk](https://github.com/libraos/sdk).

**2. Point it at your deployment:**

```bash
export LIBRA_OS_URL=https://libraos.your-company.example   # or http://localhost:8900
export LIBRA_OS_API_KEY=msk_live_...
```

(The legacy `NOVA_OS_*` names still work — the server bridges them — but
`LIBRA_OS_*` is canonical.)

## Build the agent

Create `first_agent.py`:

```python
import asyncio
import os

from libraos import Client


async def main() -> None:
    base_url = os.environ["LIBRA_OS_URL"]
    api_key = os.environ["LIBRA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create the employee — the identity that owns one or more agents.
        #    model_config picks the model per routing tier, with fallbacks.
        await c.employees.create(
            id="my-first-employee",
            display_name="My First Employee",
            model_config={
                "answer": {
                    "primary": "anthropic/claude-opus-4-7",
                    "fallback": ["gemini/gemini-2.5-flash"],
                }
            },
        )

        # 2. Create the agent — the runnable behavior bound to that employee.
        #    "type" tells the registry what loop to run:
        #    skill = single-call, persona = multi-turn.
        await c.agents.create(
            id="my-first-agent",
            type="skill",
            owner_employee="my-first-employee",
            instructions="You are a helpful assistant. Answer concisely.",
        )

        # 3. Talk to it. No session object needed — memory is keyed on the
        #    (API key, end user, agent) triple automatically.
        resp = await c.messages.create(
            agent_id="my-first-agent",
            messages=[{"role": "user", "content": "What are you good at?"}],
        )
        print(resp)


asyncio.run(main())
```

This code has three parts:

1. **`employees.create`** — the employee is the durable identity: display
   name, model configuration, and (as it grows) the knowledge and memory that
   accumulate around it. One employee can own several agents.
2. **`agents.create`** — the agent is the runnable behavior. A `skill` agent
   handles a single delegated call; a `persona` agent holds a multi-turn
   conversation. `instructions` is the agent's system prompt.
3. **`messages.create`** — sends work to the agent. There is no session or
   environment object to manage: send another `messages.create()` at any time,
   and pass the `X-End-User` header to scope memory per end user (omit it for
   a single shared scope, which is fine while evaluating).

### Run it

```bash
python first_agent.py
```

The agent answers through the model tiers you configured, and the response —
like every Libra OS answer — passes the AI firewall on the way in and out.
This script is
[`00_quickstart.py`](https://github.com/libraos/sdk/blob/main/python/examples/00_quickstart.py)
in the SDK repo, which also shows the optional cleanup calls
(`agents.delete` / `employees.delete`) for idempotent dev loops.

## Customize your agent

**Give it tools.** Add `filesystem.enabled: true` to the agent's frontmatter
and six filesystem tools register automatically — no container plumbing.
Register your own tools with `custom_tools`: Mode A delivers tool calls inline
over SSE; Mode B calls a webhook you host.

**Control the models.** `model_config` works per tier (answer / skill / brain /
memory worker) with fallback chains, and cascades per-call → per-skill →
per-agent → per-employee → server default. If your deployment runs on a token
plan, use the covered model ids — see
[Model settings](/model-settings).

**Enforce output shape.** Set `output_type` to a JSON Schema and choose what
happens on violation: `error`, `log`, or `repair`.

**Search the web.** `web_search_config` selects the search backend, fallback
chain, and recency-intent escalation.

**Ship it to another deployment.** Employees are portable — export the bundle
(agents, prompts, config) and import it elsewhere.

Worked end-to-end integrations — legaltech, healthcare, finance — are in the
SDK repo's [`examples/`](https://github.com/libraos/sdk/tree/main/examples)
directory.

## Already building agents with Anthropic's tooling?

Your existing code runs against Libra OS without a rewrite:

- **Anthropic Messages SDK** — `anthropic.Anthropic(base_url=<your Libra OS>)`.
  The Messages API and the Managed Agents beta endpoints (`/v1/agents`,
  `/v1/sessions`) work unchanged. See the
  [compat reference](https://github.com/libraos/sdk/blob/main/docs/anthropic-compat.md).
- **[Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)** —
  the SDK's bundled CLI inherits its environment, so
  `ClaudeAgentOptions(env={"ANTHROPIC_BASE_URL": <your Libra OS>, "ANTHROPIC_API_KEY": "msk_..."})`
  redirects the whole local agent loop (Read/Bash/Edit tools included) to your
  own runtime. See
  [`01b_claude_agent_sdk_drop_in.py`](https://github.com/libraos/sdk/blob/main/python/examples/01b_claude_agent_sdk_drop_in.py).

Use those to get running in an afternoon; graduate to the native surface above
when you want model tiers, output contracts, and custom tools.

## Next steps

- **[Defining employees in YAML](/employee-yaml)** — the declarative file format behind these SDK calls
- **[Model settings](/model-settings)** — routing tiers, billing, covered and local models
- **[Core capabilities](/capabilities)** — the kernel, firewall, and knowledge base your agent runs on
- **[SDK examples](https://github.com/libraos/sdk/tree/main/python/examples)** — every pattern above as a runnable script
