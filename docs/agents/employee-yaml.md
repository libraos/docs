---
slug: /employee-yaml
sidebar_position: 4
title: Employees and agents in YAML
description: Advanced — the filesystem-canonical definition format for employees and agents; Markdown files with YAML frontmatter, hot-reloaded by the runtime.
---

# Employees and agents in YAML

Define employees and agents in **Markdown files with YAML frontmatter**.
The runtime loads them at boot and supports explicit reloads. Commit these
files to version control so configuration and prompts can be reviewed together.

An **employee** groups agents and supplies defaults. An **agent** executes
work. The link is `owner_employee` on the agent; applications call the agent
ID. An employee file has no executable prompt or default-agent selector.

The [SDK tutorial](/creating-an-agent) shows the managed API path. Its accepted
fields are a subset of this file format: the current managed-agent handler
uses `system` for instructions and does not persist `owner_employee`,
`model_config`, or `callback` from create/update requests. Use files for those
settings; sending unknown API fields is not proof they were applied.

Two directories, one format:

| Directory | Defines | The Markdown body becomes |
| --- | --- | --- |
| `data/employees/<id>.md` | An **employee** — the identity that owns agents and carries shared config | Dashboard description (the YAML `description` stays authoritative) |
| `data/agents/<id>.md` | An **agent** — a runnable behavior | The agent's **system prompt** |

Optional specialist **agent** templates live in the SDK repo's
[employees playbook](https://github.com/libraos/sdk/tree/main/employees) —
`cp employees/<vertical>/<name>.md ./data/agents/` copies an agent definition.
Despite the source folder's name, these are not employee identity records.
Create the destination directory first, review the tools it references, and
reload after editing. Template availability does not imply pre-installed agents.

## An employee file

Save as `data/employees/frontdesk.md` (the first line must be `---`):

```yaml
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
  url: https://your-app.example/libraos/tools   # replace before enabling custom tools
---
Front Desk owns the intake specialist and triage agents. This body text
renders on the dashboard; the YAML description above is what the runtime uses.
```

Employee fields: `id` (required), `display_name`, `description`,
`model_config`, `web_search_config`, `callback`, `owner` (email; empty means
admin-only). The inheritable runtime settings are `model_config`, `web_search_config`,
and `callback`. Model inheritance is per slot: an agent can override `answer`
and still inherit `planner`. `owner` identifies the user allowed to manage the
employee record; it does not automatically set the agent's own `owner`.

:::caution Employee defaults and reload order
In the inspected server implementation, startup builds agents before loading
employees, and SIGHUP rebuilds agents before reloading employee files. The admin
agent-reload endpoint does not itself reload employee files. Consequently,
employee defaults can be missing at startup or one reload behind an edit.

After startup, trigger an agent reload once employees have loaded. After editing
an employee file, send SIGHUP, wait for the employee reload to complete, then
trigger the admin agent-reload endpoint. Check logs and an execution result to
confirm the intended configuration. Releases that fix this ordering may no
longer need the extra step.
:::

## An agent file

Save this minimal linked agent as `data/agents/intake.md`:

```yaml
---
name: intake
description: Collect a client's request and identify missing information.
agent_type: persona
owner_employee: frontdesk
max_turns: 8
max_output_tokens: 2048
---

You handle client intake. Ask for missing details one question at a time.
Summarize the request for a human reviewer. Do not promise an external action.
```

Everything below the closing `---` is the agent's system prompt. The employee's
Markdown body is descriptive text; it is not prepended to the agent prompt.
Model IDs in the employee example are illustrative: replace them with IDs your
gateway serves, or omit `model_config` to inherit the server defaults.

## Call the agent

After loading both files, call **`intake`**, not `frontdesk`:

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/agents/v1/intake/chat" \
  -H "Authorization: Bearer $LIBRA_OS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"message":"I need help preparing an application."}'
```

Use a credential authorized for the agent. Hand-written files with no `owner`
are admin-only. For SDK and compatible request shapes, see
[Calling agents](/calling-agents).

To add another behavior, create another agent file with
`owner_employee: frontdesk`. That gives it shared defaults, not automatic
routing from `intake`. Add installed skills to the agent or let your application
choose the next agent explicitly.

## Agent field reference

The following fields describe the **file format**, not a promise that every
field is accepted by the managed API. New files need a unique `name` identifier;
other fields are optional unless their feature requires them.

### Identity and routing

| Field | Meaning |
| --- | --- |
| `name` | Identifier slug (kebab-case) for new agents; display name for legacy files whose slug is in `agent_id`/`id` |
| `description` | Shown in pickers and used by the planner when no hint is set |
| `delegation_hint` | Planner-facing "when to use this agent" — separate from `description` because the routing model and the UI need different text |
| `agent_type` / `type` | `skill` (single call) or `persona` (multi-turn) |
| `brain` | `true` lets the planner tier decompose work across skills |
| `category` | Classification class (`legal`, `bi`, …) for optional re-routing |
| `owner_employee` | Employee supplying shared model, search, and callback defaults; does not invoke or authorize the agent |
| `owner` | Owning user's email; empty = admin-only |

### Models

`model_config` has three slots — `answer`, `planner`, `skill` — each with a
`primary` and an optional `fallback` chain. Resolution cascades **per slot**:
per-agent → per-employee → server default. The selected slot supplies both its
primary and its fallback list; lists are not merged across levels. Supported
per-call overrides apply at the API layer; see [Calling agents](/calling-agents). The legacy
single `model:` field still works; `model_config` takes precedence when both
are present.

The YAML never declares "local" or "cloud" — it just names model ids, and the
deployment's gateway (`OPENAI_API_BASE`) determines which namespace those ids
live in. Against a **routing gateway**, ids carry a `provider/` prefix:

```yaml
model_config:
  answer:
    primary: anthropic/claude-opus-4-7
    fallback: [gemini/gemini-2.5-flash]
  planner:
    primary: anthropic/claude-opus-4-7
  skill:
    primary: gemini/gemini-2.5-flash-lite
```

Some plans additionally serve `-Ent` variants of these ids. They are not
present on every account, so list `GET /v1/models` against your own gateway
before pinning one, and see [Model settings](/model-settings) for what the
suffix does and does not guarantee.

Against a **local Ollama server** ([Local models](/model-settings#local-models)),
ids are the server's bare model names — no prefix, per the standing Ollama
exception:

```yaml
model_config:
  answer:
    primary: qwen3:32b
  planner:
    primary: qwen3:32b
  skill:
    primary: llama3.2:3b
```

Bare Ollama ids are accepted in **files**. The managed-agents API is stricter:
`POST`/`PUT /v1/agents` reject any id without a `provider/` prefix, so the same
`model_config` that loads from disk is refused through the API.

Pin only ids your gateway actually serves — anything else 404s at call time.
For an employee meant to run on **both** kinds of deployment, pin nothing:
with no `model_config` it inherits the deployment's default models through
the cascade above, so the identical YAML works on cloud and air-gapped
installs alike (this is why the SDK templates ship modelless).

### Skills and tools

| Field | Meaning |
| --- | --- |
| `skills` (alias `tools`) | Installed skill/tool references. Agent references can delegate behavior; tool-pack references load operations. Check the installed catalog for the ID's meaning |
| `direct_tools` | The escape hatch: attach a skill's tool definitions to the agent's **own** LLM call, so the agent's prompt governs how the tool is used (e.g. "print base64 inline") |
| `capabilities` | Routing labels the planner dispatches on. On a `brain: true` persona these build the skill map — see the note below |
| `custom_tools` | Partner-defined tools: `name`, `description`, `input_schema` (JSON Schema), optional per-tool `callback`, plus `side_effects`, `risk_tier` (low/medium/high), and dry-run support for the configured approval path |
| `callback` | Agent-level webhook for custom tools; cascade is tool → agent → employee |

:::caution Declare `capabilities` on a `brain: true` persona
On a persona with `brain: true`, an empty `capabilities` means an **empty skill
map**: the planner can dispatch nothing, and every question is answered from the
model's own memory instead. `skills:` alone is decorative on a persona. The
server logs this at ERROR per agent at boot (`persona_dispatch:<id>`). If you
set `brain: true`, declare `capabilities` with the routing labels the planner
should dispatch on.
:::

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

- Agent files load at boot. After editing an agent file, use the admin reload
  endpoint (`POST /api/admin/agents/reload`) or the server's SIGHUP handler.
  Saving a file alone does not guarantee that the active registry changed.
- API-managed agents normally write under `data/agents/_runtime/` (overridable
  with `LIBRA_OS_AGENTS_RUNTIME_DIR`). A runtime definition can override a
  packaged definition with the same ID. Check `source_path` in the operator
  registry when an edit seems ineffective.
- The SDK's create/update methods write supported fields through the management
  APIs. Read back the definition and inspect the registry after a change;
  YAML and API field coverage differ.
- Legacy field names (`agent_id`, `id`, single `model:`) keep working; the
  identifier is resolved as `agent_id` → `id` → `name`. Prefer the canonical
  names shown above for new files.


## Start from a template

Customer support is the most common first deployment — inquiry triage,
troubleshooting, and ticket summaries map directly onto a single persona
agent with `knowledge_base_lookup` grounded in your own product docs:

```bash
git clone https://github.com/libraos/sdk
mkdir -p ./data/agents
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

The playbook templates cover support, communications, marketing,
analytics, operations, and finance — see the
[catalog](https://github.com/libraos/sdk/tree/main/employees) for what each
one does and its recommended skills.
