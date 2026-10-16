---
slug: /cookbook
sidebar_position: 7
title: Cookbook & learning paths
description: Learn LibraOS step by step, explore individual Runtime capabilities, or run a complete application with explicit prerequisites and verification boundaries.
---

# Cookbook & learning paths

The [public Cookbook](https://github.com/libraos/cookbook) contains runnable
examples for adding LibraOS to your application. Choose a learning sequence,
a capability, or a complete app. Your application continues to own its business
records, authorization, and user experience.

## Learn Step by Step

Start with [local setup](https://github.com/libraos/cookbook/tree/main/get-started)
and the [shared Python environment and token setup](https://github.com/libraos/cookbook/blob/main/docs/recipe-setup.md).
The documented protocol-test environment uses Python 3.12 and SDK 2.0.0;
Mission Client and Console require Node 22.12 or newer.

| Level | Example | What to learn first |
| --- | --- | --- |
| L1 | [First Agent](https://github.com/libraos/cookbook/tree/main/get-started/01-first-agent) — Python, TypeScript or Bash | Running Runtime, model and credentials |
| L1 | [Ticket Routing](https://github.com/libraos/cookbook/tree/main/recipes/ticket-routing) — structured output | First Agent; Python |
| L2 · Knowledge | [Document Q&A](https://github.com/libraos/cookbook/tree/main/recipes/document-qa) | First Agent; document ingestion |
| L2 · Tools | [Order Lookup](https://github.com/libraos/cookbook/tree/main/recipes/tool-calling) | First Agent; signed callback service and agent definition |
| L2 · Memory | [Memory & User Isolation](https://github.com/libraos/cookbook/tree/main/recipes/memory-isolation) | First Agent; memory enabled; two ordinary users |
| L3 | [Customer Support](https://github.com/libraos/cookbook/tree/main/recipes/customer-support) | Knowledge, Tools and trusted user identity mapping |
| L3 | [Async Jobs & Recovery](https://github.com/libraos/cookbook/tree/main/recipes/async-jobs) | First Agent; PostgreSQL-backed jobs |
| L4 | [Personal Assistant](https://github.com/libraos/cookbook/tree/main/apps/personal-assistant) | Browser sign-in, Knowledge and Memory |
| L4 | [Marketing Team](https://github.com/libraos/cookbook/tree/main/apps/digital-marketing-team) and [Mission Console](https://github.com/libraos/cookbook/tree/main/apps/mission-console) | Native jobs and enabled mission workflows |

**L2 has independent branches.** You can learn Knowledge, Tools or Memory
without completing the other two. Customer Support combines knowledge, tools
and identity; cross-session recall is optional. Async Jobs is an independent
L3 branch. Difficulty reflects concepts and setup dependencies, not the industry
named in an example.

## Explore by Capability

Each example should demonstrate an outcome you can inspect and a failure or
boundary you can exercise. These are verification targets, not a claim that
every live check has already passed.

| Capability | Observable outcome | Failure or boundary |
| --- | --- | --- |
| First Agent | Create an agent and receive a reply | Invalid credentials; model unavailable |
| Structured output | Schema-valid result and separately measured label accuracy | Invalid schema; valid JSON with an incorrect label |
| Knowledge | An answer supported by the supplied documents | A missing policy is not invented |
| Tools | Order status with a signed callback receipt | Unknown order, bad signature, unavailable webhook |
| Memory | A recalls a unique preference in a new conversation | B cannot access A's conversation or recall the preference, including with forged identity headers |
| Async | Persist a recovery receipt and resume observation of the same job | Lost submit response, timeout, failure and cancellation races |
| Mission | Complete tasks and generate a report | Reconnection, replayed events, failed tasks and pending decisions |

An answer that looks like an order status does not prove a tool executed.
Check the callback receipt. Likewise, a failed memory lookup does not prove
isolation: verify that A can recall the preference and read the conversation
before checking B's denial.

### Approval has two separate contracts

| Mechanism | Success means | Required boundary |
| --- | --- | --- |
| Mission Decision | An authorized decision resolves a gate and dependent mission work resumes | An unauthorized caller cannot resolve the gate |
| Tool Action Approval | An authorized approval allows a pending business action to execute and produce a receipt | Rejection executes no action; unauthorized approval is denied |

The Marketing examples demonstrate Mission Decisions. A mission decision does
not authorize arbitrary business mutations, and job completion does not prove
that an approved action executed. A standalone Tool Action Approval tutorial is
planned; the permission model must be verified for the selected Runtime version.
See the [approval contract notes](https://github.com/libraos/cookbook/blob/main/docs/approval-mechanisms.md).

## See Complete Applications

- **[Personal Assistant](/guides/personal-assistant):** signed-in chat, documents
  and memory, with a complete browser application.
- **[Marketing Team](https://github.com/libraos/cookbook/tree/main/apps/digital-marketing-team):**
  a multi-task mission with decisions and an attributed report.
  [Mission Console](https://github.com/libraos/cookbook/tree/main/apps/mission-console)
  is another interface to that mission, including stream recovery and failure display.
- **Existing App Integration — planned:** keep an existing customer/order
  management app and add knowledge, tools and AI-assisted business processing.
  This is not yet a runnable tutorial.

Finance, Legaltech, Healthcare and Content Moderation remain industry electives
in the Cookbook. Running an industry example does not establish the quality or
suitability of its decisions for production use.

## Setup and compatibility

Read each example's README before running its source. Tools need companion
files, a callback secret and an allowed callback host. Memory needs two distinct
ordinary-user tokens as well as a setup credential. Complete apps also need
registered sign-in redirects and their documented Runtime configuration.

The common Compose setup defaults to **kernel v0.2.2**. Check `/api/version` and
the recipe's compatibility notes for the instance you use. Original examples
have reported live checks on v0.2.2; the new minimal Tools, Memory and Async
recipes have offline coverage, with live Runtime/model verification still pending.

Async Recovery deliberately uses native HTTP. Its terminal success status is
`done`; do not mix its response shape with a managed-jobs SDK example. Recovery
of an uncertain submission requires verified server support for the saved
idempotency key. Client reconnection is separate from recovery of execution
after a server restart. See [background tasks](/durable-runs).

For v0.2.2, use each recipe's documented agent registration path and structured
output endpoint. API creation and agent-definition files do not accept identical
fields. A successful create response alone does not prove custom tools were
registered. Verify a job's state after requesting cancellation; an acknowledgement
alone does not establish that execution stopped.

### Using the VS Code extension

The [LibraOS VS Code extension](https://github.com/libraos/vscode) can set up a
local Runtime and open examples. Its current **Browse Cookbook** list is curated
and may omit newer entries; existing entries fetch their source from GitHub
`main`. Use this page for the full learning path and open the recipe README for
multi-file setup. The extension-managed Runtime does not automatically include
every recipe's feature flags, app mounts or callback configuration.

## Verify protocol behavior separately from model quality

From the Cookbook checkout, after installing `requirements-dev.txt`:

```bash
python -m pytest -m 'not live' --junitxml=test-results.xml
node --experimental-strip-types --test shared/mission-client/src/index.test.ts
```

Offline CI checks request shapes, callback verification, state transitions and
client recovery against fixtures. It does not prove live authorization,
retrieval quality, model recall or server restart durability. Optional live
tests require explicit `COOKBOOK_LIVE=1` and the selected recipe's prerequisites.

For model evaluations, check schema validity separately from answer quality,
source support and classification accuracy. Avoid exact wording snapshots;
record the model, Runtime/SDK versions, configuration and observed pass rate.
The [validation matrix](https://github.com/libraos/cookbook/blob/main/docs/validation.md)
records coverage and remaining checks.
