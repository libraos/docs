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

The left rail is deliberately short — five doors, one loop:

| Rail | What it is |
|---|---|
| **Today** | One attention queue: what is ready for your decision, what still needs a response, what is done. Carries the badge that counts only decisions *you* can make. |
| **Tickets** | The shared support queue, grouped by what should happen next — *needs a draft*, *awaiting approval*, *replied* — rather than by ticket status. Shown to members of a reviewing group, and to admins. |
| **Contacts** | The CRM records the work is about. |
| **Mailbox** | Each member's own work mailbox, read through the corporate connection (Microsoft 365 or Google Workspace) — reply, summarize, share a thread into the knowledge layer. |
| **Connections** | Which services this desk is connected to. Admin-only today. |

More surfaces sit one keystroke away in the **command palette (⌘K)** and
behind cross-links from the records above:

| Surface | What it is |
|---|---|
| **Organizations** | Account-level CRM records; contacts roll up into them. |
| **Projects** | Where incoming work is filed. Every ticket, thread, and document is classified into a project by routing rules an admin sets; a review queue catches what the classifier was unsure about. A project's page carries its own knowledge — the documents an agent grounds its answers in ([how this layer works](/workspaces-memory)). |
| **Content Studio** | Drafting long-form content under the same approval discipline; can publish as a draft to a connected blog. |
| **Campaigns** | Segment, draft, approve, and send email campaigns. The send engine is governed, not just drafted: canary-first staged fan-out, a per-stage bounce/complaint gate that pauses the campaign until a person resumes it, per-contact frequency caps, consent re-checked per send, and an idempotent send ledger so a crashed worker can never double-send. One-click unsubscribe is built in. |
| **Chat** | A direct conversation with any agent, outside the queue. |

A **copilot** docks on the right of the record and list surfaces — Tickets,
Contacts, Organizations, Content, Campaigns, Mailbox, Projects — grounded in
whatever is on screen. It answers, summarizes, and drafts; it does not act.
Toggle it with ⌘J. Today and the admin console do not carry one.

### Admin

Admin opens in its own tab (see [Settings vs Admin](/docs/desk-settings/)).
Its sections:

- **Agents** — each agent's model, instructions, knowledge bindings,
  connections, automations, permissions and autonomy level; plus one-click
  **department templates** (support, IT helpdesk, HR, sales) that provision an
  agent together with its approval group.
- **People** — employees, and the groups that review each queue.
- **Connections & data** — org connectors, the website widget, corporate
  email, knowledge sources, one-time **imports** from a system you are leaving,
  and the Project Brain taxonomy.
- **Governance** — the approval ledger, per-agent autonomy, and (on kernels
  that serve it) the authorization console: intent → decision → execution
  receipt, with risk tier, reversibility and grant evidence per action.
- **Advanced** — usage and limits, model configuration, analytics.

## Autonomy is a dial, not a switch

Each agent runs at a level an admin chooses, per agent:

- **Draft only** — it never acts, it only proposes.
- **Approval** — it may act once a person approves. **This is the default**
  for a new agent.
- **Auto** — the proposal is filed and approved in the same motion, by the
  connector's service identity, and recorded in the
  [audit trail](/docs/desk-audit/) like any other approval. It is an audited
  approval, not a bypass of the queue. Auto is off unless the deployment
  enables it (`AUTONOMY_AUTO_ENABLED`), and provisioning scripts refuse to
  set it — turning it on is a decision someone makes on purpose, in Admin.

Today the dial governs one action: the **public reply**. Status, priority,
group assignment and escalation are always proposals that a person decides.

Autonomy is separate from *what an agent may reach*. Tool access on a
connected service is set per tool — **allow**, **ask** (the call lands in the
approval queue), or **never** — and contact-record access per agent is
**none / read / read-write**, deny by default. There is also a per-connector
**kill switch** that stops filing and auto-approval at once.

## Where it runs

Desk deploys alongside a Libra OS kernel — hosted or self-hosted, the same as
the platform. See [Cloud vs Self-Hosted](/editions) for the trade-off, and
[Deployment](/deployment) for how a desk is stood up.
