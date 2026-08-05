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

## Reference stack

For a container-based deployment, see the reference
[docker-compose stack](https://github.com/libraos/stack) — the core server plus
optional companion apps.

:::note
Sizing, connectors, and support are scoped per deployment. See
[pricing](https://libraos.com/pricing/) or book a demo.
:::
