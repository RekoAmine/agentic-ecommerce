# Dashboard Next.js

Interface Dashboard pour Agentic Ecommerce.

## Architecture

- `src/app`: routes Next.js pour Dashboard, Produits, Produit, Score, Historique et Configuration.
- `src/lib/mcp`: frontière d'accès aux données. Le dashboard ne communique qu'avec `DashboardMcpClient`; aucun connecteur externe n'est importé.
- `src/features`: modules métier UI indépendants et testables.
- `src/components/ui`: composants Shadcn UI compatibles Tailwind.

Les données sont actuellement simulées via `SimulatedDashboardMcpClient`, ce qui permet de remplacer le transport par un client MCP réel sans modifier les pages.

## Commandes

```bash
npm install
npm run test
npm run typecheck
npm run build
```
