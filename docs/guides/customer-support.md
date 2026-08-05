---
sidebar_position: 1
title: Customer support agent
description: Production guide — a support agent grounded in your product docs, wired into your ticket system, with human escalation and repeatable evaluation.
---

# Customer support agent

Build a support agent that answers product questions **from your own docs with
citations**, stays on topic, takes real actions (order lookups, ticket
creation) through your existing systems, and hands anything past its scope to
a human — with the review trail becoming your compliance record. It runs
inside your deployment, so customer conversations and the data inside them
never leave your network.

## Prerequisites

- A running Libra OS deployment — see [Getting started](/getting-started)
- **Python 3.10+** and the SDK: `pip install libraos-sdk`
- A Libra OS API key:

```bash
export LIBRA_OS_URL=https://libraos.your-company.example
export LIBRA_OS_API_KEY=msk_live_...
```

## Before you build

### Decide whether to automate support

Indicators that an agent should take part of the load:

- **High volume of repetitive queries** — the agent absorbs the routine;
  human agents keep the complex cases.
- **Answers live in documentation** — product docs, policy wording, FAQs:
  exactly what knowledge grounding retrieves and cites.
- **24/7 coverage and demand spikes** — an agent doesn't staff a night shift.
- **Consistent brand voice** — one reviewed persona file instead of per-agent
  variation.

And the indicators specific to choosing **Libra OS** as the substrate:

- **The conversations can't leave your network** — support chats carry
  account data, order history, sometimes regulated PII.
- **Answers must be attributable** — every claim traces to a source document,
  so a support lead can verify what the agent told a customer.
- **Actions need sign-off** — refunds, cancellations, and escalations go
  through a human queue by construction, not by convention.

### Define your ideal interaction

Write the conversation you want before configuring anything — it determines
which tasks, tools, and knowledge the agent needs. A worked example for a
product-support flow:

- **Customer:** opens chat → **Agent:** greets, states what it can help with
- **Customer:** "Does the Pro plan support SSO?" → **Agent:** answers from
  the product docs, citation attached
- **Customer:** "Where's my order?" → **Agent:** calls `lookup_order`,
  synthesizes the status into a plain-language answer
- **Customer:** asks something off-topic → **Agent:** declines briefly,
  steers back to product support
- **Customer:** "This is the third time this broke, I want to talk to
  someone" → **Agent:** files a ticket via `create_ticket` (which lands in
  the approval queue) and escalates to a human with the conversation summary
- **Customer:** follow-up questions → **Agent:** answers, closes out

Write the actual sentences for your version — it fixes the tone, response
length, and level of detail you'll put in the persona file.

### Break the interaction into tasks

Each line above is a distinct task you'll configure — and later evaluate —
separately:

1. **Greeting and general guidance** — persona prompt
2. **Product Q&A with citations** — knowledge grounding
3. **Conversation management** — on-topic rules in the prompt; the firewall
   backstops injection and abuse
4. **Taking action** — custom tools against your order/ticket systems
5. **Escalation** — approval groups and an explicit escalation rule

### Establish success criteria

Set targets with your support team before shipping. Task metrics:

| Metric | Target |
| --- | --- |
| Query comprehension accuracy | ≥ 95% |
| Response relevance (LLM-graded sample) | ≥ 90% |
| Answer accuracy vs. the cited source | 100% — a cited claim must match its source |
| Citation provision where beneficial | ≥ 80% of interactions |
| Topic adherence | ≥ 95% |
| Escalation accuracy (escalated when it should) | ≥ 95% |

Business metrics: deflection rate (typically 70–80% target), CSAT ≥ 4/5,
average handle time below your human baseline, and sentiment maintained or
improved across the conversation.

## What the platform already handles

Building this directly on a model API means assembling a prompt scaffold, a
RAG pipeline, a tool-use loop, guardrails, and an escalation path yourself.
On Libra OS those are configuration:

| You'd normally build | On Libra OS |
| --- | --- |
| System prompt engineering, brand voice | The persona template — a reviewed Markdown file you edit |
| RAG pipeline (chunking, embedding, retrieval, citation) | Knowledge collections + `knowledge_bindings`; every answer cites its source |
| Guardrails against prompt injection, PII leaks, off-topic drift | The 3-tier AI firewall screens every request and response |
| Tool-use loop + API integration code | `custom_tools` with a webhook callback — no client-side loop |
| Human-in-the-loop approval flow | `approval_group` + side-effect declarations on tools |
| Per-customer conversation memory | Automatic — keyed on the (API key, end user, agent) triple |
| Chat UI | Any OpenAI-compatible chat client, pointed at the agent |
| Evaluation harness | The SDK's synthetic-customer simulator |

## Step 1 — Install the template

```bash
git clone https://github.com/libraos/sdk
cp sdk/employees/support/customer-support.md ./data/agents/
```

The template arrives as a multi-turn persona (`agent_type: persona`,
`brain: true`) with the `support_qa`, `troubleshooting`,
`ticket_summarization`, and `knowledge_base_lookup` capabilities and a
complete support-specialist system prompt in the body.

## Step 2 — Write the persona

The Markdown body below the frontmatter **is** the system prompt. Structure
it the way you'd structure any strong support prompt — identity, static
context, examples, guardrails — but in one reviewable file instead of
concatenated Python strings:

```markdown
# Support Specialist

You are Eva, the support specialist for Acme. Warm, precise, and
solution-oriented. You resolve issues on first contact when possible.

## What you know
Business hours: Mon–Fri 9–5 EST. Phone support: 1-800-123-4567.
Products: Starter, Pro (adds SSO, audit log), Enterprise (adds on-prem).
Detailed product behavior comes from the knowledge base — search it and
cite it; do not answer product questions from memory.

## Example interactions
H: Do you offer a self-hosted version?
A: Yes — the Enterprise plan includes on-prem deployment. Would you like
   me to summarize what that involves, or connect you with the team?

H: I've been waiting two weeks for my order.
A: Let me check that for you right away. [calls lookup_order]

## Rules
1. Answer only from the knowledge base or tool results — cite the source.
2. Off-topic requests: decline briefly and return to product support.
3. Never make commitments (refunds, discounts, timelines) yourself —
   file the request and tell the customer it's with the team.
4. On the third repeated complaint, or on request, escalate to a human.
```

Include 4–5 example interactions covering the tricky cases: the product you
*don't* offer, the implicit request, the escalation trigger. The examples do
more for consistency than any instruction.

Two guardrails you do **not** need to write: prompt-injection screening and
PII redaction run in the firewall on every request and response, outside the
prompt where a jailbreak can't negotiate with them.

## Step 3 — Ground it in your product docs

Create a knowledge collection, upload your documentation (the SDK's
[`03_upload_knowledge.py`](https://github.com/libraos/sdk/blob/main/python/examples/03_upload_knowledge.py)
shows the upload flow), and bind the agent to it:

```yaml
knowledge_bindings: [product-docs]
allowed_collections: [product-docs]   # retrieval restricted to this collection
knowledge_gate: true                  # below the confidence floor, don't answer from thin evidence
```

`knowledge_bindings` attaches the collection; `allowed_collections` is the
restriction — the agent cannot retrieve outside it, so a support agent can
never answer from, say, the finance team's collection. With `knowledge_gate`
on, weak retrieval triggers the planner instead of a confident-sounding guess.

This is also the latency-and-cost answer: retrieval pulls only what the
question needs, instead of stuffing the full product manual into every
prompt.

## Step 4 — Connect your systems with tools

Declare real actions as `custom_tools` with a webhook callback — your
endpoint executes the call with its own credentials; the agent never holds
them, and **your chat client never runs a tool loop** (contrast with
API-level integrations, where your code must catch `tool_use` blocks,
execute, and re-send — here the runtime dispatches to your webhook
mid-conversation and the answer comes back synthesized):

```yaml
custom_tools:
  - name: lookup_order
    description: Fetch an order's status and history by order id.
    input_schema:
      type: object
      properties:
        order_id: { type: string }
      required: [order_id]
  - name: create_ticket
    description: File a support ticket in the tracker.
    input_schema:
      type: object
      properties:
        summary:  { type: string }
        severity: { type: string, enum: [low, medium, high] }
      required: [summary, severity]
    side_effects: true
    risk_tier: medium          # gates the approval path
callback:
  url: https://your-app.example/libraos/tools
```

`lookup_order` is read-only and runs freely. `create_ticket` declares
`side_effects: true` with a risk tier — it routes through the approval path
instead of firing silently. The
[legaltech example](https://github.com/libraos/sdk/tree/main/examples/legaltech)
shows a complete webhook implementation (FastAPI, idempotency, signature
verification).

## Step 5 — Talk to it

Your integration is a plain chat call — no tool loop, no RAG plumbing:

```python
import os
from libraos import Client

async def answer(customer_id: str, history: list[dict]) -> str:
    async with Client(
        base_url=os.environ["LIBRA_OS_URL"],
        api_key=os.environ["LIBRA_OS_API_KEY"],
    ) as c:
        resp = await c.messages.create(
            agent_id="customer-support",
            messages=history,                    # [{"role": "user", "content": ...}, ...]
            headers={"X-End-User": customer_id}, # per-customer memory scope
        )
        return resp["content"]
```

The `X-End-User` header scopes memory per customer — each gets an isolated
history, and the agent remembers *their* prior tickets, with no session
plumbing on your side.

**Or skip the custom front end entirely.** Every agent is exposed as an
OpenAI-compatible model, so any chat client that speaks that protocol can
front it — including streaming:

```bash
curl -N $LIBRA_OS_URL/v1/chat/completions \
  -H "Authorization: Bearer $LIBRA_OS_API_KEY" \
  -H "X-End-User: cust_4812" \
  -d '{
    "model": "customer-support",
    "stream": true,
    "messages": [{"role": "user", "content": "Does the Pro plan support SSO?"}]
  }'
```

Set `published: true` in the frontmatter to list the agent in curated picker
surfaces; with `stream_phase_markers: true`, long operations stream
human-readable progress ("searching the knowledge base…") instead of a
silent spinner.

## Step 6 — Triage in front, routes out the back

- **Inbound:** put the
  [`email-classifier`](https://github.com/libraos/sdk/blob/main/employees/communications/email-classifier.md)
  template in front for inbox triage — classify intent, then hand the
  conversation to the support persona (or a human) by category. The full
  routing setup — taxonomy, structured outputs, accuracy targets — is the
  [ticket routing guide](/guides/ticket-routing). This is also the scaling
  path when one agent accumulates too many jobs: specialized personas behind
  a classifier, each with its own tools and prompt.
- **Outbound:** declare `route_templates` so the agent can send your UI
  somewhere concrete instead of describing where to click:

```yaml
route_templates:
  ticket_detail: "/support/tickets/{ticket_id}"
  order_status:  "/orders/{order_id}"
```

## Step 7 — Keep humans in the loop

```yaml
approval_group: support-leads
```

Binding the agent to an approval group means side-effecting tool calls (the
`create_ticket` above), low-confidence answers, and anything the agent
escalates land in that group's queue. This is the supervision bound the
platform is built around: the agent closes the routine tickets; the judgment
calls reach people — and the approval trail is auditable after the fact.

## Step 8 — Evaluate before (and after) you ship

Score the agent against the success criteria you set earlier, per task —
comprehension, relevance, citation, adherence, escalation. Two loops, both
off your production instance:

1. **Scripted checks** — a fixed set of prompts per task with expected
   behaviors (answers cite the right doc; the off-topic probe gets declined;
   the "I want a human" message escalates). Rerun on every prompt or
   `model_config` change.
2. **Synthetic customers** — the SDK's
   [simulator](https://github.com/libraos/sdk/tree/main/examples/simulator)
   plays multi-turn customers from archetype YAML files, each with hidden
   facts the agent must elicit — realistic information asymmetry, not happy
   paths. Write archetypes for your top ticket categories, including a
   frustrated repeat-contact customer and an implicit-request customer.

For relevance and comprehension at scale, use LLM-graded scoring over a
conversation sample rather than hand-review — and spot-check the grader.

## Improve performance

- **Latency** — set `model_config` per slot: a capable `planner`, a fast
  `answer` tier; the cascade handles fallbacks. On a token plan use the
  covered ids ([Model settings](/model-settings)). Streaming (above) removes
  most *perceived* latency.
- **Long troubleshooting answers truncating** — raise `max_output_tokens` in
  the frontmatter.
- **Off-topic drift or tone slip** — add the failing case to the example
  interactions in the persona body; examples beat instructions.
- **One agent doing too much** — split behind the classifier (Step 6) into
  specialized personas with their own tools and prompts.
- **Commitments and competitor mentions** — keep the "never commit, file it
  instead" rule in the persona; the firewall handles the adversarial cases,
  the prompt handles the polite ones.

## Next steps

- **[Ticket routing](/guides/ticket-routing)** — the classifier that fronts
  this agent
- **[Defining employees in YAML](/employee-yaml)** — the full field reference
  for everything configured above
- **[Create your first agent](/creating-an-agent)** — the same setup via SDK
  calls instead of files
- **[Security](/security)** — what the firewall screens on every request
