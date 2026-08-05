---
slug: /getting-started
sidebar_position: 3
title: Getting started
description: Download, install, and run Libra OS on your own machine.
---

# Getting started

Libra OS is a single signed binary. It is free to start; the offline license
unlocks the team features.

## Install (connected machine)

```bash
curl -fsSL https://libraos.com/install.sh | sh
```

The installer detects your OS and architecture, downloads the matching binary,
**verifies it against `SHA256SUMS`**, and installs it as `libraos` on your PATH.

## Install (air-gapped)

On a machine with no outbound network, download the binary and checksums from the
[download page](https://libraos.com/download/) on a trusted machine, verify, then
copy them in:

```bash
sha256sum -c SHA256SUMS --ignore-missing
chmod +x libraos-linux-amd64
sudo mv libraos-linux-amd64 /usr/local/bin/libraos
```

## Verify the install

```bash
libraos --version
```

## Start the server

```bash
export LIBRA_OS_PUBLIC_URL=http://0.0.0.0:8900
export LIBRA_OS_ADMIN_EMAIL=...
export LIBRA_OS_ADMIN_PASSWORD=...
export LIBRA_OS_DATABASE_URL='postgres://...'
export OPENAI_API_BASE=https://api.meganova.ai
export OPENAI_API_KEY="sk-..." 
export LIBRA_OS_JWT_SECRET=...
libraos serve
```

## Next steps

- [Deploy Libra OS](/deployment) for your team — on-prem, VPC, or air-gapped.
- Review the [security model](/security) before connecting your knowledge base.
