---
slug: /component-responsibilities
sidebar_position: 2
title: Component responsibilities
description: What applications, agents, knowledge, memory, jobs, governance, and deployment stores do—and what they do not do.
---

# Component responsibilities

Use this page to decide which layer should change when a requirement changes.
The names below describe public concepts and contracts, not Libra OS's internal
process layout.

| Layer or object | Responsible for | Not responsible for | Supported entry points |
| --- | --- | --- | --- |
| **Customer application** | User experience, business authentication and authorization, business workflow, business records, and presenting results or review decisions | Implementing Libra OS retrieval or agent execution | Application code calling HTTP APIs or an SDK |
| **API and SDK** | Stable request and response shapes, agent selection, authentication transport, and typed client access | Choosing your business workflow or repository structure | Native HTTP APIs, compatible APIs, Python SDK, generated clients |
| **Agent** | Executable instructions, model settings, knowledge bindings, tools, output shape, and execution limits | Owning the application's UI or business database | Managed-agent API or supported declarative files |
| **Employee record** | Optional shared configuration and defaults for associated agents | Executing a prompt, selecting a default agent, authorizing a user, or merging sibling-agent memory | Employee files and supported management APIs |
| **Skill or tool** | A delegated behavior or a callable operation with defined inputs and policy | Proving that an external side effect completed | Agent configuration, installed packs, callback configuration, and tool policy |
| **Knowledge** | Explicit document collections, indexing, retrieval, bindings, and collection access | Conversation history, inferred personal facts, or authoritative business records | Collection and document APIs, bindings, and supported connectors |
| **Memory** | Conversation threads, optional observations, persisted fields, and house profiles under their documented scopes | Knowledge collections or a general business database | Endpoint context, agent schema, management APIs, and operator configuration |
| **Job** | A runtime invocation record, persisted progress/events when supported, and a terminal outcome | Your application's business task, case, ticket, or workflow state | Native jobs API |
| **Governance** | Runtime identity checks, collection authorization, guardrail results, approval records, and audit information exposed by the applicable API | Replacing the application's business authorization or guaranteeing that a model answer is correct | Credentials, roles, tool policy, approval configuration, and result fields |
| **Runtime stores** | Libra OS documents, definitions, conversations, memory, jobs, approvals, audit data, and other configured runtime state | Automatically becoming the source of truth for your application's business records | Deployment database, filesystem, retention, backup, and restore configuration |
| **Model and embedding services** | Processing the requests sent to their configured endpoints | Storage ownership or runtime authorization | Model and embedding settings |
| **External systems** | Their own records and the operations exposed to Libra OS through a tool | Becoming part of Libra OS merely because a tool can call them | Tool callbacks or application-managed integration code |

## Business task versus runtime job

A **business task** is an application concept: for example, a case moving from
review to approval. Your application owns its states, permissions, and source of
truth.

A Libra OS **job** is one agent invocation that can outlive an HTTP connection.
It has its own ID, progress events, and outcome. A job reaching `done` does not
mean the surrounding business task is complete, and it does not prove that a
separate approved action executed. See [Run background tasks](/durable-runs).

## Database versus business data

A Libra OS deployment needs configured stores for runtime state. That database
is not automatically your application's database. Keep business records in the
system your application designates as authoritative; send only the required
context to Libra OS, or expose a narrowly scoped tool for reading or changing
those records.

See [Data ownership & flow](/data-ownership) before deciding where a new field
or retention rule belongs.

## “Agent harness” terminology

Libra OS does not require a separate public “agent harness” component. In an
integration, the relevant supported pieces are the agent definition, its tools
and policies, the API invocation, and the runtime result. Treat any
application-side wrapper around those pieces as application code unless a
published API gives it a distinct contract.
