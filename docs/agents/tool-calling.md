---
slug: /tool-calling
sidebar_position: 5
title: Call your systems with tools
description: Connect an agent to a signed callback, then verify the tool ran and its result supports the answer.
---

# Call your systems with tools

An agent can ask your application to look up an order, check an account, or
perform another narrowly defined operation. LibraOS sends the tool call to
your callback and returns the result to the agent. Your application still
owns the business data and decides whether the caller may access it.

Start with the runnable [Order Lookup recipe](https://github.com/libraos/cookbook/tree/main/recipes/tool-calling).
It includes a signed webhook, a client, offline tests, and live checks for a
known order, a missing order, and an unavailable webhook.

## What you need

- **Kernel v0.3.0 or later.** Earlier releases could accept `custom_tools` on
  `POST /v1/agents` without making them available to the model. Check
  `/api/version` on the deployment you will use.
- A model that supports tool calls, and an application endpoint the Runtime
  can reach. For a remote callback, use HTTPS and allow its host in the Runtime
  configuration.
- A callback secret held by the Runtime and your webhook. Put its environment
  variable name in `secret_ref`; do not put the secret in the agent definition.

## Register the agent

The managed-agent route is `POST /v1/agents`. This is a definition excerpt;
the [recipe](https://github.com/libraos/cookbook/tree/main/recipes/tool-calling)
supplies the working callback service and complete request.

```json
{
  "name": "order-lookup",
  "brain": false,
  "tool_scope": "none",
  "tool_choice": "order_lookup",
  "system": "Look up the requested order. Report only the tool result.",
  "custom_tools": [{
    "name": "order_lookup",
    "description": "Read one order by its order_id.",
    "input_schema": {
      "type": "object",
      "required": ["order_id"],
      "properties": {"order_id": {"type": "string"}},
      "additionalProperties": false
    },
    "side_effects": false,
    "callback": {
      "url": "https://your-app.example/callback/",
      "auth": {
        "type": "hmac_sha256",
        "secret_ref": "LIBRA_OS_CALLBACK_SECRET_COOKBOOK"
      }
    }
  }]
}
```

`tool_choice` asks the model to call `order_lookup` first. `tool_scope: "none"`
keeps catalog tools out of this agent; its declared custom tool remains
available. Check that the registration response contains `order_lookup` in
`custom_tools`. A successful HTTP response by itself does not prove the tool
was registered.

Agent files and the managed API have different accepted fields. If you are
using a file instead, see [Employees and agents in YAML](/employee-yaml#skills-and-tools).

## Call and verify

Invoke the agent by its route ID on `POST /agents/v1/order-lookup/chat`.
For a stateless lookup, send `no_memory: true` so a previous answer cannot
substitute for a fresh lookup. `include_metadata: true` returns the
`tool_transcript` for server-side verification:

```json
{
  "message": "Look up order ORD-5591.",
  "no_memory": true,
  "include_metadata": true
}
```

Before showing a status to a user, check all of the following:

1. The transcript has an `order_lookup` call with the **exact** requested
   `order_id` and a nonempty call ID.
2. A tool result carries that same call ID. For a delivered result, its
   `order_id`, `found` boolean, and status agree with the answer.
3. The webhook has a new receipt for that verified callback. A plausible
   answer alone is not evidence that your system was queried.

Treat a missing, malformed, or contradictory result as a failed request. Do
not turn it into `not_found`: that would tell a customer their order does not
exist when the lookup may not have run. Keep tool transcripts on the server
side if they contain business data.

The recipe's [validation record](https://github.com/libraos/cookbook/blob/main/docs/validation.md#verification-record--2026-10-29-tool-calling)
reports different pass rates for different models under the documented test
configuration. Recheck your selected model and Runtime release before using
the workflow with customers.

For tools that change business records, declare their side effects and test
authorization, approval, rejection, and idempotency separately. A signed
callback proves where the request came from; your backend must still decide
whether that caller may access or change the specific record. See the
[customer support guide](/guides/customer-support#step-4--connect-your-systems-with-tools)
for a larger integration and [Security](/security) for the trust boundaries.
