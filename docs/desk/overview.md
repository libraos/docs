---
slug: /desk
sidebar_position: 1
title: What Libra Desk is
description: The company workspace on Libra OS — a shared, governed queue where agents draft and a person approves, with an audit trail behind every outbound action.
---

# What Libra Desk is

**Libra Desk** is the company workspace that runs on Libra OS. Libra OS is the
platform — the agent runtime, model routing, knowledge indexing and identity.
Desk is what your team actually opens: a shared queue of customer work, with
agents drafting and people deciding.

A deployed instance is called *a desk*.

## The shape of the product

Desk is built around one idea: **the AI drafts, a person approves.** Nothing
leaves the building because a model decided it should.

- An agent proposes a reply. It lands in a queue as a **draft**, not a send.
- A reviewer reads it next to the customer's message, edits or approves.
- The decision is recorded — who approved what, when, on which draft.

If that sounds like reviewing a pull request, that is deliberate. Reviewing the
words your company says to a customer deserves the same treatment as reviewing
the code it ships.

## What you get

| Surface | What it is |
|---|---|
| **Today** | One attention queue: what is ready for review, what still needs a response, what is done |
| **Tickets** | The shared support queue, grouped by workflow state rather than by ticket status |
| **Organizations / Contacts** | The CRM records the work is about |
| **Workspaces** | Per-project knowledge — the documents an agent grounds its answers in |
| **Content / Campaigns** | Drafting surfaces with the same approval discipline |
| **Mail** | The employee's own work mailbox |

Every one of these carries a **copilot** docked on the right, grounded in
whatever is on screen — the list you are looking at, or the record you opened.

## Autonomy is a dial, not a switch

Each agent runs at a level you choose:

- **Draft only** — it never acts, it only proposes.
- **Approval** — it may act once a person approves.
- **Auto** — it acts within its grant.

New agents start at draft-only. Moving an agent up is a decision someone makes
on purpose, and the approval queue is where that trust is earned.

## Where it runs

Desk deploys alongside a Libra OS kernel — hosted or self-hosted, the same as
the platform. See [Cloud vs Self-Hosted](/editions) for the trade-off, and
[Deployment](/deployment) for how a desk is stood up.
