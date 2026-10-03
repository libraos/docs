---
slug: clef-vs-llm-email-triage
title: "Can a decision model triage email better than an LLM? Clef vs Claude Haiku on a DGX Spark"
authors: [libraos]
tags: [benchmarks]
description: "Cloudflare's Clef decision models vs the LLM classifier on real and multilingual email triage, run locally on a DGX Spark: who finds the mail that needs a person, and what one threshold changed."
---

Every email that reaches a Libra OS desk gets triaged: who sent it, what it is,
what the reader has to do, which part of the business it belongs to, and
whether it looks risky. Today that runs on an LLM. We tested Cloudflare's new
**Clef** decision models against it: **Clef 27B** and the smaller
**clef-flash**, running locally on a single NVIDIA DGX Spark (GB10). The
short version: **Clef 27B found more of the mail that needs a person, while
the LLM kept more noise out of the inbox.** For now the LLM stays in charge.

<!-- truncate -->

## What we measured

Libra OS sorts each inbound email into one of four streams: **Needs me**,
**Conversations**, **Feed** and **Paper trail**. Two numbers matter most to
the person reading the inbox:

- **Needs-me recall:** of the emails that really need the reader (a reply, an
  approval, a "was this you?" check), how many land in Needs me.
- **Inbox precision:** of the emails shown in the inbox (Needs me plus
  Conversations), how many belong there rather than in the feed or the paper trail.

Every model answered the same typed questions about each email:
- **what it is:** a request, a security notice, a social notification, …;
- **what to do:** reply, approve, verify, read later, nothing;
- **business area;**
- **risk:** phishing, or a one-time code.

"Who sent it" (a person, an automated system or a mailing list) comes from
the email's headers for every model, exactly as the product does.

## Results on a real mailbox

124 inbound emails from a test mailbox on one of our demo deployments, mostly
social-network notifications, account-security notices and sign-in codes:

| Model | Needs-me recall | Inbox precision | Business area |
|---|---|---|---|
| **Clef 27B** (local, GB10) | **0.91** | 0.71 | **0.98** |
| **clef-flash** (local, GB10) | 0.73 | 0.67 | 0.81 |
| Claude Haiku 4.5 (current LLM classifier) | 0.82 | **0.83** | 0.94 |

Clef 27B caught the most emails that needed attention, and it was also the
most accurate on "what to do" (0.96) and on business area. Haiku put fewer
emails in the inbox that didn't belong there. clef-flash trailed on every
measure.

## Results on a multilingual test set

16 hand-written business emails in English, Chinese, Spanish and French: a
client asking about a work permit, a quote request, a vendor invoice, contract
redlines, a payroll approval, a phishing attempt, newsletters and security alerts.

| Model | Needs-me recall | Inbox precision | Business area (EN / ZH / ES / FR) |
|---|---|---|---|
| **Clef 27B** | **1.0** | 1.0 | 0.9 / 0.5 / 1.0 / 1.0 |
| clef-flash | 0.92 | 1.0 | 0.8 / 0.75 / 1.0 / 1.0 |
| Claude Haiku 4.5 | 0.92 | 1.0 | **1.0 / 1.0 / 1.0 / 1.0** |

Clef 27B found every email that needed the reader. Its weak spot was business
area in Chinese: it filed a work-permit renewal inquiry under legal instead of
sales, and a translation vendor's invoice under finance instead of vendor.

## One setting made the difference

In our first run, both Clef models missed emails that clearly needed a person:
a payroll approval, a sign-in code, a login alert. The cause was the same
every time. Clef had marked them as **suspicious**, and suspicious mail goes
to the paper trail, out of the inbox.

Clef returns a probability for every answer, so the fix was a threshold.
- **Clef 27B:** the real phishing email scored 0.97, and its false alarms scored between 0.59 and 0.77.
- **The result:** raising the cut-off from 0.5 to 0.9 kept the phishing catch and removed all three false alarms. On the 124 real emails, which contain no phishing, Clef 27B then flagged just one.
- **clef-flash:** it was less separable. It scored a sign-in code email at 0.94, so that false alarm survives even at 0.9.

This is what a calibrated model buys you. The LLM's self-reported confidence
sat around 0.95 for nearly everything, right or wrong, so a threshold on it
would mean nothing.

## Speed and footprint

On the DGX Spark, in BF16 at batch size 1:
- **clef-flash:** about 21 GB of GPU memory and roughly 0.5 seconds per email in our first run.
- **Clef 27B:** about 56 GB and 1.6 seconds.

With longer emails and the full set of business-area descriptions in the
prompt, both took about twice as long. Clef answers every question in one
forward pass, with no text generation, so the timing is predictable.

## What we're doing with it

- **The LLM stays the live classifier for now.** It keeps the inbox cleanest,
  and it handles business areas in every language we tested.
- **Clef 27B is the candidate to watch.** It finds more of what needs a
  person, it is well calibrated, and it runs entirely on local hardware. That
  matters for deployments where mail must not leave the building.
- **Before it could take over,** we want three things:
  - a larger mailbox that includes person-written business mail (this one had almost none);
  - confirmed labels on the real set;
  - better Chinese business-area routing.

## Caveats

- **Small samples:** 124 real emails and 16 test emails, one run per configuration.
- **Provisional labels:** the real-mailbox labels are a draft still being reviewed by a person. In particular, whether a routine Google security alert "needs" the reader is a judgement call, and it moves inbox precision.
- **Not like-for-like latency:** the LLM ran through a hosted API, and Clef ran locally.
- **Our task, not Clef's ceiling:** Clef was used zero-shot, on our question schema and wording, with the threshold we chose. Treat this as one measurement of one setup.
