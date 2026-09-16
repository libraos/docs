# Developer documentation review — 2026-09-16

Reviewed all 24 existing documentation pages, both blog posts, navigation,
build configuration, and contributor instructions. Added one shared API guide.
This review checks explanations and examples against source; it is not a
certification of every product feature or a live production integration test.

## Evidence baseline

- Docs base: `54ceacf`.
- Server inspected: `41c48d1fcbbe90cdbe4bf00b0e0c7f5864896271`.
- Python SDK inspected and used for mocked requests:
  `a616ce12e1c35c4a7fcbed9eaeedf477a38f14ec`.
- SDK verification used a clean exported snapshot, not the adjacent worktree's
  uncommitted changes.
- Live Cloud page was checked directly and described private-beta access.
  Search-engine output still showed older signup/preset copy; it was not used
  as the current availability contract.

## Most consequential corrections

| Problem | Evidence | Documentation change |
| --- | --- | --- |
| Employee and agent treated as synonyms | Server `internal/corporate/employee_def.go`, `loader.go`, `cascade.go` | Employee owns/configures; agent executes; human Desk member is a third meaning. |
| Quickstart sends unsupported creation fields | SDK `resources/agents.py`; server `routers/managed_agents.go` create/update request structs | Use `system`, returned agent ID, and a standalone persona. Explain YAML-only employee binding and configuration fields. |
| Messages examples select the wrong behavior | SDK `resources/messages.py`; server `routers/messages_api.go` | Set `metadata.agent_id` in HTTP examples; distinguish `model` and response formats. |
| SDK examples use unsupported `headers` and treat content blocks as strings | SDK `resources/messages.py`, `models.py`, `client.py` | Supported method arguments, authenticated user token, `response.text`, and explicit history. |
| Low-confidence classifier assigns before escalating | Old ticket-routing example | Escalate and return before assignment. Label application adapters and failure handling. |
| Memory described as automatic and keyed by arbitrary headers | Server `routers/openai_compat_memory.go`, `chat.go`, observational `types.go` | Separate threads, observations, fields, and profiles; explain authenticated identity and privileged overrides. |
| File save/reload described as automatically applying employee defaults | Server `cmd/libraos/main.go` boot and SIGHUP ordering | Explicit reload instructions and current ordering caveat. |
| Preset employees, Cloud signup, offline behavior, and provider prices presented as unconditional | Public site and deployment/runtime configuration | Create agents in examples; private-beta Cloud; distinguish storage and processing; remove fixed pricing/model entitlement promises. |
| Registry source filter described as tenant ownership | Server `routers/agents.go` | Explain file-location classification and separate authorization. |

## Page coverage

| Page | Review result |
| --- | --- |
| Introduction | Developer path, object definitions, dependencies, and data flow. |
| Getting started | Create an agent explicitly; correct authentication handoff and unsigned/checksum wording. |
| Cloud | Private-beta access and supplied connection details; remove non-awaited SDK example. |
| Editions | Operations, processing location, and explicit migration work. |
| Deployment | Required services and release-dependent agent sets. |
| Model settings | Model IDs versus agent IDs, per-slot inheritance, local dependencies, search host check. |
| Agents overview | Employee/agent/tool/planner boundaries and invocation flow. |
| Create an agent | Executable SDK example with supported fields and content parsing. |
| Employee YAML | Linked files, call path, field inheritance, API parity, reload limitations. |
| Workspaces & memory | Filesystem workspace versus collection, retrieval permissions, opt-in memory. |
| Managing memory | Authenticated identity, context, persistence, retention/deletion boundaries. |
| Web search | Gateway conditions, correct agent selection, evidence limits. |
| Durable runs | Agent route identity and release-dependent behavior; preserve detailed reconnect/outcome guidance. |
| Customer support | SDK arguments, content blocks, identity, explicit escalation, template loading. |
| Ticket routing | JSON parsing, bounded confidence, review before assignment, application adapters. |
| Desk overview | Application boundary and human/agent terminology. |
| Desk settings | Organization-owned connections and human members. |
| Desk connections | Human account linking versus employee records. |
| Desk audit | Action ledger versus chat/job completion. |
| Capabilities | Requirements mapped to actionable guides. |
| Security | Concrete storage/processing/access/approval boundaries. |
| Portability | Dependencies, migration limits, authenticated capability check. |
| Listing agents | Header requirements, source semantics, model-summary limits. |
| Benchmarks | Previously reported figures clearly distinguished from reproducible evidence or deployment guarantees. |
| Calling agents (new) | Endpoint selectors, response shapes, context, and errors in one place. |
| Product explainer blog | Availability update and corrected preset/privacy statements. |
| Welcome blog | Reviewed; retained historical announcement and working links. |

## Remaining implementation gaps

1. **Managed-agent/YAML parity:** the managed create/update structs omit
   `owner_employee`, `model_config`, and `callback`; the SDK accepts arbitrary
   keyword fields but that does not make the server persist them. The old
   tutorial could return success without installing its prompt or employee link.
   A future server change should round-trip supported fields or reject them
   explicitly. This docs change uses the supported path.
2. **Employee reload ordering:** startup builds agents before employees load.
   SIGHUP rebuilds agents before reloading employees; the admin agent-reload
   closure does not reload employees. Inherited settings may be missing or
   stale until a subsequent agent rebuild. The YAML guide documents the
   workaround; the server ordering still needs a code fix.
3. **Identity and deletion:** stores do not all use one universal tenant or
   employee key. Shared-credential integrations need verified canonical/end-user
   mapping; a documentation edit cannot introduce an atomic cross-store deletion
   contract. Avoid promising one until implemented and tested.

## Validation

- Production Docusaurus build with broken links, Markdown links, and anchors
  configured as errors; includes generated LLM feeds.
- `tools/check_examples.py`: Python, YAML, shell, and JSON syntax; explicit
  Messages routing in curl payloads; exact SDK quickstart, support, and
  ticket-routing snippets with a mocked HTTP transport.
- Mock checks cover the prompt field, beta header, agent selector, content-block
  parsing, authenticated support request, and escalation before assignment.
- No live inference requests or production data mutations are required for
  those checks. Live provider behavior and release-specific integration still
  need deployment testing.

Pull requests now run the static build; deployment remains restricted to main.
The contributor guide records the terminology and example conventions.
