# Database

PostgreSQL schema assets live here.

- `migrations/`: ordered SQL migrations or future migration-tool output.
- `seeds/`: optional local-only seed data.

No business rules should be encoded directly in SQL unless they are invariant data-integrity constraints.
