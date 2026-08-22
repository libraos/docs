---
slug: /deployment
sidebar_position: 4
title: Deployment
description: One binary, three ways to run it — managed cloud, your cloud, or air-gapped on-prem.
---

# Deployment

Run the same runtime in a managed environment, your cloud, or on-premises.
Plan the database, model services, storage, and credentials alongside the binary.

## Deployment modes

| Mode | What it means | Best for |
| --- | --- | --- |
| **Managed cloud** | Managed environment; [private-beta access](/cloud) | Getting started fast, smaller teams |
| **Your cloud** | Your infrastructure and configured data boundary | Firms with a cloud footprint and compliance requirements |
| **Air-gapped on-prem** | Your hardware, offline license, no phone-home | Work that cannot leave the building |

In the self-hosted modes there is no per-seat cloud dependency and no phone-home
— the license is validated offline. On-premise deployments can also run
networked behind your firewall if full air-gapping isn't required.

The binary size varies by release. A working deployment also needs a database,
model endpoint, and any storage or tool backends required by the application.
The [quickstart](/getting-started) covers the minimum configuration.

Air-gapped operation requires local generation and embeddings plus tools that
work inside that boundary. Verify [effective capabilities](/portability) and
[data flow](/security) before disconnecting the deployment.

## What ships in the binary

- The kernel and knowledge base
- The AI firewall (three-tier screening)
- The agent runtime; create definitions through APIs, files, or available setup tooling
- Compatible API endpoints that call models served by your configured gateway

## Secrets & environment

The server is its own identity provider: every login session and API token it
issues is signed with `LIBRA_OS_JWT_SECRET`. The
[getting-started guide](/getting-started) shows how to generate it; for a
production deployment, also plan for:

- **Replicas share one secret.** Every instance behind a load balancer (or in
  a blue/green pair) must run the same `LIBRA_OS_JWT_SECRET`, or tokens minted
  by one replica are rejected by the next.
- **Store it like a credential.** Put it in your secret manager and inject it
  at start — not in shell history, unit files, or compose files checked into
  git. With auth enabled the server refuses to boot if the secret is unset,
  a known default, or shorter than 16 bytes.
- **Rotation logs everyone out.** Changing the secret invalidates every
  outstanding session and token at once. That makes rotation a deliberate,
  announced event — useful after a suspected leak, disruptive as routine
  hygiene.
- **Token lifetime is tunable.** `LIBRA_OS_ACCESS_TOKEN_TTL` sets how long
  issued tokens live (a Go duration such as `720h`; unset defaults to 1 hour).
  Longer lifetimes trade fewer re-logins for a longer exposure window on a
  leaked token — and a wider blast radius when you do rotate the signing
  secret.

`libraos doctor deployment` audits all of this — environment, database, LLM
gateway, and the running server — and prints a fix line for anything wrong.

## Knowledge base & retrieval

Which backend actually holds vectors, how to confirm retrieval is working, and
how to scope auto-indexing: see **[Knowledge base & retrieval](/knowledge-retrieval)**.
If you are upgrading to v0.1.18, read the auto-indexing note there first — the
default changed.

## Reference stack

For a container-based deployment, see the reference
[docker-compose stack](https://github.com/libraos/stack) — the core server plus
optional companion apps.

:::note
Sizing, connectors, and support are scoped per deployment. See
[pricing](https://libraos.com/pricing/) or book a demo.
:::
