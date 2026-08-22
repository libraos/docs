---
slug: /knowledge-retrieval
sidebar_position: 6
title: Knowledge base & retrieval
description: Which backend actually holds vectors, how to confirm retrieval is working, and how to scope auto-indexing.
---

# Knowledge base & retrieval

Two settings decide whether your knowledge base answers questions semantically
or only by keyword, and neither of them is named in a way that makes the answer
obvious. This page is the short version of both.

:::warning Upgrading to v0.1.18: auto-indexing is now opt-in

`LIBRA_OS_SUPERNOVA_ENABLED` defaults to **`false`** as of v0.1.18. If you rely
on uploaded documents being indexed automatically, set it:

```bash
LIBRA_OS_SUPERNOVA_ENABLED=true
```

Without it, documents are stored but never parsed, chunked, embedded or
retrievable. Nothing errors at request time — retrieval simply returns nothing.
Boot logs it at `level=ERROR` and `GET /api/capabilities` reports it.

The default changed because auto-indexing reads **every object** under your
documents root. That should be a decision you make, not one you discover.

:::

## Only one backend holds vectors

`LIBRA_OS_VECTOR_BACKEND` chooses where knowledge chunks live. Configuring an
embedding model does **not** by itself mean retrieval uses embeddings — that
depends entirely on which store you land on.

| value | vector search | survives restart |
|---|---|---|
| `surreal` | **yes** — hybrid keyword + semantic | yes |
| `pgvector` | **no** — keyword only, despite the name | yes |
| `qdrant` | **no** — keyword only, despite the name | yes |
| `memory` | yes | **no** — wiped on every restart |
| `auto` *(default)* | only if SurrealDB connects | depends |

**If you want semantic retrieval, deploy SurrealDB.** There is no other option
today.

`pgvector` is the one to watch: it reads like the vector-capable choice, and it
is the one you would reach for if what you wanted was durability. A deployment
can end up with a correctly configured embedding endpoint, a clean startup, and
keyword-only search.

## Confirm retrieval is actually working

Ask the deployment rather than inferring it from configuration:

```bash
curl -s $LIBRA_OS_URL/api/capabilities | jq .retrieval
```

```json
{
  "vector_search": true,
  "backend": "surreal",
  "durable": true,
  "embedder_configured": true,
  "embedding_model": "Qwen/Qwen3-Embedding-8B",
  "verdict": "vector retrieval ACTIVE (hybrid lexical + cosine)"
}
```

Read `verdict` first — it states the consequence, not the setting. The same
response carries a per-collection breakdown, including whether each
collection's documents were actually embedded:

```json
{ "id": "matters", "chunks": 437, "documents": 136, "embedded": "yes", "retrievable": true }
```

`embedded` can be `no` or `partial` on a vector-capable backend — a collection
ingested before embeddings were configured, or while the embedding endpoint was
failing, holds chunks that only keyword matching can reach. Re-ingest those.

Two more places answer the same question:

```bash
libraos doctor deployment      # includes a "vector retrieval" check
libraos config --effective     # embedding.endpoint, embedding.model, vector.backend
```

## Scope auto-indexing before you enable it

Unconfigured, auto-indexing puts **every** object into one shared `default`
collection. If your application separates content per customer, per matter or
per case, that collapses those separations into a single index.

| Variable | Effect |
|---|---|
| `LIBRA_OS_SUPERNOVA_COLLECTION_TEMPLATE` | Route by path: `matter-{path[1]}` sends `cases/<id>/uploads/x.pdf` to collection `matter-<id>`. |
| `LIBRA_OS_SUPERNOVA_IGNORE_PREFIXES` | Never index these prefixes, e.g. `kyc/,identity/`. |
| `LIBRA_OS_SUPERNOVA_ALLOW_PREFIXES` | When set, index **only** these prefixes. |

Two properties worth relying on:

- **Exclusions apply before the file is opened.** An ignored prefix is never
  read, parsed or embedded — not filtered out afterwards. If you have content
  you are contractually forbidden to send through AI retrieval, this is the
  control to use. A file-extension check is not one.
- **Ignore beats allow**, and a path that cannot satisfy the collection template
  is skipped rather than falling back to `default`.

To turn auto-indexing off durably, use the environment variable above.
`POST /api/super-nova/emergency/pause` works but is held in memory only, so a
restart, upgrade or reboot resumes indexing.

## Running SurrealDB

The `surrealdb/surrealdb:v3` image runs as a non-root user (uid 65532) and v3.2.4
removed the `file://` scheme. A fresh named volume is root-owned, so the
container cannot initialise its database and restart-loops. Use a bind mount
owned by the container user, a `rocksdb:` path, and a generated password:

```bash
mkdir -p /opt/libraos/surreal-data && chown 65532:65532 /opt/libraos/surreal-data
docker run -d --name surrealdb -p 127.0.0.1:8010:8000 \
  -v /opt/libraos/surreal-data:/data surrealdb/surrealdb:v3 \
  start --user root --pass "$STRONG_PASSWORD" rocksdb:/data/database.db
```

Bind to `127.0.0.1` and never accept a default password. Then point LibraOS at
it with `LIBRA_OS_SURREAL_URL=ws://127.0.0.1:8010/rpc` plus
`LIBRA_OS_SURREAL_USER` and `LIBRA_OS_SURREAL_PASS`.

## Changing the vector backend does not move your data

`LIBRA_OS_VECTOR_BACKEND` selects where chunks live; changing it does not
migrate what is already stored. Collection metadata survives, so listings and
search still respond — from whatever fraction made it across.

Plan a backend change as a re-ingest. To move one collection without a running
server:

```bash
libraos knowledge export <collection-id> -o collection.zip   # from the old backend
# change LIBRA_OS_VECTOR_BACKEND, restart
libraos knowledge import collection.zip                      # re-embeds into the new store
```

Startup warns, per collection, when the active store holds materially fewer
chunks than your database does.

## Verify the binary you deployed

Every release carries a checksum manifest:

```bash
gh release download v0.1.18 --pattern 'libraos-v0.1.18-*'
sha256sum -c --ignore-missing libraos-v0.1.18-SHA256SUMS
```

The [public mirror](https://github.com/libraos/releases) publishes its own
`SHA256SUMS` over the stable filenames.
