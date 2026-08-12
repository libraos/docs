---
slug: /workspaces-memory
sidebar_position: 4
title: Workspaces & memory
description: Where your company's context lives — knowledge collections agents ground in, the memory that carries across sessions, and the loop that makes both compound.
---

# Workspaces & memory

The tagline promises *one sovereign AI layer over everything your company
knows*. This page is where that layer lives.

A **workspace** is a living body of knowledge for a project, a customer, a
team, or a workflow: the documents that define it, and — over time — the
decisions, closed cases, and useful outputs that came from working it. Agents
don't start from scratch; they start from the workspace. Any agent bound to
it picks up the thread with the right context already in place.

## Collections and bindings

Knowledge is organized into **collections** — one per body of context. An
agent sees a collection only if it is **bound** to it, at create time, in the
[employee YAML](/employee-yaml):

```yaml
knowledge_bindings:
  - product-documents
  - matter-documents
```

Bindings are the scope line: an intake agent bound to the product docs cannot
answer from the legal matter files, no matter what it is asked. Sharing
context across agents is the same mechanism — bind two agents to one
collection and they work from the same knowledge.

Documents get in by upload, by the website crawler, or by export/import when
moving a collection between deployments (`libraos knowledge` — the dev→prod
path). Retrieval over a collection is graph + vector + keyword combined, so
an answer can be traced to the exact passages it used.

## Grounding is visible

You met the two fields in the [quickstart](/getting-started): every chat
response carries `retrieved_chunks` — the exact files the answer drew on —
and a `grounding` verdict. Bound agents answer *from your sources*, and show
their work. That is the property everything else here exists to serve: not
that the AI sounds right, but that you can check it.

The practical side effect is cost: grounding retrieves the relevant slice of
a workspace instead of re-feeding the whole history into every prompt. Shared
context is cheaper than repeated context.

## Memory across sessions

Conversations are not islands. Passing `conversation_id` continues a thread,
and the runtime's **observational memory** extracts durable facts from work
as it happens — attributes, dates, events — so they can be recalled later
without re-reading every transcript. Facts recognized as personal are routed
to a dedicated per-person pool rather than the shared one; a person's private
context does not leak into the team's.

## The loop that compounds

On [Libra Desk](/desk) this layer appears as **Workspaces**, and the loop
closes: every case your team reviews and sends flows back into the knowledge
the next draft starts from. The workspace is not a folder you fill once — it
is the accumulating memory of how your company handles its work, and it is
the reason the system gets better at your business the longer it runs.

All of it stays inside your deployment: the collections, the vectors, the
extracted facts. On Self-Hosted, that means inside your walls — see the
[security model](/security) before connecting sensitive material, and
[Local models](/model-settings#local-models) if even embeddings must not
leave the building.
