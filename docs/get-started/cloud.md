---
slug: /cloud
sidebar_position: 1
title: Libra OS Cloud
description: The hosted, sign-up-and-go edition — start free in minutes with no install, connect your website, and write blogs and docs.
---

# Libra OS Cloud

Libra OS Cloud is the **hosted edition**: we run the infrastructure, so you go
from sign-up to a working workspace in minutes — no binary, no database, no
Kubernetes. It is the same Libra OS engine and the same eight supervised digital
employees you would run yourself; the only difference is who operates the
servers.

Prefer to run it on your own hardware — on-prem, VPC, or fully air-gapped? That
is [Libra OS Self-Hosted](/getting-started), and it is the same product. See
[Cloud vs Self-Hosted](/editions) to choose.

## 1. Sign up

Create a free workspace at **[app.libraos.com/signup](https://app.libraos.com/signup)**.
No credit card — the free tier is enough to evaluate. Your workspace is
provisioned on sign-up, at `your-workspace.libraos.com`.

## 2. Meet your employees

Your workspace arrives with eight supervised digital employees ready to work —
support, document analysis, content, and more. Everything the
[self-hosted quickstart](/getting-started) does after install, you have on
sign-up instead.

## 3. Connect your website

Point Libra OS at your site. It crawls your pages into a private knowledge base,
and from then on your assistant answers **from your own content, with a citation
to the page each fact came from** — the same knowledge-grounding described in
[Building a customer support agent](/guides/customer-support), with the crawl and
collection set up for you.

```
Settings → Knowledge → Connect a website → https://your-company.com
```

## 4. Talk to it — chat or API

- **In the workspace:** chat with any employee, assign work, review what ships.
- **From your code:** Libra OS Cloud exposes the same OpenAI-compatible endpoints
  and the same [`libraos` SDK](/creating-an-agent) as self-hosted — just point
  them at your workspace URL with a workspace API key:

```python
from libraos import Client

c = Client(base_url="https://your-workspace.libraos.com", api_key="msk_live_...")
resp = c.messages.create(
    agent_id="customer-support",
    messages=[{"role": "user", "content": "Does the Pro plan support SSO?"}],
)
```

Everything in [Building agents](/creating-an-agent) and the
[Guides](/guides/customer-support) works identically on Cloud — the API surface
is the same, only the base URL and key differ.

## 5. Write blogs and docs

Ask a content employee to draft a blog post, a help article, or a report. Because
it is grounded in your connected website and knowledge base, drafts are
source-cited and on-brand — ready for you to review and publish rather than
starting from a blank page.

## Growing up: Cloud plans and beyond

The free tier is for evaluation. Cloud plans start at **$249/month** as you grow
— see [pricing](https://libraos.com/pricing/). Every plan includes the complete
platform; the firewall and governance layer are never gated behind a higher tier.

## Moving to self-hosted later

Compliance, data-residency, or scale requirements can arrive after you have
already built something. Because Cloud and Self-Hosted are the **same Libra OS**,
you export your employees, knowledge, and configuration and import them into a
self-hosted deployment — no rebuild, no migration of agents. See
[Cloud vs Self-Hosted](/editions).

:::note Availability
Libra OS Cloud is rolling out. If sign-up isn't yet open in your region, the same
capabilities are available today on [Self-Hosted](/getting-started), and your
work carries over when Cloud opens.
:::

## Next steps

- **[Cloud vs Self-Hosted](/editions)** — which edition fits, and how to move between them
- **[Create your first agent](/creating-an-agent)** — the SDK works the same on Cloud
- **[Customer support agent](/guides/customer-support)** — a full grounded-assistant build
