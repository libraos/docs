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

> Running in Docker or Kubernetes instead? Skip to
> [Run it as a container](#run-it-as-a-container) — the configuration is the
> same, but the container needs one flag the binary does not.

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

## Run it as a container

The steps above install a binary. The published image runs the same server —
`ghcr.io/libraos/libraos`, entrypoint `libraos serve`, listening on **8900**.

Pin a tag from [releases](https://github.com/libraos/libraos/releases). `:latest`
moves only on production cutovers (`vX.Y.Z`); weekly tags
(`vX.Y.Z-week-YYYY-MM-DD`) never move it, and weeklies are built for
`linux/amd64` only — production tags carry `linux/arm64` as well, which matters
if your nodes are arm.

:::warning `--ulimit memlock=-1` is required, not optional
Without it the server **refuses to start** and exits 1:

```
memlock: RLIMIT_MEMLOCK soft cap is 65536 bytes, below the 8388608-byte minimum
```

Docker's default memlock cap is 64 KiB. Under memcg accounting the kernel
charges every `epoll_ctl(EPOLLET)` item against that cap, and Go's netpoll uses
`EPOLLET` for every file descriptor — so a non-trivial request load exhausts it
and the process dies inside the runtime rather than returning an error. The
guard refuses to boot instead of letting that happen.
:::

### Docker

```bash
docker network create libraos-net

docker run -d --name libraos-pg --network libraos-net \
  -e POSTGRES_USER=libraos -e POSTGRES_PASSWORD='<strong-password>' \
  -e POSTGRES_DB=libraos \
  -v libraos-pgdata:/var/lib/postgresql/data \
  postgres:16-alpine

docker run -d --name libraos --network libraos-net -p 8900:8900 \
  --ulimit memlock=-1 \
  -e LIBRA_OS_PUBLIC_URL=http://localhost:8900 \
  -e LIBRA_OS_ADMIN_EMAIL='you@example.com' \
  -e LIBRA_OS_ADMIN_PASSWORD='<12+ chars>' \
  -e LIBRA_OS_JWT_SECRET='<openssl rand -base64 48>' \
  -e LIBRA_OS_DATABASE_URL='postgres://libraos:<strong-password>@libraos-pg:5432/libraos?sslmode=disable' \
  -e OPENAI_API_BASE=https://api.meganova.ai \
  -e OPENAI_API_KEY='<your key>' \
  -e OPENAI_MODEL='<a model your gateway serves>' \
  -v libraos-runtime:/app/data/agents/_runtime \
  ghcr.io/libraos/libraos:<tag>

curl -fsS http://localhost:8900/health
```

From here, steps 3 and 4 above are unchanged — mint a token, create an agent.

### Two volumes that are not optional

**`/app/data/agents/_runtime`.** Agents created through `POST /v1/agents` are
written here as Markdown files. Without a volume they exist only in the
container's writable layer, so every agent you create through the API
disappears on the next `docker run`. The image ships its bundled agents at
`/app/data/agents/`; only the `_runtime` subdirectory needs to persist.

**Postgres data.** Conversations, settings, audit and memory live in the
database, not in the container.

`LIBRA_OS_JWT_SECRET` must also be the same value across restarts — regenerate
it and every outstanding token stops working.

### Kubernetes

The same three requirements apply: the memlock limit, a persistent volume for
runtime agents, and a stable JWT secret from a Secret rather than the manifest.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: libraos
spec:
  serviceName: libraos
  replicas: 1
  selector:
    matchLabels: { app: libraos }
  template:
    metadata:
      labels: { app: libraos }
    spec:
      securityContext:
        # The memlock guard above. Without IPC_LOCK the pod CrashLoopBackOffs
        # on the same RLIMIT_MEMLOCK error as Docker.
        capabilities:
          add: ["IPC_LOCK"]
      containers:
        - name: libraos
          image: ghcr.io/libraos/libraos:<tag>
          ports:
            - containerPort: 8900
          envFrom:
            - secretRef: { name: libraos-secrets }
          env:
            - name: LIBRA_OS_PUBLIC_URL
              value: https://libraos.example.com
            - name: OPENAI_API_BASE
              value: https://api.meganova.ai
          volumeMounts:
            - name: runtime-agents
              mountPath: /app/data/agents/_runtime
          readinessProbe:
            httpGet: { path: /health, port: 8900 }
            initialDelaySeconds: 5
          livenessProbe:
            httpGet: { path: /health, port: 8900 }
            initialDelaySeconds: 30
  volumeClaimTemplates:
    - metadata:
        name: runtime-agents
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests: { storage: 1Gi }
```

`LIBRA_OS_JWT_SECRET`, `LIBRA_OS_ADMIN_PASSWORD`, `LIBRA_OS_DATABASE_URL` and
`OPENAI_API_KEY` belong in the `libraos-secrets` Secret, not in the manifest.

**A StatefulSet with one replica, deliberately.** Runtime agents are files on a
`ReadWriteOnce` volume, so a second replica would neither see agents created by
the first nor be able to mount the same claim on most storage classes. Scale
horizontally only after moving agent definitions into the database or onto
shared storage — and note that `LIBRA_OS_INSTANCE_ID` (defaulting to
`<hostname>-<pid>`) is what marks orphaned async jobs at startup, so several
replicas sharing one database need distinct values.

**Bring your own Postgres.** Use a managed instance or an operator; the
single-container Postgres above is for a laptop, not a cluster.

### What this basic setup does not include

Vector retrieval needs SurrealDB. Without it the deployment falls back to a
lexical-only store, which still answers but cannot match on meaning — and it
says so at boot and in `GET /api/capabilities`. See
[Deploy Libra OS](/deployment) for the knowledge-store options, and run
`libraos doctor deployment` inside the container to check what is actually
active:

```bash
docker exec libraos libraos doctor deployment
```

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
