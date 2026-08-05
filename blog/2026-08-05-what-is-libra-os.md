---
slug: what-is-libra-os
title: "What is Libra OS? The AI Operating System, explained"
authors: [libraos]
tags: [explainers]
---

The simplest way to think about Libra OS: a desktop operating system is the
base layer that runs your applications; **Libra OS is the base layer that
runs, coordinates, and supervises a team of AI employees**. One system where
they share knowledge, hand work to each other, and complete real business
processes end to end — inside your walls.

<!-- truncate -->

## Not one model — many, working in parallel

Libra OS is model-agnostic by design. Instead of depending on a single AI
vendor, it routes work across multiple models side by side — a planner-class
model for the hard calls, a fast lightweight model for high-volume steps, a
synthesis model for the final grounded answer. Each tier is just a model id
behind **any OpenAI-compatible endpoint**: bring your own keys, point a tier
at a locally-run model, or mix providers per tier.

Model ids carry a vendor prefix so the gateway knows where to route each
request — `anthropic/…` for an Anthropic model, `gemini/…` for a Google
model. (Locally-run Ollama is the one exception and needs no prefix.) The
full routing story is in [Model settings](/model-settings).

## A team, not a chatbot

Libra OS ships with eight supervised digital employees, and you can define
your own [in YAML](/employee-yaml). The point isn't one assistant that
answers questions — it's specialized roles collaborating on one system: one
employee drafting the document, another researching, another handling the
customer thread, all sharing the same knowledge base and the same audit
trail.

Every employee works under the same supervision bound: output is
**source-cited**, work that escalates past an employee's scope goes to a
human, and nothing ships without review. That last part is what makes it
safe to hand real work over — you can see exactly what steps each employee
took and which tools it used.

## Yours, wherever it runs

Libra OS comes in [two editions](/editions) of the same product: **Libra OS
Cloud**, hosted and sign-up-and-go, and **Libra OS Self-Hosted** — your
cloud or fully air-gapped on-prem, where customer data, model traffic, and
knowledge stores never leave your environment. Same engine, same employees,
same API; an employee built in one runs in the other.

## Build on it: the SDK

The official Python devkit, [`libraos-sdk`](https://pypi.org/project/libraos-sdk/)
(1.0.2), is live on PyPI. It speaks the same protocol as Anthropic's Managed
Agents, so Anthropic SDK callers can point at a Libra OS deployment with a
drop-in client — see [Creating an agent](/creating-an-agent).

One streaming caveat worth knowing when you build observability: while
**server-side tools** run, the SSE stream emits no discrete content-block
events. The tool results appear in the final `MessageResponse.content[]` as
`server_tool_use` blocks. If you're rendering live activity, poll message or
job state for those phases — or use a non-streaming call — rather than
waiting on stream events that never come.

## In one sentence

Libra OS gives a team of AI employees a shared work desk — and gives you the
supervision, citations, and audit trail to confidently hand them real work.

Start with the [getting-started guide](/getting-started), or read how the
[two editions](/editions) compare.
