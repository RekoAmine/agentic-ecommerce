# Architecture

This repository follows Clean Architecture:

1. **Domain**: enterprise rules and framework-independent models.
2. **Application**: use cases and orchestration through ports.
3. **Ports**: interfaces that express dependencies as contracts.
4. **Infrastructure**: adapters for databases, AI runtimes, external APIs, and protocols.

The first milestone intentionally contains only scaffolding, contracts, configuration, and tests. Business logic will be introduced through use cases once product decisions are explicit.

## Evolution principles

- Keep domain code independent from frameworks and vendor SDKs.
- Add one adapter per provider or runtime.
- Prefer typed settings and dependency injection over global state.
- Keep agent orchestration behind ports so multiple AI agents can coexist.
- Keep data ingestion behind provider ports so multiple data sources can evolve independently.
