# Agentic Ecommerce

Private AI-agent decision-support platform for Amazon FBA research and operations.

This repository is intentionally designed as a long-lived personal platform, not a public SaaS. The initial version provides a professional Clean Architecture foundation without business logic.

## Repository layout

```text
backend/        Core backend package and application boundaries
mcp-server/     Model Context Protocol server package for agent tools
frontend/       Next.js dashboard that consumes MCP server data only
database/       PostgreSQL migrations and seed assets
docker/         Future Docker operational assets
docs/           Architecture and engineering documentation
```

## Architecture principles

- Clean Architecture with explicit dependency inversion.
- SOLID-friendly modules and small interfaces.
- Infrastructure isolated behind ports.
- Prepared for multiple AI agents and data providers.
- Testable Python modules with typed configuration.

## Tooling

- Python 3.13
- PostgreSQL
- Docker Compose
- uv
- Ruff
- Black
- Mypy
- Pytest
- Next.js / TypeScript / Tailwind / Shadcn UI / TanStack Query for the dashboard
- pre-commit

## Quick start

```bash
cp .env.example .env
uv sync
uv run pytest
uv run ruff check .
uv run black --check .
uv run mypy
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Development rules

Business logic should enter through application use cases and domain modules only after the relevant functional decision is clear. External services, model providers, data providers, and protocols must be implemented as infrastructure adapters behind ports.
