# Agentic Ecommerce MCP Server

Extensible Model Context Protocol server for the Agentic Ecommerce platform.

## Goals

- Python 3.13 runtime.
- Official MCP SDK via `mcp.server.fastmcp.FastMCP`.
- Clean Architecture boundaries: tools call service ports, services return Pydantic schemas.
- SOLID-friendly modules with one MCP tool per file.
- Deterministic simulated data until real marketplace, fee, and analytics adapters are added.

## Layout

```text
mcp-server/
  server.py                  # executable wrapper
  config.py                  # compatibility config wrapper
  tools/                     # requested top-level extension directory
  services/                  # requested top-level extension directory
  schemas/                   # requested top-level extension directory
  prompts/                   # reusable MCP prompts
  exceptions/                # requested top-level extension directory
  interfaces/                # requested top-level extension directory
  utils/                     # requested top-level extension directory
  src/fba_mcp_server/
    server.py                # MCP app factory and registration
    config.py                # Pydantic settings
    tools/                   # one file per MCP tool
    services/                # use-case/service implementations
    schemas/                 # Pydantic request/response/domain DTOs
    exceptions/              # application exceptions
    interfaces/              # ports/protocols
    utils/                   # logging and shared utilities
  tests/
```

## Tools

- `search_products(query, marketplace="amazon_us", limit=5)`
- `analyse_product(asin, marketplace="amazon_us")`
- `calculate_margin(sale_price, landed_cost, amazon_fees, fulfillment_cost)`
- `score_product(asin, monthly_sales_estimate, review_count, margin_percent)`

All tools validate inputs with Pydantic and currently return simulated but schema-valid data.

## Configuration

Environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ENV` | `local` | Runtime environment label |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `BACKEND_BASE_URL` | `http://backend:8000` | Future backend integration endpoint |
| `MCP_SERVER_NAME` | `agentic-ecommerce-mcp` | MCP server name |

## Run

```bash
uv sync
uv run python mcp-server/server.py
```

## Quality checks

```bash
uv run pytest mcp-server/tests
uv run ruff check mcp-server/src mcp-server/tests
uv run mypy
```
