---
slug: /durable-runs
sidebar_position: 6
title: Run background tasks
description: Submit a task once, reconnect to its progress, and inspect its persisted outcome.
---

# Run background tasks

Build long-running work into your own application using the native jobs API.
Your application owns its UI and business logic; Libra OS executes the agent
under the submitting identity and stores the job's progress and outcome.

:::caution Release availability
The durable-runs server update is not yet released. Before relying on
restart-safe event numbering or atomic completion receipts, confirm your server
release includes those changes. Updating this documentation does not upgrade
your running server.
:::

## Prerequisites

- A running Libra OS deployment with PostgreSQL persistence and authentication.
- An installed agent that supports background streaming execution.
- A bearer token authorized to use that agent. Keep it on your application's
  backend; never embed an administrator token in browser or mobile source code.
- For the downloadable example, Python 3.10 or newer; no extra packages.

This guide uses `/agents/v1/{agent}/jobs`, the native server API. Its successful
terminal status is **`done`**, not `completed`. Do not mix its response shape with
the separately documented managed-jobs SDK contract.

## Submit once

Set `LIBRA_OS_URL` to your deployment and `LIBRA_OS_TOKEN` to your bearer token.
Use your installed agent's route ID in place of `my-agent`:

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/agents/v1/my-agent/jobs" \
  -H "Authorization: Bearer $LIBRA_OS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize the approved documents and identify missing information."}'
```

The server returns HTTP 202 with a `job_id`, `agent_id`, `status: queued`, and
`created_at`. Save the job ID in your application before starting observation.
Closing the HTTP connection does not cancel the job.

**Do not automatically retry submission.** A timed-out POST may have been
accepted. Native job submission does not currently promise idempotency through
an `Idempotency-Key` header; submitting again can create another run and repeat
external actions. If no job ID came back, ask the operator to locate the
original request before creating replacement work.

## Observe and reconnect

Set `JOB_ID` to the ID from the response:

```bash
curl --fail-with-body -N "$LIBRA_OS_URL/agents/v1/my-agent/jobs/$JOB_ID/stream" \
  -H "Authorization: Bearer $LIBRA_OS_TOKEN" \
  -H 'Last-Event-ID: 0'
```

Each event has an integer SSE `id`. Save the last ID **after successfully
processing the event**. If the connection drops, reconnect to this same URL
with that ID in `Last-Event-ID`. The server replays later persisted events and
then follows new progress. A reconnect does not submit or retry execution.

For example, after processing event 42, send `Last-Event-ID: 42`. Invalid or
negative cursors return HTTP 400. A replay-store outage must not be interpreted
as an empty successful stream: reconnect later using your existing cursor.

Your application should tolerate repeated delivery, keyed by `(job_id, event_id)`.
Replaying an event must not send an email, charge a customer, or otherwise repeat
the action described by the event.

## Inspect the outcome

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/agents/v1/my-agent/jobs/$JOB_ID" \
  -H "Authorization: Bearer $LIBRA_OS_TOKEN"
```

| Status | What your application should show |
| --- | --- |
| `queued` | Waiting to start. |
| `running` | Working; display progress or reconnect to the stream. |
| `done` | The invocation finished; display its persisted `result`. |
| `failed` | Display `error`; inspect before deciding whether new work is safe. |
| `cancelled` | Execution stopped; already-performed external actions are not undone. |

The final `done` **event** closes the stream for both successful and failed
invocations. Inspect `metadata.status` on that receipt or poll the job's
`status`; the event name alone is not a success verdict. `authz_outcome:
authz_failed` identifies a failed execution-time permission check.

A finished invocation is also **not an approval receipt**. If a tool queued an
action for human approval, the application must inspect that action separately
and wait for its authorized decision and execution result. Do not translate a
job's `done` into “email sent” or “payment completed.”

## Try the runnable example

[Download the SDK example](https://raw.githubusercontent.com/libraos/sdk/1a9bb6bf94cc951dbd2f6275e72abe60726dc5b8/python/examples/19_durable_run.py), save it as `durable_run.py`, then:

```bash
python3 durable_run.py --agent my-agent --prompt "Summarize the approved documents."
```

The script prints its job ID immediately, displays progress, reconnects to the
same job after transient observation failures, and prints the persisted final
record. Exit code 0 means `done`, 1 means `failed` or `cancelled`, and 2 means
observation or submission could not be confirmed.

To return to existing work without submitting again:

```bash
python3 durable_run.py --agent my-agent --job-id "$JOB_ID" --after 42
```

The CLI cursor is not a durable application database. Production consumers
should persist the job ID and processed event ID themselves. Stopping this
script only stops observation, not the server-side job.

## Restart, permissions, and retention

- Automatic restart recovery is currently limited to the read-only
  `research_sweep` workflow, when workflows are enabled. It keeps the same job
  ID and resumes supported checkpointed stages. This is not a guarantee for
  arbitrary agents or external actions.
- Operators must configure a **stable, unique** `LIBRA_OS_INSTANCE_ID` for each
  worker across restarts. Do not run two workers concurrently with the same ID.
  Default process-generated IDs do not establish a stable recovery identity.
- Other interrupted jobs are marked failed when their owner performs restart
  recovery. Inspect any external effects before submitting replacement work.
- The worker carries the submitting identity and rechecks it before execution.
  Another user's or another API key's job is not made readable by knowing its ID.
  Use the same authorized identity and agent route when reconnecting.
- Jobs and events are retained according to the deployment's cleanup policy
  (`LIBRA_OS_JOBS_RETENTION_HOURS`, default 24 hours for terminal jobs). A missing
  or inaccessible job returns 404; it is not a reason to resubmit automatically.
- Jobs persist request and result content. Storage location does not determine
  model-processing location: hosted models and configured tools can receive
  task data. Review [model settings](/model-settings) and [security](/security).

For setup, see [Create your first agent](/creating-an-agent). For the different
forms of context that survive between requests, see [Managing memory](/managing-memory).
