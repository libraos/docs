---
slug: /employee-yaml
sidebar_position: 3
title: Defining employees in YAML
description: Advanced — the filesystem-canonical definition format for employees and agents; Markdown files with YAML frontmatter, hot-reloaded by the runtime.
---

# Defining employees in YAML

The SDK calls in [Create your first agent](/creating-an-agent) are one way to
define employees and agents. The other — and the source of truth on disk — is
**declarative files**: Markdown documents with YAML frontmatter that the
runtime loads at boot and hot-reloads on change. Check them into git, review
them in pull requests, and `cp` them between deployments.

Two directories, one format:

| Directory | Defines | The Markdown body becomes |
| --- | --- | --- |
| `data/employees/<id>.md` | An **employee** — the identity that owns agents and carries shared config | Dashboard description (the YAML `description` stays authoritative) |
| `data/agents/<id>.md` | An **agent** — a runnable behavior | The agent's **system prompt** |

Ready-made templates for nine specialist personas (marketing, support,
analytics, operations, finance, communications) live in the SDK repo's
[employees playbook](https://github.com/libraos/sdk/tree/main/employees) —
`cp employees/<vertical>/<name>.md ./data/agents/` works without conversion.

## An employee file

```yaml
# data/employees/frontdesk.md
---
id: frontdesk
display_name: Front Desk
description: Client-facing intake and triage for the practice.
model_config:
  answer:
    primary: anthropic/claude-opus-4-7
    fallback: [gemini/gemini-2.5-flash]
  planner:
    primary: anthropic/claude-opus-4-7
  skill:
    primary: gemini/gemini-2.5-flash-lite
callback:
  url: https://your-app.example/libraos/tools   # employee-level catch-all webhook
---
Front Desk owns the intake specialist and triage agents. This body text
renders on the dashboard; the YAML description above is what the runtime uses.
```

Employee fields: `id` (required), `display_name`, `description`,
`model_config`, `web_search_config`, `callback`, `owner` (email; empty means
admin-only). Everything an employee declares is a **default its agents
inherit** — the cascade is resolved per slot, so an agent can override
`answer` and still inherit `planner` from its owner.

## An agent file

Condensed from the playbook's
[`financial-analyst`](https://github.com/libraos/sdk/blob/main/employees/finance/financial-analyst.md)
template:

```yaml
# data/agents/financial-analyst.md
---
name: financial-analyst
description: Financial analyst — model reviews, variance analysis, KPI summaries.
delegation_hint: Use for quantitative financial analysis; NOT for legal or compliance questions.
agent_type: persona          # persona = multi-turn; skill = single delegated call
brain: true                  # allow the planner tier to decompose tasks
owner_employee: frontdesk    # inherit model slots from this employee
max_turns: 8
max_output_tokens: 8192
skills:
  - skill_deep_research
  - skill_report
capabilities:
  - financial_modeling
  - variance_analysis
model: gemini/gemini-2.5-flash   # legacy single-model field; model_config wins if both set
---

# Financial Analyst

You are a **Financial Analyst** — a digital employee specializing in
financial analysis, valuation, and investment research.

## Rules
- Show assumptions — every projection must state them explicitly
- Cite sources — earnings data from filings, prices from market data
```

Everything below the closing `---` is the system prompt.

## Agent field reference

The stable, partner-facing fields, grouped by what they control. All are
optional unless marked; absent fields keep safe defaults.

### Identity and routing

| Field | Meaning |
| --- | --- |
| `name` | Identifier slug (kebab-case) for new agents; display name for legacy files whose slug is in `agent_id`/`id` |
| `description` | Shown in pickers and used by the planner when no hint is set |
| `delegation_hint` | Planner-facing "when to use this agent" — separate from `description` because the routing model and the UI need different text |
| `agent_type` / `type` | `skill` (single call) or `persona` (multi-turn) |
| `brain` | `true` lets the planner tier decompose work across skills |
| `category` | Classification class (`legal`, `bi`, …) for optional re-routing |
| `owner_employee` | Employee whose `model_config`/`web_search_config`/`callback` this agent inherits per slot |
| `owner` | Owning user's email; empty = admin-only |

### Models

`model_config` has three slots — `answer`, `planner`, `skill` — each with a
`primary` and an optional `fallback` chain. Model ids always carry a
`provider/` prefix. Resolution cascades **per slot**:
per-call → per-skill → per-agent → per-employee → server default. The legacy
single `model:` field still works; `model_config` takes precedence when both
are present. On a token plan, use the covered ids — see
[Model settings & token plans](/model-settings).

### Skills and tools

| Field | Meaning |
| --- | --- |
| `skills` (alias `tools`) | Skills the agent can delegate to. Each runs as its own skill agent with its own prompt, dispatched by the planner |
| `direct_tools` | The escape hatch: attach a skill's tool definitions to the agent's **own** LLM call, so the agent's prompt governs how the tool is used (e.g. "print base64 inline") |
| `capabilities` | Free-form capability tags used for discovery and routing |
| `custom_tools` | Partner-defined tools: `name`, `description`, `input_schema` (JSON Schema), optional per-tool `callback`, plus side-effect declarations (`risk_tier`: low/medium/high, dry-run support) that gate the approval path |
| `callback` | Agent-level webhook for custom tools; cascade is tool → agent → employee |

### Knowledge

| Field | Meaning |
| --- | --- |
| `knowledge_bindings` | Collections this agent is bound to, declared inline and reconciled with the server on load |
| `allowed_collections` | Retrieval restriction. When a pack also restricts, the effective list is the **intersection** — neither side can widen the other |
| `knowledge_gate` / `knowledge_gate_min_score` | Retrieval-confidence gate: below the score floor, the planner is consulted before answering from thin evidence |

### Output, filesystem, conversation

| Field | Meaning |
| --- | --- |
| `output_type` | Structured-output contract: `schema_path` (file relative to `data/agents/`), `schema_url`, or `schema_inline` (literal JSON Schema), with `on_violation: error \| log \| repair` |
| `filesystem.enabled` | `true` provisions a workspace and registers the six filesystem tools |
| `max_turns` (alias `maxTurns`) | Agentic-loop turn cap |
| `max_output_tokens` | Per-agent output cap; overrides per-skill defaults so long deliverables (memos, reports) don't truncate |
| `persona` | Structured persona block: `background`, `voice`, `traits` |
| `hooks` | Per-agent lifecycle hooks |

### Visibility and UX

| Field | Meaning |
| --- | --- |
| `published` | Opt into curated picker surfaces (default `false` — hidden from the end-user dropdown, still callable) |
| `disabled` | Hide from the model catalog entirely; stays reachable by id for existing wiring |
| `visibility` | `private` (owner + admins, default) or `public` (any authenticated user can read); the public surface is additionally gated server-wide by an operator flag |
| `approval_group` | Binds the agent to an approval group so pending actions route to the right humans |
| `stream_phase_markers` | Stream human-readable phase updates ("analyzing your document…") for personas whose answers take >30s |
| `accepts_attachments` | Opt-in gate for receiving validated attachment references |
| `route_templates` | Named URL templates your front end supports, which the planner can fill into navigation hints (`/workspace/cases/{case_id}/intake`) |
| `web_search_config` | Per-agent search backend, fallback chain, and recency escalation (cascades agent → employee → server default) |

## Loading and reloading

- Files load at boot; the runtime **hot-reloads** on change (SIGHUP, or the
  management API's PATCH endpoints, which write back to the same files — the
  filesystem stays canonical).
- The SDK's `employees.create` / `agents.create` calls from the
  [tutorial](/creating-an-agent) create these same records; defining them as
  files is the declarative, reviewable equivalent — the same split as config
  files vs. API calls anywhere else.
- Legacy field names (`agent_id`, `id`, single `model:`) keep working; the
  identifier is resolved as `agent_id` → `id` → `name`. Prefer the canonical
  names shown above for new files.

## Start from a template

Customer support is the most common first deployment — inquiry triage,
troubleshooting, and ticket summaries map directly onto a single persona
agent with `knowledge_base_lookup` grounded in your own product docs:

```bash
git clone https://github.com/libraos/sdk
cp sdk/employees/support/customer-support.md ./data/agents/
# edit the frontmatter (model_config, knowledge_bindings), reload, done
```

Templates ship without a pinned `model:` — the agent inherits your
deployment's default (server `OPENAI_MODEL`, or the owning employee's
`model_config`), so the copy works as-is on any gateway. If you do pin a
model in the frontmatter, use an id **your gateway actually serves**, or the
agent 404s at call time.

The template ships with `agent_type: persona`, `brain: true`, and the
`support_qa` / `troubleshooting` / `ticket_summarization` /
`knowledge_base_lookup` capabilities — bind it to your product-docs
collection via `knowledge_bindings` and it answers from your sources,
citations included. Pair it with the `email-classifier` template
(communications) when you also want inbox triage and routing in front of it.

The full path from this template to production — grounding, ticket-system
tools, escalation, evaluation — is the
[customer support agent guide](/guides/customer-support).

The nine playbook templates cover support, communications, marketing,
analytics, operations, and finance — see the
[catalog](https://github.com/libraos/sdk/tree/main/employees) for what each
one does and its recommended skills.
