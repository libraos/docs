---
slug: /deployment
sidebar_position: 4
title: Deployment
description: One binary, three ways to run it — managed cloud, your cloud, or air-gapped on-prem.
---

# Deployment

**One binary, three ways to run it.** The same Go runtime in all three modes —
the demo is the product.

## Deployment modes

| Mode | What it means | Best for |
| --- | --- | --- |
| **Managed cloud** | Runs on our inference cloud, subscription pricing | Getting started fast, smaller teams |
| **Your cloud** | Your own tenant, your data boundary | Firms with a cloud footprint and compliance requirements |
| **Air-gapped on-prem** | Your hardware, offline license, no phone-home | Work that cannot leave the building |

In the self-hosted modes there is no per-seat cloud dependency and no phone-home
— the license is validated offline. On-premise deployments can also run
networked behind your firewall if full air-gapping isn't required.

**Deployment reality:** one engineering day from install to first governed
workflow. 59MB, no dependency stack, no Kubernetes project.

**No telemetry, by design.** In air-gapped mode there is nothing calling home.
Not a setting you toggle — an architectural property.

## What ships in the binary

- The kernel and knowledge base
- The AI firewall (three-tier screening)
- Eight supervised digital employees
- An OpenAI-compatible endpoint fronting 100+ models with failover

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

## Reference stack

For a container-based deployment, see the reference
[docker-compose stack](https://github.com/libraos/stack) — the core server plus
optional companion apps.

:::note
Sizing, connectors, and support are scoped per deployment. See
[pricing](https://libraos.com/pricing/) or book a demo.
:::
