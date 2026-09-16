---
slug: /editions
sidebar_position: 3
title: Cloud vs Self-Hosted
description: Choose who operates Libra OS, where its stores run, and which external services process your data.
---

# Cloud vs Self-Hosted

Both editions use the Libra OS runtime and agent-definition format. Choose
based on who operates the deployment and where data may be stored and processed.

| | Cloud | Self-Hosted |
| --- | --- | --- |
| Start | [Request private-beta access](/cloud) | [Install and configure the server](/getting-started) |
| Operations | Managed during onboarding and service operation | Your team runs and updates it |
| Storage | Assigned managed environment | Your configured databases and filesystem |
| Model processing | Configured providers and service terms | Hosted providers or local models you configure |
| Offline operation | Confirm available deployment options | Requires local models, embeddings, and compatible tools |
| Agents | Configured for your workload | Created through APIs, files, or available setup tooling |

Self-hosting does not automatically prevent outbound model, embedding, search,
or callback traffic. See [Security](/security).

## Same interfaces, environment-dependent capabilities

An application can use the same API shapes against either edition, but must
supply the correct base URL, credential, and installed agent ID. The available
models, tool services, persistence, permissions, and release versions can differ.
Check [Portability](/portability) before moving an integration.

## Moving between editions

1. Export the employee/agent definitions and the supported knowledge bundle.
2. Provision the destination runtime and its stores.
3. Import definitions and knowledge; verify collection bindings.
4. Configure destination credentials, model IDs, tool callbacks, and ownership.
5. Run your integration and evaluation checks before redirecting traffic.

An employee bundle does not promise to move all conversation history,
observational memory, job state, audit records, or external credentials.
Plan those separately if your migration needs them.

For current access and commercial terms, see [Cloud](/cloud) and
[pricing](https://libraos.com/pricing/).
