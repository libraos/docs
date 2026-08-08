---
slug: /desk-audit
sidebar_position: 5
title: Audit trail
description: >-
  What Libra Desk records about every outbound action - the fields, who can
  read them, how long they are kept, and how they leave the system.
---

# Audit trail

Desk's promise is that nothing leaves the building because a model decided it
should. The audit trail is how you prove that promise to someone who wasn't in
the room — an auditor, a regulator, a client, or you in six months.

This page answers the four questions every compliance review asks: what is
recorded, who can read it, how long it is kept, and how it gets out.

## What is recorded

Every outbound action is one record in the kernel's action ledger, created
when the draft is filed and carried through its whole life:

| Field | What it captures |
| ----- | ---------------- |
| **Actor** | Who decided — the authenticated identity of the approver, and whether the decider was a **person or a service**. Written from the verified session, never from the request body. |
| **Agent** | Which agent proposed the draft, and which connector filed it. The filer is recorded server-side, which is what makes the rule below enforceable. |
| **Action** | The tool called, the channel it came through, and the full proposed content and parameters. For ticket replies the recipient is the ticket's requester, joined through the ticket reference the action carries. |
| **Decision** | Approved or rejected, with the decision reason — then the execution outcome (executed, or failed) as the send actually happens. |
| **Timestamps** | When the draft was filed and when it was decided. The send itself is recorded as an event on the ticket's own timeline. |

**The filer cannot be the decider.** The kernel refuses self-approval: the
identity that created an action is recorded server-side and cannot approve
it. Four eyes is enforced in the kernel, not requested in the UI.

**Editing is not amending.** A reviewer who edits a draft does not mutate the
agent's proposal. The original is rejected — reason: *superseded by an
approver's amendment* — and the edited version is filed, approved, and sent
as its own action carrying a pointer back to the one it amends. Both versions
survive, decided, in the trail.

**Auto-execution thins nothing.** An agent acting within its autonomy grant
does not bypass the queue: the action is filed normally and approved through
the *same* endpoint a person would use. The decider is recorded as a service,
and the decision reason names the autonomy policy and the agent. The grant
itself has its own trail — every change to an agent's autonomy level records
who made it, when, and the old and new levels.

Rejected drafts are recorded too. The trail is a record of decisions, not
just of sends.

## One decision, decided once

There is no route — API or console — that deletes an audit entry or amends a
decision. The only writes an entry ever receives advance it through its
lifecycle: filed, decided, executed. Deciding is single-use and enforced
server-side — a second decision on the same action is refused with a
conflict, and the approver's identity and reason, once written, are protected
from later overwrites by the execution step.

Admins can read the trail; they cannot amend a decision. The enforcement
lives at the API layer: the ledger is a table in the deployment's own
database, as everything in a sovereign deployment is — the product gives no
one a route around the rules, and the database stays under your control, not
ours.

## Who can read it

- **Admins** read the full trail for the deployment.
- **Reviewers** read the entries for queues they belong to — access is scoped
  by group membership, and deciding additionally requires an approver role in
  that group.
- **Connectors read only what they filed.** A connector's service identity
  can list and follow its *own* proposals — that is how it learns the
  decisions — and nothing anyone else filed. Deciding is refused to
  connectors outright.
- An entry you cannot access answers as if it did not exist — the API refuses
  to confirm the existence of actions outside your scope.

## Retention

Audit entries are kept indefinitely. There is no retention window, no purge
job, and no archival path in the product today — nothing ages out. A
self-hosted deployment owns its storage and can apply a database-level
retention policy of its own; that is an operational decision made outside the
product, and it should be written down where your auditors can find it.

## Export

The console's analytics view exports the action ledger as **CSV** — one row
per action with its source, group, status, decision, decider, and reason —
gated by the analytics entitlement and scoped to what the exporting user may
read. The same records are readable over the API with the same scoping, for
anything scripted.

## Where this sits

The audit trail is the third leg of Desk's model:

1. [Connections](/docs/desk-connections/) decide what an agent can reach.
2. The approval queue decides what it may do.
3. The audit trail proves both, after the fact.

Connection is access; approval is permission; **audit is proof**.
