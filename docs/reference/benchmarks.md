---
slug: /benchmarks
sidebar_position: 3
title: Benchmarks
description: Measured, not marketed — controlled same-model A/B results for the Libra OS system layer.
---

# Measured, not marketed

The figures below are previously reported project results. This page does not
include the raw runs, version pins, or enough methodology to reproduce them;
request those artifacts before using the numbers for a deployment decision.
They are not capacity or accuracy guarantees for your application.

| | Result | What it means |
| --- | --- | --- |
| **GAIA** — public agentic benchmark | **+18.9 pts** | Reported absolute score difference; inspect the task set and model/version controls |
| **Grounded scale** | **256** concurrent agent workloads per 8×H100 node, 98.0% grounded success (single run) | We measure grounded answers, not HTTP 200s |
| **Token economy** | **23×** fewer tokens per task (~27K vs ~615K) | Under a tenth of the cost per answer |
| **AgentDojo** — prompt-injection defense | attack success **26.8% → 17.3%**, benign utility held at **90.7%** | Hardened without making the system useless |

Full methodology and per-run data available on request —
[contact@meganova.ai](mailto:contact@meganova.ai).
