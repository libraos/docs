---
slug: /workspaces-memory
sidebar_position: 5
title: Knowledge, workspaces & memory
description: Distinguish knowledge collections, filesystem workspaces, conversation history, and long-term memory.
---

# Knowledge, workspaces & memory

Use a **collection** for documents the agent should retrieve, a **conversation**
for a thread, and **memory** for information retained across turns or sessions.
These stores do not become shared simply because two agents have the same employee.

## What “workspace” means

Desk uses workspace/project language for a body of business context. In the
runtime's filesystem feature, a workspace is a directory provisioned for an
agent's file tools. A filesystem workspace is not automatically a knowledge
collection or a conversation archive.

Enable file tools with `filesystem.enabled: true` on the agent. Ingest files
into a collection separately if they should be searchable knowledge.

## Collections and bindings

A collection holds indexed documents. A Knowledge Pack packages knowledge and
configuration for installation; refer to the resulting collection IDs when
binding an agent.

Add these fields to the **agent's** frontmatter, not the employee file:

```yaml
knowledge_bindings:
  - product-documents
allowed_collections:
  - product-documents
```

`knowledge_bindings` associates the agent with a collection.
`allowed_collections` restricts retrieval; pack restrictions and caller
permissions can narrow access further. A binding alone is not an authorization
grant and does not imply that every document is retrieved on every turn.

To share document context, bind two authorized agents to the same collection.
To isolate customer or project data, configure collection access and retrieval
restrictions explicitly.

## Add documents, then verify retrieval

1. Create a collection and ingest documents. The SDK's
   [upload example](https://github.com/libraos/sdk/blob/main/python/examples/03_upload_knowledge.py)
   illustrates this flow.
2. Wait for ingestion/indexing to finish and inspect any failures.
3. Bind the collection to your agent and apply the configuration.
4. Ask a question with a known answer in those documents.
5. Inspect retrieval evidence and grounding in the response.

Retrieval capabilities depend on the configured store. Check
[Portability](/portability#knowledge-retrieval) before assuming durable vector
search is available.

## Read the evidence

Native chat exposes `retrieved_chunks` and `grounding`; other interfaces
use their own response formats. See [Calling agents](/calling-agents).
A bound collection can still return no relevant passages. Handle that outcome
explicitly instead of treating every generated answer as sourced.

## Continue a conversation or remember a fact

- Pass history or an endpoint-supported `conversation_id` for a continuing thread.
- Enable observational memory when the agent should extract durable facts.
- Use persisted structured fields when the application needs a specific value.
- Use an employee house profile for shared operating instructions.

[Managing memory](/managing-memory) explains the scopes and switches.
Observational memory is not enabled by creating a collection or employee.

Desk can connect reviewed work to its knowledge workflows, but a custom
application must configure its own ingestion and feedback process. Sending a
chat message does not automatically add that answer to a shared collection.

Stores live in your deployment; hosted embedding and model providers can still
process their contents. See [Security](/security).
