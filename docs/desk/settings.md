---
slug: /desk-settings
sidebar_position: 2
title: Settings vs Admin
description: Desk splits personal preferences from organization policy. Settings is what you control for yourself; Admin is what your organization decides for everyone.
---

# Settings vs Admin

Desk has two places that look like configuration, and the difference between
them is not cosmetic — it is who the decision belongs to.

| | **Settings** | **Admin** |
|---|---|---|
| Who opens it | every employee | admins only |
| What it changes | your own preferences and your own connections | organization policy, for everyone |
| Example | which language you read the app in | which services employees may connect at all |

The rule: **Settings never overrides Admin.** Where a personal setting is
constrained by policy, Settings says so plainly and names who can change it,
rather than showing you a control that quietly does nothing.

## Settings — yours

- **Language** — English or 简体中文, remembered per person.
- **Connections** — the state of your own working connections. Your corporate
  mailbox appears here as *Working for your account* or *Not enabled by your
  organization*; it is labelled **Managed by your organization** because you
  cannot turn it on yourself, and no toggle is shown that would fail.
- **Your work** — how many queued decisions are waiting on you.

## Admin — the organization's

- **Connectors** — the services this deployment runs, and their credentials.
- **Employees and groups** — who reviews what, and which group approves which
  queue.
- **Agents** — each agent's model, knowledge bindings and autonomy level.
- **Imports** — one-time backfills from a system you are moving off.

Admin opens in its own tab. It is a separate console, not a page of the app.

## Why a non-admin sees fewer doors

Desk does not show an employee a control that will refuse them. The connector
console is admin-gated by the kernel on **every** route — reads included — so
the navigation entry is not rendered for a non-admin at all, rather than
leading to a wall.

This is the same reasoning behind the notification badge counting only work
**you** can decide: an affordance that leads nowhere is worse than no
affordance.
