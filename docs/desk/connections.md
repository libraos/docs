---
slug: /desk-connections
sidebar_position: 3
title: Connections
description: Every connection on a desk belongs to the organization. Admins configure the shared ones and decide which services employees may connect for the desk; nothing about connecting lets an agent act without approval.
---

# Connections

**Connection is access; approval is permission.** Connecting a service lets an
agent reach it; nothing about connecting lets the agent act through it —
outbound actions remain drafts until a person approves, or until an admin has
deliberately moved that agent to [auto](/docs/desk/#autonomy-is-a-dial-not-a-switch).

Every connection on a desk **belongs to the organization**. Some are set up
by an admin with one shared credential; some are opened by an admin and then
connected by an employee signing in at the provider. Either way the
connection is the desk's, its assistants use it, and an admin can see that it
exists. There are no private, per-member connections.

## Org connectors

Configured in **Admin → Connections & data**. One row per service for the
whole deployment; the connector console is admin-gated on every route, reads
included.

| Connector | Kind | What it does |
|---|---|---|
| **Tickets** | intake, native | The desk's own governed ticket store — the default helpdesk. Optional email notifications to requesters. |
| **Website widget** | intake, native | Embeddable chat for your site. Several named widgets, each bound to an agent, each with its own embed snippet; visitors can ask the knowledge base and open a ticket. Has its own admin panel. |
| **Email intake** | intake + outbound, native | A support mailbox over IMAP; replies go out over SMTP or Gmail. |
| **Internal tickets** | intake, native | Employee-facing IT / internal requests, with an allowlist of intents that may auto-resolve. |
| **Corporate email** | intake, vendor | The company mailbox fleet — Microsoft 365 (app permissions) or Google Workspace (domain-wide delegation). One tenant credential; each member then sees their own mailbox under **Mailbox**. Can be scoped to a group. |
| **Freshdesk** | intake, vendor | Two-way sync for teams keeping an existing helpdesk during the move. |
| **Sending provider** | outbound, vendor | Amazon SES or SMTP, used by campaigns; unsubscribe endpoint and a per-message recipient cap. |
| **Marketing** | outbound, native | The campaign action adapter — sends land as approvable actions. |
| **Ghost** | outbound, vendor | Publish Content Studio pieces to a Ghost blog, as drafts. |
| **Website crawler** | knowledge, native | Crawl your own sites into the knowledge layer: start URLs, depth, page cap, recrawl interval. No secrets. |
| **Contacts** | knowledge, native | Derives CRM dossiers from what the desk has seen, on an interval. |

**Slack, Gmail, Google Calendar, Google Drive** connect through the kernel's
OAuth integrations rather than the table above (Google OAuth is off unless the
deployment enables it). **GitHub** connects through its own OAuth and webhook.
Each OAuth integration exposes its tools with a per-tool policy — **allow**,
**ask** (the call lands in the approval queue), or **never**; read tools
default to allow, write tools to ask.

## Employee-connected services

An admin can open a service — Gmail, Google Calendar, Google Drive, Notion,
GitHub — so that employees may connect it **for the desk**. The employee
signs in with whatever account they have at the provider; the connection that
results belongs to the organization and its assistants use it. Turning a
service on does not mean the organization runs a connector for it; a service
nobody opened holds no credentials on this deployment. Deny by default,
enforced server-side.

Connecting this way needs a kernel with the lease model and a configured
OAuth client for that provider. Where that is not in place, the employee sees
a request-access state rather than a form that will fail.

**Disconnecting always works**, including after an admin closes a service. A
policy change must never strand a credential with no way to revoke it.

## Imports

Alongside live connections, **Admin → Imports** runs one-time backfills from
a system you are moving off — website crawl, Slack history, GitHub, a mailbox,
Freshdesk — as resumable jobs into the knowledge layer and the ticket store.

## What is stored, and what is not

- Credentials are **encrypted at rest** and never returned by the API. Surfaces
  learn only *which* secrets are set, never their values.
- Rotating one credential leaves the others alone — a blank field means "keep
  what is stored", not "delete it".

## Where the drafts land

Intake connectors are **group-bound**: each names the group whose queue
receives its drafts — the support intake to the support group, the internal
tickets to IT. A connector with no group bound routes its drafts to the
admin-only queue. Binding is part of the connector's configuration. Who's in
a group is managed under
[Employees and groups](/docs/desk-settings/#admin--the-organizations).
