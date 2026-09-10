---
slug: /build-on-libraos
sidebar_position: 6
title: Build on Libra OS
description: The SDK, the API contract and the CLI — what a developer installs, what is generated from the spec, and what to reach for first.
---

# Build on Libra OS

Everything the product does is reachable over HTTP, and everything in this
guide is something an application can do without a change to the server. This
page is the entry point for building one.

## The SDK

```bash
pip install libraos-sdk
```

The Python SDK is **Anthropic Managed Agents compatible**, so code written
against that shape works here, with LibraOS's multi-model routing and employee
features available on top. Point it at a deployment:

```bash
export LIBRA_OS_URL=https://your-deployment
export LIBRA_OS_API_KEY=...
```

Source, examples and the partner integration docs:
**[github.com/libraos/sdk](https://github.com/libraos/sdk)**

## The API contract

The SDK is generated from a published OpenAPI specification, and so is
everything else — the Go client, the TypeScript types, the CLI. If you would
rather call the API directly, or generate a client for a language we do not
ship, the spec is the authority:

**[`openapi/libra-os-partner.v1.yaml`](https://github.com/libraos/sdk/blob/main/openapi/libra-os-partner.v1.yaml)**

It is worth reading even if you use the SDK, because it is where response
fields are defined — including the ones that tell you whether an answer can be
trusted. `grounding`, `retrieved_chunks` and `citations_verified` are described
in [Workspaces & memory](/workspaces-memory) and [Web search](/web-search); the
spec is where their exact values live.

## What is available today

| | status |
| --- | --- |
| **Python** — `pip install libraos-sdk` | published |
| **OpenAPI spec** | published, the source of truth |
| **CLI** | in the SDK repo |
| **TypeScript client** | **in the repo, not published to npm** — clone and build from `clients/typescript` |
| **Go client** | in the repo under `cli/internal/client` |

The TypeScript client is generated and tested but has no npm release yet. Use
it from a checkout rather than expecting `npm install` to work.

## Worked examples

The SDK repository carries runnable examples rather than snippets:

- **[`examples/simulator`](https://github.com/libraos/sdk/tree/main/examples/simulator)**
  — a synthetic-customer simulator for exercising an agent against generated
  conversations
- **[`examples/react-ui-demo`](https://github.com/libraos/sdk/tree/main/examples/react-ui-demo)**
  — a front end talking to a deployment
- **[`employees/`](https://github.com/libraos/sdk/tree/main/employees)** —
  employee definitions you can install and adapt, including the
  `email-classifier` used in [Ticket routing](/guides/ticket-routing)

Two end-to-end guides walk the whole path:
[Customer support](/guides/customer-support) and [Ticket routing](/guides/ticket-routing).

## What the platform handles for you

Worth knowing before you build around it, because these are not things an
application needs to implement:

- **Grounding and citation checking** — every answer carries a verdict; you
  read it rather than compute it
- **The AI firewall** — inbound and outbound screening on every turn
- **Agent orchestration** — planning, parallel skill execution, circuit
  breakers and per-stage deadlines
- **Knowledge retrieval** — collections, bindings and scope enforcement
- **Approval workflow** — the dry-run and pending-action gate for
  side-effecting tools

An application decides *what* to ask for and *what to do with the answer*.
Retrieval, safety and orchestration are the platform's job.

## Before you go to production

- [Portability contract](/portability) — what behaves identically across
  deployment shapes and what degrades. Read this before assuming a capability
  is present.
- [Security model](/security) — what leaves the deployment.
- [Managing memory](/managing-memory) — what persists, and how to scope it to
  the right person.

## Where to go next

- [Getting started](/getting-started) — a running deployment in about six
  minutes
- [Creating an agent](/creating-an-agent) — your first agent
- [Employee YAML](/employee-yaml) — the definition format
