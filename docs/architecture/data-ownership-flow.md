---
slug: /data-ownership
sidebar_position: 3
title: Data ownership & flow
description: Identify the authoritative system for business records, documents, agent state, memory, jobs, approvals, and audit data.
---

# Data ownership & flow

“Stored in the same deployment” does not mean “owned by the same component.”
Choose an authoritative system for each data class, then configure access,
retention, deletion, backup, and processing location for that class.

| Data class | Authoritative system | Libra OS behavior | Retention and deletion owner |
| --- | --- | --- | --- |
| **Application business records** | Your application or external business system | Receives only the values placed in a request, retrieved collection, or permitted tool call | Application or external-system operator |
| **Agent and employee definitions** | The supported management API or declarative source selected by the operator | Loads configuration used for execution; file and managed-API fields are not always interchangeable | Deployment operator |
| **Source documents** | The collection and document source chosen by the application | Stores or references documents according to the configured document path and collection | Collection owner and deployment operator |
| **Indexed chunks and embeddings** | The configured knowledge backend | Parses, chunks, embeds, and retrieves only when the effective configuration supports it | Deployment operator; backend changes require an explicit migration or re-ingest plan |
| **Conversation threads** | Libra OS conversation store for the authorized caller and conversation ID | Persists endpoint-specific history according to the configured store and retention | Deployment operator and application privacy policy |
| **Observational memory** | Libra OS memory store when enabled | Extracts scoped observations asynchronously; disabling use does not delete existing observations | Deployment operator |
| **Persisted fields** | Libra OS structured memory for the declared scope | Merges only declared output fields using the configured rule | Application designer and deployment operator |
| **House profile** | Managed employee profile | Makes shared operating instructions available to associated agents in the applicable context | Authorized profile editor |
| **Jobs, events, and results** | Libra OS jobs store | Keeps the invocation request, progress, and outcome for the configured retention period | Deployment operator; the application must retain any identifier it needs longer |
| **Approvals and runtime audit records** | The applicable Libra OS approval or audit API | Records the runtime decision or receipt exposed by that API | Deployment operator and governance policy |
| **Credentials and secrets** | The configured identity or secret-management system | Uses credentials to authenticate callers and configured dependencies | Credential owner and deployment operator |

Knowledge collections are not memory. A document intentionally placed in a
collection has different scope, lifecycle, and deletion behavior from a
conversation, observation, persisted field, or house profile. See
[Managing memory](/managing-memory).

## Storage flow

1. The application sends a request and the minimum context the selected
   endpoint requires.
2. Libra OS resolves the caller, agent, collection access, and memory scope.
3. The runtime may read permitted documents and prior runtime state.
4. The runtime stores the endpoint's documented state, such as a conversation,
   job event, result, or approval record.
5. The application reads the returned status and updates its own business
   record only according to its own workflow rules.

Do not use a conversation ID, job ID, employee owner, or collection name as a
substitute for application authorization or tenant isolation.

## Processing flow

Storage and processing are separate. Depending on configuration, prompts,
retrieved passages, document chunks, search queries, and tool inputs can be
sent to model, embedding, search, or callback services. A self-hosted runtime
does not make those dependencies local automatically.

Before production:

- list every configured processing endpoint;
- verify `GET /api/capabilities` against the running deployment;
- test two distinct users and collection scopes;
- set retention and deletion procedures for each separate store;
- confirm backups and restores cover the intended runtime state; and
- verify external tools receive no more data or authority than required.

See [Security & data boundaries](/security), [Portability](/portability), and
[Deployment](/deployment) for the operational contracts.
