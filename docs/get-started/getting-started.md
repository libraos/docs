---
slug: /getting-started
sidebar_position: 3
title: Getting started
description: From a blank machine to a first grounded answer in about ten minutes — install, start, mint a token, and talk to a built-in employee.
---

# Getting started

**From a blank machine to a first answer in about ten minutes.** Libra OS is
a single signed binary — free to start; the offline license unlocks the team
features. Four steps: install, start, mint a token, ask.

## 1. Install — about a minute

```bash
curl -fsSL https://libraos.com/install.sh | sh
```

The installer detects your OS and architecture, downloads the matching binary,
**verifies it against `SHA256SUMS`**, and installs it as `libraos` on your PATH.

On an air-gapped machine, download the binary and checksums from the
[download page](https://libraos.com/download/) on a trusted machine, verify,
then copy them in:

```bash
sha256sum -c SHA256SUMS --ignore-missing
chmod +x libraos-linux-amd64
sudo mv libraos-linux-amd64 /usr/local/bin/libraos
```

Check it:

```bash
libraos --version
```

## 2. Configure and start — about three minutes

```bash
export LIBRA_OS_PUBLIC_URL=http://0.0.0.0:8900
export LIBRA_OS_ADMIN_EMAIL=...
export LIBRA_OS_ADMIN_PASSWORD=...
export LIBRA_OS_DATABASE_URL='postgres://...'
export OPENAI_API_BASE=https://api.meganova.ai
export OPENAI_API_KEY="sk-..."
export LIBRA_OS_JWT_SECRET=$(openssl rand -base64 48)

# A credential for this quickstart (step 3 uses it):
export Q_SECRET=$(openssl rand -hex 24)
export LIBRA_OS_SERVICE_CLIENTS="quickstart:admin=$Q_SECRET"

libraos serve
```

`OPENAI_API_BASE` can be any OpenAI-compatible endpoint — the managed gateway
shown here (pay-as-you-go by default, [token plan](/model-settings) optional),
or a fully local server: see [Local models](/model-settings#local-models) for
the Ollama configuration.

`LIBRA_OS_JWT_SECRET` signs every session and API token the server issues.
Generate it once, store it with your other secrets, and reuse the same value
across restarts and replicas — a new secret invalidates every existing login
and token. With auth enabled, the server refuses to start if the secret is
unset, left at a known default, or shorter than 16 bytes.

To check the whole setup — environment, database, LLM gateway, and the
running server — use the built-in audit:

```bash
libraos doctor deployment
```

## 3. Mint a token — about a minute

The `quickstart` client you registered in the environment can exchange its
secret for a bearer token:

```bash
TOKEN=$(curl -s -X POST http://localhost:8900/oauth/token \
  -H 'content-type: application/json' \
  -d "{\"grant_type\":\"client_credentials\",\"client_id\":\"quickstart\",\"client_secret\":\"$Q_SECRET\"}" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
```

You should have a JWT in `$TOKEN` (`echo $TOKEN` → `eyJhbGciOi...`).

:::note
`quickstart:admin` is a full-admin credential — fine for a laptop, not for a
deployment. In production, register least-privilege service clients and let
people sign in as themselves; see [Deployment](/deployment) and
[Security](/security).
:::

## 4. Ask a built-in employee — about a minute

The kernel ships with preset employees. `business-assistant` is a general
analyst — ask it something:

```bash
curl -s -X POST http://localhost:8900/agents/v1/business-assistant/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"message":"In one sentence, what can you help with?"}'
```

You should see a response like:

```json
{
  "response": "I can help with business questions — summaries, comparisons, and reports across financials, operations, and strategy.",
  "conversation_id": "chat_1786552728460381358",
  "agent_id": "business-assistant",
  "model": "gemini/gemini-2.5-flash",
  "retrieved_chunks": [],
  "grounding": "ungrounded",
  "usage": { "...": "..." }
}
```

Two fields to notice:

- **`retrieved_chunks`** is empty and **`grounding`** says so — you haven't
  given it any knowledge yet. Once you ingest documents and bind them to an
  employee, this same call answers *from your sources* and lists the exact
  files each answer drew on. That list is the difference between an AI that
  sounds right and one you can check.
- **`conversation_id`** — pass it back on the next call to continue the
  conversation.

That's the whole loop: a governed employee, behind your own endpoint,
answering with its evidence attached.

## What's next

- **[Create your first agent](/creating-an-agent)** — the same thing from the
  Python SDK: employee, agent, message, in three calls.
- **[Define employees in YAML](/employee-yaml)** — the filesystem-canonical
  format the presets use; add knowledge bindings to make answers grounded.
- **[Model settings](/model-settings)** — routing tiers, pay-as-you-go vs
  token plan, covered models, local models, web search.
- **[Deploy Libra OS](/deployment)** for your team — on-prem, VPC, or
  air-gapped, plus the secrets checklist.
- **[Security](/security)** — the model to review before connecting your
  knowledge base.
