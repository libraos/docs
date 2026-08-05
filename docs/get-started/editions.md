---
slug: /editions
sidebar_position: 2
title: Cloud vs Self-Hosted
description: Libra OS ships in two editions — hosted Cloud and sovereign Self-Hosted. Same engine, same agents, same API; choose by who runs the infrastructure.
---

# Cloud vs Self-Hosted

Libra OS comes in two editions. They are the **same product** — the same engine,
the same eight supervised employees, the same OpenAI-compatible API and
[`libraos` SDK](/creating-an-agent). What differs is who runs the servers and
where your data lives.

| | **Libra OS Cloud** | **Libra OS Self-Hosted** |
| --- | --- | --- |
| Get started | [Sign up free](/cloud) — workspace in minutes | [Install](/getting-started) a 59MB binary |
| Infrastructure | We run and update it | Your hardware — on-prem, VPC, or air-gapped |
| Data residency | Our managed environment | Never leaves your network |
| Compliance posture | Managed | SOC 2 Type II certified · HIPAA-ready · air-gapped |
| Updates | Automatic | You choose when to upgrade |
| Best for | Getting started fast, smaller teams | Regulated, sovereign, or offline work |
| Pricing | Free tier, then [from $249/mo](https://libraos.com/pricing/) | Free to start; commercial license per node |

## Same engine, either way

Both editions run the identical Libra OS runtime and the identical agent model.
Anything you read in [Building agents](/creating-an-agent),
[Defining employees in YAML](/employee-yaml), the [Guides](/guides/customer-support),
or [Model settings](/model-settings) applies to **both** — the only thing that
changes between them is the base URL and API key your clients point at.

That is the point of shipping one product in two editions: you never learn two
systems, and you never rebuild when you switch.

## Moving between editions

Because the two editions are the same Libra OS, an employee built in one runs in
the other unchanged. Employees are portable bundles — agents, prompts,
knowledge-collection bindings, and configuration — that export from one
deployment and import into another:

- **Cloud → Self-Hosted** — the common path: prototype fast on Cloud, then move
  to your own infrastructure when compliance, data-residency, or scale calls for
  it. Export your workspace, stand up a self-hosted binary, import. No agent
  rebuild, no prompt rewrite.
- **Self-Hosted → Cloud** — hand operations to us for a team or workload that no
  longer needs to stay on your hardware.

## How to choose

- **Start on Cloud if** you want to evaluate quickly, you're a smaller team, or
  you don't have a hard data-residency requirement. It's the fastest path from
  idea to a working assistant. → [Libra OS Cloud](/cloud)
- **Start on Self-Hosted if** your data cannot leave your network, you need
  air-gapped or on-prem deployment, or you're in a regulated environment where
  the sovereignty guarantees are the requirement. → [Getting started](/getting-started)

Not sure? Start free on Cloud today — you can always move to self-hosted later
without rebuilding anything.
