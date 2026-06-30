# Connectors

The connector layer isolates external providers from the rest of the platform. Each connector is intentionally independent so that a provider can be replaced without changing application or domain code.

## Layout

Connectors live under `backend/src/fba_advisor/connectors/`:

```text
connectors/
  amazon/
    client.py
    exceptions.py
    interfaces.py
    mapper.py
    models.py
  brightdata/
    client.py
    exceptions.py
    interfaces.py
    mapper.py
    models.py
  keepa/
    client.py
    exceptions.py
    interfaces.py
    mapper.py
    models.py
  openai/
    client.py
    exceptions.py
    interfaces.py
    mapper.py
    models.py
```

## Responsibilities

Connectors may only handle infrastructure concerns:

- Authentication headers or request credentials.
- API calls through a small transport protocol.
- Response parsing and validation.
- Transformation from raw provider payloads to typed connector models.

Connectors must not contain product research rules, scoring, ranking, persistence workflows, or other business logic.

## Replaceability

Each connector exposes a protocol in `interfaces.py`, typed Pydantic models in `models.py`, provider-specific exceptions in `exceptions.py`, mapping functions in `mapper.py`, and a concrete API client in `client.py`.

Clients accept an injectable transport. Unit tests use fake transports, and production code can swap the transport or the whole connector implementation behind the protocol.

## Bright Data targets

The Bright Data connector is generic by design. `BrightDataTarget` currently declares target families for Amazon, Alibaba, and Google. The connector returns generic `BrightDataRecord` objects and preserves raw provider payloads for later provider-specific transformation outside business logic.
