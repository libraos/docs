---
slug: /
sidebar_position: 1
title: Introduction
description: Build applications on Libra OS — understand the runtime, create an agent, connect knowledge and tools, and operate your deployment.
---

# Build on Libra OS

Your knowledge. Your infrastructure. Your digital workforce.

Libra OS is a runtime for applications that use agents, enterprise knowledge,
and tools. Your application supplies the user experience and business logic;
Libra OS runs agents and provides model routing, retrieval, persistence, and
governance features.

You can use the Python SDK, native HTTP APIs, or compatible model APIs.
[Libra Desk](/desk) is one application built on this runtime; you can build
your own without adopting Desk's interface or workflow.

## Start with a working agent

1. **Run the server:** [Getting started](/getting-started) covers installation,
   a database, model configuration, authentication, and a first request.
   [Cloud](/cloud) is available through private-beta onboarding.
2. **Create an agent:** [Create your first agent](/creating-an-agent) shows a
   complete Python example with a prompt and a response you can print.
3. **Choose an interface:** [Calling agents](/calling-agents) maps each endpoint
   to its agent selector, request shape, and response format.
4. **Add context and actions:** bind [knowledge collections](/workspaces-memory),
   configure [tools](/employee-yaml#skills-and-tools), and choose the
   [memory](/managing-memory) your application needs.
5. **Operate it:** inspect [available agents](/listing-agents), run
   [background tasks](/durable-runs), and check [deployment](/deployment)
   and [portability](/portability) requirements.

## Understand the objects

| Object | Developer responsibility |
| --- | --- |
| **Application** | Calls the runtime, authenticates users, and presents results or review decisions. |
| **Employee** | An optional identity record that groups agents and supplies shared configuration. It does not execute a prompt. |
| **Agent** | The executable behavior: instructions, tools, model settings, and knowledge bindings. Applications invoke an agent by ID. |
| **Skill / tool** | A delegated behavior or callable operation available to an agent. See [the distinction](/agents#core-concepts). |
| **Knowledge collection / Pack** | Documents available for retrieval, or a distributable package of knowledge and configuration. Bind the installed collections to agents. |

One employee can own several agents through their `owner_employee` field.
An agent can also run independently. Creating an employee does not create an
agent, choose a default agent, or make all its agents share conversation memory.
See [Employees and agents in YAML](/employee-yaml) for a complete linked example.

Setup-generated agents and optional templates are starting points you can edit.
The tutorials create their own agents and do not depend on a fixed set of
pre-installed employees; bundled agents vary by release and deployment.

## Know where processing happens

Self-hosting controls where the runtime and its stores run. Hosted models,
embedding services, web search, and tool callbacks can still receive data.
For an offline deployment, configure local models and embeddings and check
each tool's dependencies. [Security](/security) explains the boundaries;
[portability](/portability) explains which capabilities depend on the environment.

## Worked integrations

- [Customer support](/guides/customer-support): ground answers in product docs,
  connect order and ticket tools, and handle escalation.
- [Ticket routing](/guides/ticket-routing): classify tickets into structured
  outputs and let your application select a queue.
- [Libra Desk](/desk): see how a complete application combines agents,
  connectors, approval queues, and an audit trail.

These docs describe interfaces and configuration. Check the capabilities of
your installed server and SDK versions before relying on a recently added field.
