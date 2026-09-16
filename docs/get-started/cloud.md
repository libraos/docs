---
slug: /cloud
sidebar_position: 2
title: Libra OS Cloud
description: Private-beta access to a managed Libra OS deployment and the information developers need to connect.
---

# Libra OS Cloud

Libra OS Cloud is the hosted edition, currently available through **private-beta
onboarding**. Request access at [libraos.com/signup](https://libraos.com/signup/).
Submitting that form requests an invitation; it does not immediately provision
a workspace.

To start without an invitation, use [Self-Hosted](/getting-started).

## Before you integrate

Your onboarding contact supplies your deployment URL, supported server version,
credentials, and available model configuration. Use those values rather than
assuming a workspace hostname, a default agent, or a particular model is present.

The runtime APIs follow the same conventions as Self-Hosted. Feature availability
also depends on release version, configured services, and enabled tools.
See [Cloud vs Self-Hosted](/editions) and [Portability](/portability).

## Connect your application

Set the URL and bearer credential you received:

```bash
export LIBRA_OS_URL=https://your-assigned-host.example
export LIBRA_OS_API_KEY='your-bearer-token'
```

Follow [Create your first agent](/creating-an-agent) to create and call an agent,
or call an existing agent using the ID supplied by your operator.
The Python SDK is asynchronous: use `await client.messages.create(...)` inside
an async function and an `async with Client(...)` context.

Employees and agents are configured for your workload. Setup-generated
definitions and templates are editable starters; there is no fixed eight-person
team that applications should assume exists.

## Add your knowledge

Upload documents, create collections, and bind them to your agents using
[Workspaces & memory](/workspaces-memory). A website crawler or other connector
must be configured and available before it can import content. A Cloud
invitation by itself does not connect your website or populate a knowledge base.

## Move between deployments

Export the employee and agent definitions and supported bundle contents,
import them into the destination, then configure credentials, callbacks,
models, and storage for that environment. Verify collection bindings and run
your evaluation set. A bundle is not a backup of conversations, jobs, audit
history, or every external service.

See [portability](/portability) for environment-dependent features. Confirm
current availability and commercial terms during onboarding rather than
relying on a fixed price or free-tier allowance in an integration guide.
