---
slug: /customization
sidebar_position: 4
title: Customization & extension points
description: Map a desired behavior change to application code, APIs, agent files, knowledge bindings, tools, policy, or deployment configuration.
---

# Customization & extension points

Customize Libra OS through published contracts. Internal services, prompts,
database tables, and source modules are not extension points and can change
without compatibility guarantees.

| Change you need | Change this layer | Verify with |
| --- | --- | --- |
| Change the UI or business workflow | Your application code | UI and integration tests |
| Change an agent's instructions, model, tools, output, or limits | Supported managed-agent API or declarative agent file | Agent evaluation plus a request through the installed endpoint |
| Share defaults across agents | Employee configuration or house profile, according to the intended scope | Effective configuration and an identity-scoped test |
| Add or update documents | Collection and document APIs or a supported connector | Retrieval capability response and retrieval test |
| Decide which knowledge an agent can use | Agent bindings and collection authorization | Positive and negative authorization tests |
| Call a business system | A narrowly scoped tool callback or application-side adapter | Contract, authorization, failure, and idempotency tests |
| Change whether an external action needs review | Tool risk and approval policy | Dry-run, approval, execution-result, and audit tests |
| Change model routing | Server and per-agent model settings | Effective model configuration and representative evaluations |
| Retain a known structured value | `output_type` with declared persisted fields and scope | Cross-turn, cross-user, reset, and deletion tests |
| Retain general observations | Operator-enabled observational memory | Identity-isolation, latency, retention, and removal tests |
| Run work beyond one connection | Native jobs API | Submit-once, reconnect, duplicate-event, failure, and outcome tests |
| Change deployment services | Documented environment and deployment configuration | `libraos doctor deployment` and `GET /api/capabilities` |

## Choose the narrowest supported entry point

- Put presentation and business-state transitions in the application.
- Put executable agent behavior in an agent definition.
- Put reusable operating guidance in the supported shared configuration for its
  intended scope.
- Put documents in knowledge collections, not in prompts or memory by default.
- Put external side effects behind a typed tool with explicit policy.
- Read capability and outcome fields instead of inferring success from a 2xx
  response, stream event name, backend name, or completed model turn.

## Keep a project-specific file map

Public documentation cannot name files in an application it does not own. Each
application repository should maintain a file map using real paths from that
repository:

```md
| Change | File or configuration | Contract | Verification |
| --- | --- | --- | --- |
| Change agent behavior | <actual path> | Agent schema/API | Agent evaluation |
| Add a business field | <actual migration and API path> | Application schema | Migration test |
| Add an external operation | <actual adapter path> | Tool contract | Authorization test |
| Add a knowledge source | <actual connector/binding path> | Collection API | Retrieval test |
```

Do not copy example paths into a customer repository. Generate or review this
table against the actual code, migrations, configuration, and tests whenever
the project structure changes.

## When the public contract is insufficient

First confirm the installed server and SDK versions and inspect the published
OpenAPI contract. If the required field or behavior is absent, treat it as an
unsupported capability rather than editing runtime internals and documenting
that edit as a stable integration.

Start with [Build on Libra OS](/build-on-libraos), [Calling agents](/calling-agents),
and the [Portability contract](/portability).
