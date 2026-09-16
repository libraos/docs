---
slug: /security
sidebar_position: 2
title: Security & data boundaries
description: Where data is stored and processed, how identity and tools are authorized, and what grounding and approval results mean.
---

# Security & data boundaries

Libra OS can run inside your infrastructure. Its configuration determines which
data is processed locally and which data goes to external services.

## Storage and processing are separate

| Component | Data it may receive | Configuration to check |
| --- | --- | --- |
| Model gateway | Prompts, retrieved passages, tool results, and generated output | Answer, planner, and skill model settings |
| Embedding service | Document chunks and retrieval queries | Embedding endpoint and model |
| Memory worker model | Conversation content to summarize | Memory worker model and endpoint |
| Search / page-fetch provider | Search queries and requested URLs | Search and fetch backends |
| Tool callback / connector | Inputs required by the operation | Callback URL, credentials, tool policy |
| Runtime stores | Documents, conversations, memory, jobs, and audit records | Database, filesystem, access, retention, and backups |

For fully offline operation, configure local models and embeddings, use
compatible local tools, and enforce the intended network boundary. An offline
license does not make a hosted model available offline. See
[Model settings](/model-settings) and [Portability](/portability).

## Identity and access

Authenticate requests with a deployment-issued credential. Agent ownership,
collection restrictions, and approval-group membership serve different purposes.
`owner_employee` supplies an agent's shared defaults; it is not a replacement
for user authorization or a tenant identifier.

End-user identity overrides are accepted only for authorized integration
callers. Follow [Managing memory](/managing-memory#who-the-memory-belongs-to)
before routing several users through a shared credential.

## Screening, grounding, and approvals

The firewall and configured guardrails screen requests and responses. They
reduce risk; they do not prove that every output is correct or contains no
sensitive information.

Inspect grounding and source evidence when the application needs a sourced
answer. No retrieval, weak retrieval, and unread web sources are different
outcomes. A model can answer without a source; see [Web search](/web-search).

Declare side effects and risk on tools, configure the applicable approval
policy, and follow the action's execution outcome. A prompt asking for approval
or an `approval_group` field alone does not implement every escalation workflow.
A completed chat or job does not mean an external action executed.

[Desk's audit trail](/desk-audit) describes the action ledger and its access and
retention behavior. Database operators still control the underlying storage;
do not confuse API-level restrictions with tamper-proof storage.

## Reporting a vulnerability

Follow the [security policy](https://github.com/libraos/community/security/policy)
for private disclosure, or email `contact@meganova.ai`.
