---
slug: /desk-connections
sidebar_position: 3
title: Connections
description: Desk has two kinds of connection — the organization's, configured by an admin, and each member's own. Admins decide which services members may connect; members connect their own accounts.
---

# Connections

**Connection is access; approval is permission.** Connecting a service lets an
agent reach it; nothing about connecting lets the agent act through it —
outbound actions remain drafts until a person approves.

With that split in place: Desk has two kinds of connection, governed
differently because their blast radius is different.

## Organization connections

Configured by an admin, used by the whole deployment. The corporate helpdesk,
the sending domain, the company mailbox.

These carry **one credential for everyone**, so they are admin-only: the
connector console refuses non-admins on every route, reads included. There is
exactly one row per service for the whole deployment.

Typical org connections: the native ticket intake, email intake, corporate
mailbox (Microsoft 365 or Google Workspace), Freshdesk, the sending provider,
the website crawler, a Ghost blog.

## Personal connections

Each member connecting **their own account** — their Gmail, their calendar.
The credential belongs to that person, is stored separately from the
organization's, and only they can use it.

The two-step model matches how Claude's own Google Workspace connectors work:

1. **An admin opens the service.** Until then it does not exist for members.
2. **Each member connects their own account**, from *Settings → Connections*.

This is deny-by-default and enforced server-side, not merely hidden in the UI.
A service nobody opened is one this deployment holds no member credentials
for — which is the point. A member cannot make the company hold their
Google credentials by finding the right URL.

### What an admin does

In the connector console, the **Personal connections** section lists services
that are personal by nature — Gmail, Google Calendar, Google Drive, Notion,
GitHub — each with one toggle. Turning it on permits members to connect that
service. It does **not** mean the organization runs a connector for it.

### What a member does

*Settings → Connections* shows the services their organization has opened, and
their own connections to them. Connecting asks only for that service's
credentials; the app never shows a credential back, only whether each one is
set.

**Disconnecting always works**, including after an admin closes a service. A
policy change must never strand a credential with no way to revoke it.

## What is stored, and what is not

- Credentials are **encrypted at rest** and never returned by the API. Surfaces
  learn only *which* secrets are set, never their values.
- Rotating one credential leaves the others alone — a blank field means "keep
  what is stored", not "delete it".
- Personal credentials are never readable by an admin. The console can see that
  a service is open; it cannot read anyone's connection to it.

## Where the drafts land

Connectors can be **group-bound**: a connector may name the group whose queue
receives its drafts — the support intake to the support group, the corporate
mailbox to whoever owns outbound mail. A connector with no group bound routes
its drafts to the admin-only queue. Binding is part of the connector's
configuration and can be changed there. Who's in a group is managed under
[Employees and groups](/docs/desk-settings/#admin--the-organizations).
