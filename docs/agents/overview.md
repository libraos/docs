---
slug: /agents
sidebar_position: 1
title: Agents overview
description: The Libra OS agent runtime — employees, agents, skills, and the planner; what the runtime does for you and when to use it over a raw model call.
---

# Agents on Libra OS

A pre-built, supervised agent runtime that runs inside **your** deployment.
Best for grounded, auditable work over your own documents.

There are two ways to build with Libra OS, each suited to different use cases:

|                | Compatible APIs | Agent runtime |
| -------------- | --------------- | ------------- |
| **What it is** | Your existing agent code, pointed at your deployment | Pre-built agent harness: employees, agents, skills, and the planner |
| **Best for**   | Getting running in an afternoon with tooling you already use | Multi-turn digital employees with memory, grounding, and supervision |
| **Learn more** | [Anthropic-compat section](/creating-an-agent#already-building-agents-with-anthropics-tooling) of the tutorial | This page, then [Create your first agent](/creating-an-agent) |

The agent runtime provides the harness for running models as autonomous,
supervised agents. Instead of building your own agent loop, tool execution,
memory store, and review workflow, you define an employee and an agent — two
records — and the runtime handles planning, skill delegation, model routing
with fallbacks, per-user memory, and the AI firewall on every request in and
out. Nothing leaves your network.

:::note

The runtime is identical on **Libra OS Cloud** and **Self-Hosted** — same
binary, same APIs, no migration between them. See
[Cloud vs Self-Hosted](/editions).

:::

**Start here:**

- **[Create your first agent](/creating-an-agent)** — a working agent in three SDK calls
- **[Defining employees in YAML](/employee-yaml)** — the declarative file format and full field reference
- **[Customer support agent](/guides/customer-support)** — the most common deployment, from template to production

## Core concepts

The agent runtime is built around five concepts:

| Concept | Description |
| --- | --- |
| **Employee** | The durable identity — display name, model configuration, and the knowledge and memory that accumulate around it. One employee can own several agents |
| **Agent** | A runnable behavior bound to an employee: `skill` handles a single delegated call, `persona` holds a multi-turn conversation. Its Markdown body is the system prompt |
| **Skill** | A sub-agent an agent can delegate to — each runs with its own prompt and model slot, dispatched by the planner |
| **Planner** | The decomposition tier. With `brain: true`, it breaks a task across the agent's skills and routes each piece to the model that fits |
| **Memory** | Conversation state, keyed automatically on the (API key, end user, agent) triple — there is no session object to create or manage |

## How it works

1. **Create an employee.** Define the identity, `model_config` (per routing
   tier, with fallback chains), and shared defaults its agents inherit — via
   [SDK call](/creating-an-agent) or a
   [declarative file](/employee-yaml) in `data/employees/`.

2. **Create an agent.** Bind it to the employee, choose `skill` or `persona`,
   write its instructions, and attach skills, tools, and knowledge bindings.

3. **Send a message.** `messages.create(agent_id=...)` — pass the
   `X-End-User` header to scope memory per end user. No session or environment
   object to manage; send another message any time and the agent picks up
   where it left off.

4. **The runtime runs the loop.** The planner decomposes the task, skills and
   tools execute, models resolve per slot through the fallback cascade, and
   the AI firewall screens every request on the way in and out — source
   grounding, PII redaction, prompt-injection screening. Answers cite where
   they came from.

5. **Supervise and steer.** High-risk tool calls route to
   [approval groups](/employee-yaml#visibility-and-ux) before they execute; an
   instant hard-stop freezes any agent mid-task; and the review trail becomes
   your compliance record.

## When to use the agent runtime

The agent runtime is best for workloads that need:

- **Grounded answers:** retrieval over your own documents via
  `knowledge_bindings`, with citations on every answer and a confidence gate
  below which the planner is consulted before answering from thin evidence
- **Multi-turn assistants:** persona agents with per-user memory that persists
  across conversations without session bookkeeping
- **Delegated pipelines:** a planner decomposing work across skills, each
  routed to the model — frontier or local — that fits the step
- **Structured output:** a JSON Schema contract on the agent's answers, with
  `error`, `log`, or `repair` on violation
- **Human review:** approval queues on risky actions, per-tool risk tiers,
  and a hard-stop — supervision as part of the runtime, not an add-on
- **Minimal infrastructure:** no agent loop, memory store, tool-execution
  layer, or review UI to build

## Built-in tools

Agents get access to a set of built-in tools, all opt-in per agent:

- **Knowledge base lookup:** graph and vector hybrid search over the
  collections the agent is bound to, citations included
- **Filesystem:** set `filesystem.enabled: true` and six filesystem tools
  register automatically against a provisioned workspace — no container
  plumbing
- **Web search:** backend, fallback chain, and recency-intent escalation via
  `web_search_config`, cascading agent → employee → server default
- **Custom tools:** partner-defined tools with JSON Schema inputs — delivered
  inline over SSE or to a webhook you host, with per-tool risk tiers that
  gate the approval path
- **Skills:** any skill in the catalog, attached with one line of frontmatter

See the [agent field reference](/employee-yaml#agent-field-reference) for the
full list and configuration options.

## State and data

The runtime is stateful by design: memory, knowledge indexes, workspaces, and
the audit trail persist across conversations — and all of it lives inside your
deployment. On Self-Hosted, that means your own network, down to fully
air-gapped; on Libra OS Cloud, a dedicated environment you can export from and
[move to Self-Hosted](/editions) without migration. Either way, model traffic
goes only to the providers you configure, and the review trail doubles as
your compliance record.

## Next steps

- **[Create your first agent](/creating-an-agent)** — employee, agent, first message
- **[Defining employees in YAML](/employee-yaml)** — every field, grouped by what it controls
- **[Model settings](/model-settings)** — routing tiers, fallback chains, covered and local models
- **[Core capabilities](/capabilities)** — the kernel, firewall, and knowledge base underneath
- **[Security](/security)** — the AI firewall and the sovereignty story in depth
