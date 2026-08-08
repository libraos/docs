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

## Who it's for

Desk is built for the shared, customer-facing inbox of a small expert team —
intake, support, and the replies that carry your name. A visa question, a
support ticket, a prospect chatting on your website: work where most answers
are re-derivable from documents the firm already has, but every answer still
needs a considered reply from someone whose time is the scarcest thing in the
building.

One loop runs underneath all of it: a message arrives on any channel — the
website widget, the mailbox, the helpdesk — and is classified and routed; an
agent grounded in your workspace drafts the reply; the draft lands in the
right group's queue; a person approves, edits, or rejects; the send goes out
with a full [audit entry](/docs/desk-audit/). Closed cases flow back into the
knowledge the next draft starts from.

Three problems this dissolves, together:

- **The inbox is where expert teams drown.** High volume, low variance —
  exactly the work a grounded drafter automates.
- **The outbound word can't be trusted to a bot.** For a law practice or a
  school, one hallucinated sentence sent to a client is a liability event.
  Desk resolves the tension instead of picking a side: the AI does the
  volume, a person keeps the signature.
- **Nobody staffs a platform team for this.** Helpdesk, CRM, knowledge, and
  the AI layer arrive pre-fused around the one loop, on one deployment.

The economics in one line: Desk converts *replying* — minutes of an expert's
time per message — into *reviewing*, seconds, without converting
accountability into hope. The queue is where the time is saved; the
[audit trail](/docs/desk-audit/) is why a regulated team is allowed to save
it.

## What you get

| Surface | What it is |
|---|---|
| **Today** | One attention queue: what is ready for review, what still needs a response, what is done |
| **Tickets** | The shared support queue, grouped by what should happen next — *needs a draft*, *awaiting approval*, *replied* — rather than by ticket status |
| **Organizations / Contacts** | The CRM records the work is about |
| **Workspaces** | Per-project knowledge — the documents an agent grounds its answers in |
| **Content / Campaigns** | Drafting surfaces with the same approval discipline |
| **Mail** | Each member's own work mailbox |

Every one of these carries a **copilot** docked on the right, grounded in
whatever is on screen — the list you are looking at, or the record you opened.

## Autonomy is a dial, not a switch

Each agent runs at a level you choose:

- **Draft only** — it never acts, it only proposes.
- **Approval** — it may act once a person approves.
- **Auto** — it acts within its **grant**: the explicit list of tools and
  channels it may use without review, issued by an admin and recorded in the
  [audit trail](/docs/desk-audit/). Anything outside the grant still lands in
  the queue as a draft.

New agents start at draft-only. Moving an agent up is a decision someone makes
on purpose, in Admin.

## Where it runs

Desk deploys alongside a Libra OS kernel — hosted or self-hosted, the same as
the platform. See [Cloud vs Self-Hosted](/editions) for the trade-off, and
[Deployment](/deployment) for how a desk is stood up.
