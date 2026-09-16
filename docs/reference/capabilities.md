---
slug: /capabilities
sidebar_position: 1
title: Core capabilities
description: Map application requirements to Libra OS runtime features and their configuration.
---

# Core capabilities

Libra OS supplies the runtime services below. Your application decides which
agents to call, what users may do, and how to present results and review work.

| Application need | Runtime feature | Start here |
| --- | --- | --- |
| Execute a prompted behavior | Persona and skill agents | [Create an agent](/creating-an-agent) |
| Reuse configuration across agents | Employee records and inheritance | [Employee YAML](/employee-yaml) |
| Retrieve company knowledge | Collections, bindings, and Knowledge Packs | [Knowledge](/workspaces-memory) |
| Call business systems | Custom tools, callbacks, and configured policies | [Tools](/employee-yaml#skills-and-tools) |
| Route models by task | Answer, planner, and skill model slots | [Model settings](/model-settings) |
| Retain context | Conversations, observations, persisted fields, house profiles | [Memory](/managing-memory) |
| Run work beyond one connection | Native jobs, persisted progress, outcome inspection | [Background tasks](/durable-runs) |
| Inspect installed agents | Managed-agent and operator registry APIs | [Listing agents](/listing-agents) |
| Build a review workflow | Approval groups and action records | [Desk example](/desk) |

## Knowledge Packs and skill packs

A Knowledge Pack supplies knowledge and associated configuration. A collection
is the indexed document resource an agent retrieves from. A skill/tool pack
supplies callable capabilities. Installing one does not imply that every agent
has access to it; configure bindings and tool availability.

## Models and data flow

Model IDs are served by your configured endpoint; they are not models bundled
inside the Libra OS binary. Configure local or hosted processing for every tier,
including embeddings and optional memory workers. Task complexity, model choice,
and available tools determine cost and latency.

See [Security](/security) for data flow and [Portability](/portability) for
capabilities that require external services or specific storage backends.

## SDK and applications

Install the Python package with `pip install libraos-sdk` and import
`from libraos import Client`. Source, API contracts, and language clients live
in [libraos/sdk](https://github.com/libraos/sdk).

[Libra Desk](/desk) is an application on this platform. A developer can use
the same runtime services from a different UI or a backend workflow.
