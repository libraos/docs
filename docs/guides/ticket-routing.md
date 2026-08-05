---
sidebar_position: 2
title: Ticket routing
description: Production guide — classify and route inbound tickets at scale with the email-classifier template, structured outputs, and measurable routing accuracy.
---

# Ticket routing

Classify inbound support tickets by intent, urgency, and required expertise —
and route them to the right team — using the
[`email-classifier`](https://github.com/libraos/sdk/blob/main/employees/communications/email-classifier.md)
template. Routing runs inside your deployment, so ticket contents (and the
customer data inside them) never leave your network.

## Prerequisites

- A running Libra OS deployment and an API key
- The SDK: `pip install libraos-sdk`, with `LIBRA_OS_URL` /
  `LIBRA_OS_API_KEY` exported
- Access to your existing ticketing system (and its webhook or polling API)
- **A sample of historical tickets with their human routing decisions** — this
  becomes your evaluation set

## Before you build

### Understand your current routing approach

The classifier automates a judgment your team already makes — so document
that judgment first. Sit with the support team and answer:

- What criteria decide which SLA or service tier applies?
- Does routing choose a support tier, a product specialist, or both?
- What automated rules already exist, and **where do they fail** — those
  failures are your first edge-case tests
- How are ambiguous or multi-issue tickets handled today?
- How does the team prioritize when queues back up?

The more precisely you can describe how humans route, the better the
classifier's instructions and examples will be.

### Why an LLM classifier instead of traditional ML

- **Limited labeled data** — a few dozen examples in the prompt replace the
  massive labeled dataset a trained classifier needs.
- **Categories evolve** — edit the taxonomy table and reload; no relabeling
  and retraining cycle.
- **Unstructured, messy input** — no feature engineering; the classifier
  reads the ticket the way a person does.
- **Rules defined by conditions, not examples** — "anything mentioning a
  regulator goes to compliance" is one line of instruction.
- **Interpretable decisions** — every classification carries human-readable
  reasoning, which builds trust and shows you exactly what to fix.
- **Ambiguity handled, not dumped** — nuanced tickets get interpreted in
  context rather than defaulting to a catch-all bucket; genuinely ambiguous
  ones report low confidence instead of guessing.
- **Multilingual by default** — one classifier for every language your
  customers write in.

And the Libra OS-specific reason: tickets contain names, account details, and
sometimes regulated data — here classification runs on your hardware with the
firewall screening every request, instead of shipping every ticket to a
vendor cloud.

### Define your intent taxonomy

Routing accuracy is directly proportional to how well-defined your categories
are. Start broad, with subcategories where different destinations need them:

| Category | Subcategories | Routes to |
| --- | --- | --- |
| `technical` | hardware, software bug, compatibility, performance | Product support tier |
| `account` | password reset, access, subscription changes | Account team |
| `billing` | payment failure, refund, plan change, invoice | Billing |
| `product_info` | features, pricing, availability | Sales-assist |
| `order` | status, shipping, returns, modifications | Fulfillment |
| `feedback` | bug report, feature request, complaint | Product / CX |
| `security` | suspicious activity, privacy inquiry | Security (priority) |
| `compliance` | regulatory, legal documentation | Legal |
| `emergency` | outage, critical failure, urgent security | On-call (immediate) |
| `escalation` | supervisor request, formal complaint, attorney | Human queue |

Intent is rarely the whole routing decision — **urgency, customer tier,
SLA, and language** often modify it. Capture those as separate output fields
(next section) rather than multiplying categories: `billing × critical ×
enterprise-customer` should be three fields, not one category.

Rules that keep accuracy high: exactly one category per ticket (and state
which intent wins when a customer raises several), keep the `escalation`
catch-all, and put 2–3 real anonymized tickets per category into the template
body as few-shot examples — with a one-line rationale each, which helps the
classifier generalize the logic.

### Establish success criteria

Set thresholds with the support team before deploying, so "is it good
enough?" is a measurement, not a debate. Classifier-specific criteria:

| Metric | How to measure | Target |
| --- | --- | --- |
| Routing accuracy | Labeled historical set | 90–95% |
| Consistency | Same standardized inputs re-run over time | ≥ 95% |
| Edge-case accuracy | Dedicated hard-ticket set | ≥ 80% |
| Multilingual delta | Accuracy drop on non-primary languages | ≤ 5–10% |
| Adaptation speed | Accuracy on a *new* category after adding examples | > 90% within 50–100 samples |
| Explainability | Human rating of the reasoning field, 1–5 | ≥ 4 |
| Bias audit | Accuracy variance across customer demographics | within 2–3% |

System-level criteria that matter regardless of method: time-to-assignment
(near-instant with push integration), rerouting rate (< 10%; best-in-class
≤ 5%), escalation rate (< 20%), first-contact resolution (70–75%+), and cost
per ticket against your current routing method.

## What the template ships

`email-classifier` is not a bare prompt — it arrives with the structure the
planning above calls for:

- A **classification taxonomy table** (categories, descriptions, trigger
  phrases) — it ships with an insurance taxonomy as a worked example; replace
  it with yours
- A per-ticket **workflow**: extract → search similar past tickets →
  classify into exactly one category → extract entities (policy #, amounts,
  dates) → assess priority → route with reasoning
- **Anti-hallucination rules**: every entity must come from the ticket text
  with a source citation; ambiguous classifications report a confidence level
  instead of guessing
- An **`escalation` category** so "supervisor", "formal complaint", and
  "attorney" reach a human by design

```bash
git clone https://github.com/libraos/sdk
cp sdk/employees/communications/email-classifier.md ./data/agents/
# edit the taxonomy table and few-shot examples in the body
```

## Step 1 — Make the output a contract, not a convention

A classifier that returns prose needs regex to parse; a classifier whose
output is malformed 1% of the time breaks 1% of your routing. Declare the
shape once in the frontmatter and let the runtime enforce it:

```yaml
output_type:
  schema_inline:
    type: object
    properties:
      intent:     { type: string, enum: [technical, account, billing, product_info,
                                         order, feedback, security, compliance,
                                         emergency, escalation] }
      priority:   { type: string, enum: [critical, high, medium, low] }
      confidence: { type: number }
      reasoning:  { type: string }
      language:   { type: string }
      entities:
        type: object
        properties:
          order_id:    { type: string }
          account_ref: { type: string }
          amount:      { type: string }
    required: [intent, priority, confidence, reasoning]
    additionalProperties: false
  on_violation: repair
```

Your routing service consumes validated JSON every time — `repair` mode fixes
malformed output instead of crashing the pipeline, `reasoning` is always
present for the audit trail, and the modifier fields (`priority`,
`language`, `entities`) carry the routing criteria that aren't intent.

## Step 2 — Pick the model for volume

Routing is high-volume and latency-sensitive; it does not need your best
model. Set a fast primary with a fallback and let the
[cascade](/employee-yaml#models) handle the rest:

```yaml
model_config:
  answer:
    primary: gemini/gemini-2.5-flash
    fallback: [anthropic/claude-haiku-4-5-20251001-Ent]
```

On a token plan, use the covered ids — see
[Model settings](/model-settings). If accuracy on hard categories lags, raise
the model for the *second*-level classifier in a cascade (below) rather than
the high-volume front door.

## Step 3 — Deploy the classify call

The routing call is one request returning validated JSON — no prompt
assembly, no regex extraction:

```python
import json
import os
from libraos import Client

async def classify_ticket(c: Client, ticket_text: str) -> dict:
    resp = await c.messages.create(
        agent_id="email-classifier",
        messages=[{"role": "user", "content": ticket_text}],
    )
    return json.loads(resp["content"])   # schema-validated by output_type

async def route(ticket: dict) -> None:
    async with Client(
        base_url=os.environ["LIBRA_OS_URL"],
        api_key=os.environ["LIBRA_OS_API_KEY"],
    ) as c:
        result = await classify_ticket(c, ticket["text"])
        assign_queue(ticket["id"], result["intent"], result["priority"])
        add_internal_note(ticket["id"], result["reasoning"])   # audit trail
        if result["intent"] == "escalation" or result["confidence"] < 0.6:
            escalate_to_human(ticket["id"], result)
```

Note the confidence gate: low-confidence classifications go to a human
*with the reasoning attached*, instead of being force-fitted into a bucket —
that is where most misroutes hide.

## Step 4 — Wire it into your ticket system

Two integration shapes, same as any routing service:

- **Push (recommended):** your ticket system's webhook (new-ticket event)
  hits your service, which runs `route()` above. Near-instant
  time-to-assignment; requires exposing an endpoint your ticket system can
  reach.
- **Pull:** your service polls for unrouted tickets on a schedule and
  classifies in batches. No public endpoint needed, but tune the interval
  against your time-to-assignment target — too fast wastes calls, too slow
  delays customers.

To let the agent *act* on the ticket system itself (assign, tag, draft a
reply), declare those operations as `custom_tools` with a webhook callback
and side-effect declarations — the same pattern as the
[customer support guide, Step 4](/guides/customer-support#step-4--connect-your-systems-with-tools).
Route `escalation`-classified tickets to an
[`approval_group`](/employee-yaml#visibility-and-ux) so they land in a human
queue with the classifier's reasoning attached.

## Evaluate against your thresholds

The structured contract makes evaluation a comparison, not a parsing
exercise. Replay your labeled historical set:

```python
async def evaluate(c: Client, test_cases: list[dict]) -> float:
    correct = 0
    for case in test_cases:
        result = await classify_ticket(c, case["text"])
        if result["intent"] == case["actual_intent"]:
            correct += 1
        else:
            print(f"MISS {case['id']}: got {result['intent']} "
                  f"({result['confidence']:.2f}) — {result['reasoning']}")
    return correct / len(test_cases)
```

Every miss prints its confidence and reasoning — read them before touching
anything. Low-confidence misses usually mean a taxonomy gap (two categories
overlap); high-confidence misses usually mean a missing or misleading
few-shot example.

Run this against the thresholds you set: overall accuracy on the full set,
the dedicated edge-case set separately, per-language slices for the
multilingual delta, and per-demographic slices for the bias audit. Rerun on
every change to the taxonomy, examples, or `model_config` — and keep all of
it **off your production instance**.

For multi-turn behavior — a customer who reveals the real issue on message
three — the SDK's
[synthetic-customer simulator](https://github.com/libraos/sdk/tree/main/examples/simulator)
plays archetypes with hidden facts; use it alongside the single-shot replay.

## Improve performance

### Use a taxonomic hierarchy for 20+ categories

As categories grow, the examples needed grow with them, and one prompt
becomes unwieldy. Split into a cascade: a top-level classifier routes to
`technical` / `billing` / `general`, and a second skill agent per branch
refines to the leaf category. Each classifier stays small, fast, and
separately editable — and you can give the hard branch a stronger model
without paying for it on every ticket. The cost is an extra hop of latency,
which is why the front door stays on the fastest model.

### Ground it in your ticket history

Few-shot examples are the strongest accuracy lever, but highly variable
tickets need more examples than a prompt can hold. The template's workflow
already includes a "search similar past tickets" step — feed it: load a
collection of resolved, labeled tickets and bind it to the classifier
(`knowledge_bindings: [ticket-history]`). Retrieval then surfaces the most
similar past cases *for the ticket at hand* — dynamic few-shot selection,
using the platform's built-in retrieval instead of a separate vector-database
integration. Refresh the collection periodically so drift in your ticket mix
shows up as new examples, not accuracy decay.

### Account for the known edge cases

Test these explicitly, and when one misses, fix it with an example in the
template body rather than more instructions:

- **Implicit requests** — "I've been waiting two weeks now…" is an
  order-status request, not venting. Include real examples of indirect asks
  *with the underlying intent and a one-line rationale*.
- **Emotion masking intent** — frustrated tickets pull the classifier toward
  the sentiment instead of the need. One instruction fixes most of it:
  *"Ignore the customer's emotional tone; classify the underlying request
  and what information they need."*
- **Multiple issues in one ticket** — state the prioritization explicitly
  (e.g. security > billing > technical > general) so the classifier ranks
  instead of dithering. The `entities` field still captures the secondary
  issue for the receiving agent.

## Next steps

- **[Customer support agent](/guides/customer-support)** — the natural
  pairing: this classifier in front, the support persona resolving what it
  routes
- **[Defining employees in YAML](/employee-yaml)** — full reference for
  `output_type`, `custom_tools`, `knowledge_bindings`, and `approval_group`
