# Architecture

QIP Guru Kit is an umbrella project, not one monolithic agent.

## Layers

1. Universal core
   - improvement method
   - governance classification prompts
   - aims, measures, PDSA, driver diagrams
   - publication/reporting discipline
   - data minimisation and de-identification checks

2. Source profiles
   - JSON files in `standards/`
   - one `global` profile plus country profiles
   - source URLs, use cases, and boundaries
   - no claim that one country's governance applies elsewhere

3. Agent skills
   - static markdown guides in `skills/`
   - tell an agent how to reason through QIP tasks
   - keep source-checking and local-governance cautions visible

4. CLI
   - deterministic file and scaffold work in `qip.py`
   - source profile inspection
   - local de-id scan/redact
   - no LLM calls, external APIs, MCP server, dashboard, or deployment

## Why This Shape

Agents are good at drafting, interviewing, adapting, and critique. CLIs are better for deterministic repeatable work. Source profiles make the kit portable without pretending that UK, US, Canadian, or Australian governance rules are interchangeable.

The right public product is therefore:

- QIP Guru as the public brand
- QIP Guru Kit as the open-source repo/toolkit
- skills as agent behaviour
- CLI as deterministic tooling
- country modules as source/governance adapters
- no engine until there is a separately reviewed runtime contract

## Module Contract

Every country module should define:

- source profile id
- scope summary
- what it is safe to use for
- primary sources with URLs
- incident-learning position
- explicit boundaries and non-claims

Modules must not include copied copyrighted guidance text. Link to primary sources and summarise use cases in original wording.

See `docs/PRODUCT_POSITIONING.md` for the current repo/toolkit/skills/CLI/engine decision.
