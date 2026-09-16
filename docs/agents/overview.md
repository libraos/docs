---
slug: /agents
sidebar_position: 1
title: Employees, agents, and tools
description: Understand what an employee owns, what an agent executes, and how applications invoke and compose them.
---

# Employees, agents, and tools

An **agent** executes work. An **employee** is an optional identity and shared
configuration record that owns agents. Your application sends work to an agent
ID; the employee record does not run an agent-selection or planning loop.

## Core concepts

| Concept | Purpose | Example |
| --- | --- | --- |
| **Employee** | Groups agents and supplies model, web-search, and callback defaults. | `frontdesk` owns intake and follow-up agents. |
| **Persona agent** | Runs a conversational agent loop using its instructions and available tools. | `intake` collects a customer's request. |
| **Skill agent** | Handles a focused invocation or delegated task. | A document classifier returns a category. |
| **Skill reference** | Configures a delegated skill or installed tool pack; the meaning depends on what that ID resolves to. | A research skill or a document tool pack. |
| **Tool** | A callable operation with defined inputs. A custom tool can call your webhook. | `lookup_order(order_id)` reads your order system. |
| **Planner** | When enabled with `brain: true`, decomposes a task and selects available skills. | Research a question, then draft a report. |
| **Knowledge collection** | Stores documents an agent can retrieve. | Product documentation bound to `intake`. |
| **Memory** | Stores conversation history, extracted facts, or structured values under their own scopes. | A thread ID or a customer's collected case number. |

In product copy, a conversational persona may be called a “digital employee.”
In YAML and APIs, distinguish that persona agent from the **employee record**.
In Desk's People screens, “employee” refers to a **human member**.

## How work reaches an agent

```text
Application → intake agent → available skills and tools → response
                   ↑
       defaults from employee frontdesk
```

1. Define an agent, optionally setting `owner_employee: frontdesk`.
2. Call the agent by ID, for example `messages.create(agent_id="intake", ...)`.
3. The runtime applies the agent's configuration and inherited defaults.
4. The agent uses its available tools; an enabled planner can delegate work.
5. Your application reads the response and any grounding, error, or approval
   information exposed by that API.

The ownership link does not automatically make sibling agents callable by one
another. Configure skills explicitly or have your application route between
agents. There is no employee-level `default_agent` selector in the current
employee schema.

## What inherits, and what does not

Models resolve **per slot**: agent → employee → server default. An agent can
override `answer` while inheriting `planner` and `skill`. Web-search defaults
and custom-tool callbacks also have their own cascades; see
[the YAML reference](/employee-yaml).

The agent keeps its own prompt, tools, knowledge bindings, access settings,
and execution limits. Employee ownership alone does not grant collection
access or merge its agents' memories. A separately configured
[house profile](/managing-memory#house-profile) can provide shared instructions.

## Choose your starting point

- **A first executable agent:** use the [SDK tutorial](/creating-an-agent).
  Start without an employee if you do not need shared configuration.
- **Several agents with employee defaults:** use
  [declarative Markdown files](/employee-yaml). File fields and managed API
  fields are not interchangeable; that page explains the current boundary.
- **An existing chat client:** use the compatible endpoint in
  [Calling agents](/calling-agents).
- **A longer task:** use the [native jobs API](/durable-runs) and retain its
  job ID for progress and results.

Persona agents still need conversation context. Pass message history or use
the thread mechanism supported by your endpoint. Long-term observational
memory is separately enabled; see [Managing memory](/managing-memory).
