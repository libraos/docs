---
slug: /getting-started
sidebar_position: 1
title: Getting started
description: Install the runtime, configure dependencies, authenticate, create an agent, and send a first request.
---

# Getting started

Install the runtime, configure a database and model endpoint, obtain a token,
and create an agent to call. You need PostgreSQL, access to a supported model
endpoint (hosted or local), and Python 3 for the token-extraction command.
The binary does not include model weights or a database.

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
export LIBRA_OS_PUBLIC_URL=http://localhost:8900
export LIBRA_OS_ADMIN_EMAIL=...
export LIBRA_OS_ADMIN_PASSWORD=...
export LIBRA_OS_DATABASE_URL='postgres://...'
export OPENAI_API_BASE=https://api.meganova.ai
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL='provider/model-served-by-your-gateway'
export LIBRA_OS_JWT_SECRET=$(openssl rand -base64 48)

# A credential for this quickstart (step 3 uses it):
export Q_SECRET=$(openssl rand -hex 24)
export LIBRA_OS_SERVICE_CLIENTS="quickstart:admin=$Q_SECRET"

libraos serve
```

Replace the sample credentials, database URL, and model ID before starting.
Run the server in this terminal and issue requests from a second terminal;
make the required request variables available there as well.

`OPENAI_API_BASE` can be a supported OpenAI-compatible endpoint — the managed gateway
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
TOKEN=$(curl --fail-with-body -sS -X POST http://localhost:8900/oauth/token \
  -H 'content-type: application/json' \
  -d "{\"grant_type\":\"client_credentials\",\"client_id\":\"quickstart\",\"client_secret\":\"$Q_SECRET\"}" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
```

Export the token and URL in the terminal where you will run the examples:

```bash
export LIBRA_OS_URL=http://localhost:8900
export LIBRA_OS_API_KEY="$TOKEN"
```

If token exchange fails, check the response and service-client configuration.

:::note
`quickstart:admin` is a full-admin credential — fine for a laptop, not for a
deployment. In production, register least-privilege service clients and let
people sign in as themselves; see [Deployment](/deployment) and
[Security](/security).
:::

## 4. Create and call your own agent

Create a standalone persona so the example does not depend on bundled agents:

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/v1/agents" \
  -H "Authorization: Bearer $LIBRA_OS_API_KEY" \
  -H 'anthropic-beta: managed-agents-2026-04-01' \
  -H 'Content-Type: application/json' \
  -d '{"name":"quickstart-assistant","agent_type":"persona","system":"Answer concisely and explain what information you need."}'
```

Save the returned `id`. For this name the ID is `quickstart-assistant`.
If it already exists, reuse it or choose another name. Call it:

```bash
curl --fail-with-body -sS "$LIBRA_OS_URL/agents/v1/quickstart-assistant/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"message":"In one sentence, what can you help with?"}'
```

A native-chat response has this shape (answer text, model, and grounding values
vary with your configuration):

```json
{
  "response": "I can help with business questions — summaries, comparisons, and reports across financials, operations, and strategy.",
  "conversation_id": "chat_1786552728460381358",
  "agent_id": "quickstart-assistant",
  "model": "gemini/gemini-2.5-flash",
  "retrieved_chunks": [],
  "grounding": "ungrounded",
  "usage": { "...": "..." }
}
```

Two fields to notice:

- **`retrieved_chunks`** is empty and **`grounding`** says so — you haven't
  given it any knowledge yet. Once you ingest documents and bind them to an
  agent ([Workspaces & memory](/workspaces-memory)), this same call
  answers *from your sources* and lists the exact files each answer drew on. That list is the difference between an AI that
  sounds right and one you can check.
- **`conversation_id`** — pass it back on the next call to continue the
  conversation.

You have created an executable agent and called it through the native API.
An employee record is optional shared configuration; it is not required to make
this request. See [the object model](/agents) and [API formats](/calling-agents).

## What's next

- **[Create your first agent](/creating-an-agent)** — the same thing from the
  Python SDK, with response parsing and conversation history.
- **[Define employees in YAML](/employee-yaml)** — the filesystem-canonical
  format for shared employee defaults, prompts, tools, and knowledge bindings.
- **[Model settings](/model-settings)** — routing tiers, pay-as-you-go vs
  token plan, covered models, local models, web search.
- **[Deploy Libra OS](/deployment)** for your team — on-prem, VPC, or
  air-gapped, plus the secrets checklist.
- **[Security](/security)** — the model to review before connecting your
  knowledge base.
