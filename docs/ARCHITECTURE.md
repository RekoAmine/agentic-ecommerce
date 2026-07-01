# Agentic Ecommerce — Documentation d'architecture officielle

> Statut : référence officielle du repository au 2026-07-01.  
> Source : analyse du code, de la configuration, des tests, des migrations, des workflows et de la documentation présents dans ce repository.  
> Règle de lecture : ce document décrit uniquement l'état réel du projet. Les capacités futures sont explicitement indiquées comme extensions ou roadmap.

## 1. Vision du projet

### But du projet

Agentic Ecommerce est une plateforme privée d'aide à la décision pour la recherche et les opérations Amazon FBA. Elle vise à assister l'utilisateur dans l'identification de produits, l'analyse de marché, l'estimation de marge, le scoring d'opportunité et la préparation de décisions humaines.

Le projet n'est pas conçu comme un SaaS public : le code existant le positionne comme une plateforme personnelle et durable, modulaire, testable, avec des frontières d'architecture explicites.

### Objectifs actuels

- Fournir une base Clean Architecture pour isoler domaine, cas d'usage, ports, adaptateurs et protocoles.
- Exposer des outils MCP pour la recherche produit, l'analyse, le calcul de marge et le scoring.
- Préparer l'intégration de fournisseurs externes : Amazon, Keepa, Bright Data et OpenAI.
- Persister les entités de recherche dans PostgreSQL via SQLAlchemy et Alembic.
- Fournir un dashboard Next.js consommant une frontière MCP simulée.
- Fournir des workflows n8n exportables pour automatiser des scénarios de recherche.

### Périmètre actuel

Le périmètre réellement implémenté couvre :

- Backend Python `fba_advisor` avec modèles domaine, services métier, ports, connecteurs, repositories SQLAlchemy et tracing par logs.
- Serveur MCP Python `fba_mcp_server` basé sur `FastMCP`, avec quatre tools enregistrés.
- Connecteurs HTTP basés sur `urllib` pour Amazon, Bright Data, Keepa et OpenAI.
- Adaptateurs locaux simulés Amazon et Keepa utilisés par les tools MCP.
- Dashboard Next.js avec données simulées derrière l'interface `DashboardMcpClient`.
- Schéma PostgreSQL pour catégories, produits, fournisseurs, revues, scores, devis et emails.
- Workflows n8n JSON exportés, désactivés par défaut.
- Tests unitaires backend, repositories, connecteurs, MCP et frontend.

### Périmètre futur

Le code prépare, mais n'implémente pas encore complètement :

- Une API HTTP backend publique : Docker et n8n référencent des URLs backend, mais aucun framework HTTP backend n'est présent.
- Un transport dashboard → MCP réel : le dashboard utilise actuellement un client simulé.
- L'injection de vrais credentials fournisseurs dans le graphe MCP : les tools utilisent aujourd'hui `LocalAmazonConnector` et `LocalKeepaConnector`.
- Une orchestration multi-agents IA : un port `DecisionAgent` existe, mais aucun agent concret n'est implémenté.
- Une couche de sécurité applicative complète : secrets et authentification sont surtout délégués aux variables d'environnement et aux connecteurs.

## 2. Architecture globale

### Vue d'ensemble

Le repository est organisé autour de trois sous-systèmes principaux :

1. **Backend** : package métier central `fba_advisor`, contenant domaine, services, ports et adaptateurs.
2. **MCP Server** : package `fba_mcp_server`, exposant des tools MCP et déléguant au backend via des use cases.
3. **Dashboard** : application Next.js, actuellement alimentée par un client MCP simulé.

Autour de ces sous-systèmes existent :

- **PostgreSQL** : base de persistance cible pour SQLAlchemy.
- **Connecteurs** : adaptateurs vers Amazon, Keepa, Bright Data et OpenAI.
- **Services** : logique métier pure ou orchestrée.
- **n8n** : workflows exportables présents dans `workflows/n8n/`, mais pas de service n8n dans `docker-compose.yml`.

### Backend

Le backend n'est pas un serveur HTTP autonome dans l'état actuel. Il est un package Python importable, structuré pour héberger la logique métier et les adaptateurs. Son point d'entrée applicatif principal est `ProductToolUseCases`, utilisé par le serveur MCP.

### MCP Server

Le serveur MCP crée une instance `FastMCP`, configure le logging, enregistre les tools `search_products`, `analyse_product`, `calculate_margin` et `score_product`, puis les encapsule dans `_safe_tool` pour convertir erreurs de validation et exceptions en dictionnaires contrôlés.

### Dashboard

Le dashboard est une application Next.js App Router. Il affiche overview, produits, détail produit, score, historique et configuration. Il ne consomme pas directement les connecteurs ou repositories backend ; il passe par l'interface `DashboardMcpClient`, implémentée aujourd'hui par `SimulatedDashboardMcpClient`.

### PostgreSQL

PostgreSQL est défini dans Docker Compose avec l'image `postgres:17-alpine`. La configuration Python utilise `DATABASE_URL`. Les entités SQLAlchemy et la migration Alembic décrivent le schéma actuel.

### Connecteurs

Chaque connecteur suit le même patron :

- `interfaces.py` : protocole abstrait.
- `models.py` : modèles Pydantic de payload provider.
- `mapper.py` : conversion du JSON brut vers modèles typés.
- `client.py` : authentification, requête HTTP, parsing, exceptions.
- `exceptions.py` : erreurs provider.

### Services

Les services métier disponibles sont : recherche produit, recherche fournisseur, marge, score, review et OpenAI/prompting. Ils dépendent de ports ou de connecteurs injectés, pas d'implémentations globales imposées.

### n8n

Deux workflows n8n sont présents :

- `daily-amazon-research.json` : recherche Amazon quotidienne, analyse, scoring, persistance, notification.
- `product-supplier-research.json` : produit validé, recherche fournisseurs, analyse, score, notification.

Ils sont exportables, désactivés par défaut, et reposent sur des URLs configurables. Aucun conteneur n8n n'est actuellement déclaré dans `docker-compose.yml`.

### Schéma Mermaid

```mermaid
flowchart TB
    User[Utilisateur] --> Dashboard[Dashboard Next.js]
    Dashboard --> DashboardClient[DashboardMcpClient simulé]

    User --> MCP[MCP Server FastMCP]
    MCP --> Tools[Tools MCP]
    Tools --> MCPAdapter[BackendProductResearchService]
    MCPAdapter --> UseCases[ProductToolUseCases]

    UseCases --> ProductService[ProductResearchService]
    UseCases --> MarginService[MarginService]
    UseCases --> ScoreService[ScoreService]
    UseCases --> Tracing[LoggingTracer]

    ProductService --> ProductCatalog[ProductCatalog port]
    ProductService --> ProductAnalytics[ProductAnalytics port]
    ProductService -. optionnel .-> ProductRepo[ProductRepository port]

    ProductCatalog --> AmazonAdapter[AmazonProductCatalog]
    ProductAnalytics --> KeepaAdapter[KeepaProductAnalytics]
    AmazonAdapter --> AmazonConnector[Amazon connector ou LocalAmazonConnector]
    KeepaAdapter --> KeepaConnector[Keepa connector ou LocalKeepaConnector]

    ScoreService -. optionnel .-> ScoreRepo[ScoreRepository]
    ProductRepo -. SQLAlchemy .-> PostgreSQL[(PostgreSQL)]
    ScoreRepo -. SQLAlchemy .-> PostgreSQL

    OpenAIService[OpenAIService] --> PromptRepo[PromptRepository]
    OpenAIService --> OpenAIConnector[OpenAI connector]
    SupplierService[SupplierResearchService] --> SupplierDirectory[SupplierDirectory port]
    SupplierService -. optionnel .-> SupplierRepo[SupplierRepository]
    SupplierRepo -. SQLAlchemy .-> PostgreSQL

    N8N[n8n workflows exportés] -. HTTP attendu .-> MCP
    N8N -. HTTP attendu .-> BackendHTTP[Backend HTTP futur/non présent]
```

## 3. Arborescence

### Arborescence complète des fichiers suivis

```text
.env.example
Dockerfile
README.md
alembic.ini
backend/
  src/fba_advisor/
    __init__.py
    application/__init__.py
    application/product_tools.py
    config.py
    connectors/__init__.py
    connectors/amazon/__init__.py
    connectors/amazon/client.py
    connectors/amazon/exceptions.py
    connectors/amazon/interfaces.py
    connectors/amazon/mapper.py
    connectors/amazon/models.py
    connectors/brightdata/__init__.py
    connectors/brightdata/client.py
    connectors/brightdata/exceptions.py
    connectors/brightdata/interfaces.py
    connectors/brightdata/mapper.py
    connectors/brightdata/models.py
    connectors/keepa/__init__.py
    connectors/keepa/client.py
    connectors/keepa/exceptions.py
    connectors/keepa/interfaces.py
    connectors/keepa/mapper.py
    connectors/keepa/models.py
    connectors/openai/__init__.py
    connectors/openai/client.py
    connectors/openai/exceptions.py
    connectors/openai/interfaces.py
    connectors/openai/mapper.py
    connectors/openai/models.py
    database/__init__.py
    database/base.py
    database/session.py
    domain/__init__.py
    domain/models.py
    infrastructure/__init__.py
    infrastructure/tracing.py
    models/__init__.py
    models/entities.py
    ports/__init__.py
    ports/agents.py
    ports/catalog.py
    ports/data_providers.py
    ports/repositories.py
    ports/reviews.py
    ports/tracing.py
    repositories/__init__.py
    repositories/connectors.py
    repositories/sqlalchemy.py
    services/__init__.py
    services/margin/__init__.py
    services/margin/service.py
    services/openai/__init__.py
    services/openai/service.py
    services/product/__init__.py
    services/product/service.py
    services/review/__init__.py
    services/review/service.py
    services/score/__init__.py
    services/score/config.yaml
    services/score/service.py
    services/supplier/__init__.py
    services/supplier/service.py
  tests/
    connectors/test_connectors.py
    repositories/test_sqlalchemy_repositories.py
    services/test_business_services.py
    test_backend_settings.py
database/README.md
docker/README.md
docker-compose.yml
docs/ARCHITECTURE.md
docs/architecture.md
docs/connectors.md
docs/n8n-workflows.md
frontend/
  README.md
  eslint.config.mjs
  next-env.d.ts
  next.config.ts
  package-lock.json
  package.json
  postcss.config.mjs
  tailwind.config.ts
  tsconfig.json
  vitest.config.ts
  src/__tests__/mcp-client.test.ts
  src/__tests__/score.test.ts
  src/app/configuration/page.tsx
  src/app/globals.css
  src/app/history/page.tsx
  src/app/layout.tsx
  src/app/page.tsx
  src/app/products/[id]/page.tsx
  src/app/products/page.tsx
  src/app/providers.tsx
  src/app/score/page.tsx
  src/components/ui/badge.tsx
  src/components/ui/card.tsx
  src/features/configuration/queries.ts
  src/features/dashboard/queries.ts
  src/features/history/queries.ts
  src/features/products/queries.ts
  src/features/score/score.ts
  src/lib/mcp/client.ts
  src/lib/query/keys.ts
  src/lib/utils.ts
  src/types/dashboard.ts
mcp-server/
  README.md
  config.py
  prompts/product_research.md
  server.py
  src/fba_mcp_server/__init__.py
  src/fba_mcp_server/application/__init__.py
  src/fba_mcp_server/config.py
  src/fba_mcp_server/exceptions/__init__.py
  src/fba_mcp_server/exceptions/base.py
  src/fba_mcp_server/infrastructure/__init__.py
  src/fba_mcp_server/interfaces/__init__.py
  src/fba_mcp_server/interfaces/product_service.py
  src/fba_mcp_server/ports/__init__.py
  src/fba_mcp_server/ports/tools.py
  src/fba_mcp_server/prompts/__init__.py
  src/fba_mcp_server/schemas/__init__.py
  src/fba_mcp_server/schemas/products.py
  src/fba_mcp_server/schemas/requests.py
  src/fba_mcp_server/schemas/responses.py
  src/fba_mcp_server/server.py
  src/fba_mcp_server/services/__init__.py
  src/fba_mcp_server/services/product_research.py
  src/fba_mcp_server/tools/__init__.py
  src/fba_mcp_server/tools/analyse_product.py
  src/fba_mcp_server/tools/calculate_margin.py
  src/fba_mcp_server/tools/dependencies.py
  src/fba_mcp_server/tools/score_product.py
  src/fba_mcp_server/tools/search_products.py
  src/fba_mcp_server/utils/__init__.py
  src/fba_mcp_server/utils/logging.py
  tests/test_mcp_settings.py
  tests/test_tools.py
migrations/env.py
migrations/script.py.mako
migrations/versions/20260701_0001_create_persistence_entities.py
prompts/ai_scoring.v1.md
prompts/brandability.v1.md
prompts/competition_analysis.v1.md
prompts/differentiation.v1.md
prompts/review_analysis.v1.md
prompts/summary.v1.md
pyproject.toml
uv.lock
workflows/n8n/daily-amazon-research.json
workflows/n8n/product-supplier-research.json
```

### Rôle de chaque dossier

| Dossier | Rôle |
| --- | --- |
| `backend/` | Package Python métier central et tests associés. |
| `backend/src/fba_advisor/domain/` | Modèles domaine indépendants des frameworks. |
| `backend/src/fba_advisor/application/` | Cas d'usage applicatifs et orchestration métier. |
| `backend/src/fba_advisor/ports/` | Interfaces/protocoles pour inversion de dépendance. |
| `backend/src/fba_advisor/services/` | Services métier : recherche, score, marge, review, supplier, OpenAI. |
| `backend/src/fba_advisor/connectors/` | Adaptateurs provider externes. |
| `backend/src/fba_advisor/repositories/` | Adaptateurs de persistance et adaptateurs connecteurs vers ports métier. |
| `backend/src/fba_advisor/models/` | Entités SQLAlchemy persistées. |
| `backend/src/fba_advisor/database/` | Base SQLAlchemy et création de sessions. |
| `backend/src/fba_advisor/infrastructure/` | Infrastructure transversale, actuellement tracing par logging. |
| `mcp-server/` | Serveur MCP et tests MCP. |
| `mcp-server/src/fba_mcp_server/tools/` | Fonctions exposées comme tools MCP. |
| `mcp-server/src/fba_mcp_server/schemas/` | Contrats Pydantic d'entrées/sorties MCP. |
| `mcp-server/src/fba_mcp_server/services/` | Adaptateur MCP vers use cases backend. |
| `frontend/` | Dashboard Next.js/TypeScript. |
| `frontend/src/app/` | Pages App Router. |
| `frontend/src/features/` | Hooks et logique par feature UI. |
| `frontend/src/lib/mcp/` | Frontière client MCP dashboard, actuellement simulée. |
| `migrations/` | Configuration et versions Alembic. |
| `database/` | Documentation/assets base de données. |
| `prompts/` | Prompts OpenAI versionnés chargés par `PromptRepository`. |
| `workflows/n8n/` | Exports JSON de workflows n8n. |
| `docs/` | Documentation d'architecture, connecteurs et workflows. |
| `docker/` | Documentation opérationnelle Docker. |

## 4. Clean Architecture

### Couches

1. **Domain**
   - Fichiers : `backend/src/fba_advisor/domain/models.py`.
   - Contient les dataclasses métier et enums : `Product`, `Supplier`, `MarginInput`, `MarginEstimate`, `ProductScoreInput`, `ProductScoringInput`, `ProductScore`, `ProductReview`, etc.
   - Ne dépend pas de SQLAlchemy, Pydantic, MCP, Next.js ou provider externe.

2. **Application / Use cases**
   - Fichiers : `backend/src/fba_advisor/application/product_tools.py`.
   - Orchestre les services métier pour répondre aux besoins des outils produit.
   - Peut dépendre du domaine, des services et de ports comme `Tracer`.

3. **Ports**
   - Fichiers : `backend/src/fba_advisor/ports/*.py`, `mcp-server/src/fba_mcp_server/interfaces/*.py`.
   - Définissent les contrats : catalogues, analytics, repositories, tracing, agents, services MCP.
   - Permettent l'injection d'adaptateurs remplaçables.

4. **Services métier**
   - Fichiers : `backend/src/fba_advisor/services/**/service.py`.
   - Implémentent calculs, validations, orchestration locale et scoring.
   - Ne doivent pas appeler directement les APIs externes ; ils passent par ports ou connecteurs injectés.

5. **Infrastructure / Adapters**
   - Connecteurs providers, repositories SQLAlchemy, tracing logging, serveur MCP, client dashboard simulé.
   - Convertissent le monde externe vers les contrats internes.

6. **Frameworks & delivery mechanisms**
   - MCP `FastMCP`, Next.js, Docker Compose, Alembic, PostgreSQL, n8n exports.

### Dépendances

Les dépendances doivent pointer vers l'intérieur :

- Dashboard/MCP → schemas/adapters → use cases → services → domain/ports.
- Repositories/connecteurs implémentent des ports, mais les services ne connaissent pas les détails provider.
- Les entités SQLAlchemy restent dans la couche persistance, distinctes des dataclasses domaine.

### Schéma Mermaid

```mermaid
flowchart LR
    subgraph Outer[Frameworks & Infrastructure]
      Next[Next.js Dashboard]
      MCP[FastMCP Server]
      SQLA[SQLAlchemy Repositories]
      Providers[Amazon/Keepa/BrightData/OpenAI Clients]
      Docker[Docker/Alembic/n8n]
    end

    subgraph Adapters[Interface Adapters]
      MCPTools[MCP Tools]
      MCPService[BackendProductResearchService]
      ConnectorRepos[AmazonProductCatalog / KeepaProductAnalytics]
    end

    subgraph Application[Application]
      UseCases[ProductToolUseCases]
      Services[Product, Supplier, Score, Margin, Review, OpenAI Services]
      Ports[Ports / Protocols]
    end

    subgraph Domain[Domain]
      Models[Domain dataclasses and enums]
    end

    Next --> MCPTools
    MCP --> MCPTools
    MCPTools --> MCPService
    MCPService --> UseCases
    UseCases --> Services
    Services --> Ports
    Services --> Models
    SQLA --> Ports
    ConnectorRepos --> Ports
    ConnectorRepos --> Providers
    Docker --> SQLA
```

## 5. Flux de données

### Flux principal actuel MCP produit

1. Un client MCP appelle un tool.
2. Le tool valide les paramètres via un modèle Pydantic de request.
3. Le tool récupère `get_product_research_service()`.
4. Cette factory construit le graphe : local Amazon + local Keepa → repositories/adapters connecteurs → services backend → `ProductToolUseCases` → `BackendProductResearchService`.
5. L'adaptateur MCP délègue aux use cases backend.
6. Les use cases appellent les services métier.
7. Les services utilisent les ports catalog/analytics/repository selon les dépendances injectées.
8. Les adaptateurs de connecteurs convertissent les modèles provider en modèles domaine.
9. Les résultats domaine sont remappés en schemas MCP.
10. Le tool retourne une enveloppe `ToolResponse` sérialisée en JSON.

### Flux générique attendu

```text
Dashboard ou Client MCP
↓
MCP Server / Tools
↓
MCP service adapter
↓
Backend application use cases
↓
Services métier
↓
Ports
↓
Repositories / Connecteurs
↓
PostgreSQL / APIs externes
↓
Mapping schemas
↓
Retour utilisateur
```

### Diagramme Mermaid

```mermaid
sequenceDiagram
    participant U as Utilisateur ou Agent
    participant M as MCP Tool
    participant A as BackendProductResearchService
    participant UC as ProductToolUseCases
    participant S as Services métier
    participant P as Ports
    participant R as Repositories/Adapters
    participant E as APIs externes ou Local connectors
    participant DB as PostgreSQL

    U->>M: Appel tool + paramètres
    M->>M: Validation Pydantic
    M->>A: Délégation schema MCP
    A->>UC: Appel use case backend
    UC->>S: Orchestration métier
    S->>P: Appel port abstrait
    P->>R: Implémentation injectée
    alt Données externes
        R->>E: HTTP provider ou connecteur local
        E-->>R: Payload provider
        R-->>S: Modèle domaine normalisé
    else Persistance optionnelle
        R->>DB: SQLAlchemy
        DB-->>R: Entité persistée
        R-->>S: Modèle domaine
    end
    S-->>UC: Résultat métier
    UC-->>A: DTO/dict métier
    A-->>M: Schema MCP
    M-->>U: ToolResponse JSON
```

## 6. MCP

### Serveur

- Module : `mcp-server/src/fba_mcp_server/server.py`.
- Framework : `mcp.server.fastmcp.FastMCP`.
- Configuration : `McpServerSettings` via Pydantic Settings.
- Logging : `configure_logging(log_level)`.
- Gestion d'erreurs : `_safe_tool` retourne `{error: "validation_error", details: ...}` pour `ValidationError` et `{error: "tool_execution_error", details: ...}` pour les autres exceptions.

### Enveloppe de réponse

Tous les tools réussis retournent :

```json
{
  "data": {},
  "simulated": false,
  "message": "Response generated successfully."
}
```

### Tools existants

| Tool | Rôle | Paramètres | Retour | Dépendances |
| --- | --- | --- | --- | --- |
| `search_products` | Recherche de produits correspondant à une requête. | `query: str` 2-120 caractères, `marketplace: str` défaut `amazon_us`, enum `amazon_us|amazon_fr|amazon_de|amazon_uk`, `limit: int` défaut 5, max 20. | `ToolResponse[list[ProductSummary]]` avec ASIN, titre, marketplace, prix, devise, ventes mensuelles estimées, nombre d'avis, rating, URL Amazon. | `SearchProductsRequest`, `BackendProductResearchService.search_products`, `ProductToolUseCases.search_products`, `ProductResearchService`, `AmazonProductCatalog`, `LocalAmazonConnector`, `KeepaProductAnalytics`, `LocalKeepaConnector`. |
| `analyse_product` | Analyse structurée d'un ASIN. | `asin: str` longueur 10, `marketplace: str` défaut `amazon_us`. | `ToolResponse[ProductAnalysis]` avec demand level, competition level, risk level, opportunities, warnings. | `AnalyseProductRequest`, `ProductToolUseCases.analyse_product`, recherche produit backend, règles heuristiques dans use case. |
| `calculate_margin` | Calcul financier de marge FBA. | `sale_price: Decimal > 0`, `landed_cost: Decimal >= 0`, `amazon_fees: Decimal >= 0`, `fulfillment_cost: Decimal >= 0`. | `ToolResponse[MarginBreakdown]` avec prix, coût rendu, frais Amazon, fulfillment, profit net, marge %. | `CalculateMarginRequest`, `ProductToolUseCases.calculate_margin`, `MarginService`. |
| `score_product` | Score une opportunité produit. | `asin: str` longueur 10, `monthly_sales_estimate: int >= 0`, `review_count: int >= 0`, `margin_percent: Decimal`. | `ToolResponse[ProductScore]` avec ASIN, score 1-100, recommandation, rationale. | `ScoreProductRequest`, `ProductToolUseCases.score_product`, `ScoreService`. |

### Schemas MCP

- `Marketplace` : `amazon_us`, `amazon_fr`, `amazon_de`, `amazon_uk`.
- `ProductSummary` : résultat de découverte produit.
- `ProductAnalysis` : analyse structurée.
- `MarginBreakdown` : détail financier.
- `ProductScore` : décision de scoring.
- `ToolResponse` : enveloppe commune.

## 7. Services

| Service | Fichier | Responsabilités | Dépendances |
| --- | --- | --- | --- |
| `ProductResearchService` | `backend/src/fba_advisor/services/product/service.py` | Normaliser la requête, rechercher des produits via `ProductCatalog`, enrichir via `ProductAnalytics`, persister via `ProductRepository` si injecté. | Ports `ProductCatalog`, `ProductAnalytics`, `ProductRepository`. |
| `SupplierResearchService` | `backend/src/fba_advisor/services/supplier/service.py` | Rechercher des fournisseurs via `SupplierDirectory`, persister si demandé, trier par fiabilité puis coût connu. | Ports `SupplierDirectory`, `SupplierRepository`. |
| `MarginService` | `backend/src/fba_advisor/services/margin/service.py` | Valider les entrées financières, calculer referral fee, coût total, profit, taux de marge. | Modèles domaine `MarginInput`, `MarginEstimate`. |
| `ScoreService` | `backend/src/fba_advisor/services/score/service.py` | Calculer un score legacy et un score configurable multi-critères ; charger une configuration YAML simple ; persister optionnellement les scores. | `ProductScoreInput`, `ProductScoringInput`, `ScoreRepository`, `ScoreConfig`. |
| `ReviewService` | `backend/src/fba_advisor/services/review/service.py` | Valider et soumettre une revue humaine ; lister les revues d'un produit. | `ReviewRepository`, `ProductReview`, `ReviewDecision`. |
| `OpenAIService` | `backend/src/fba_advisor/services/openai/service.py` | Charger des prompts versionnés et exécuter les fonctions IA : concurrence, résumé, avis, brandabilité, différenciation, scoring IA. | `OpenAIConnector`, `PromptRepository`, prompts dans `prompts/`. |
| `BackendProductResearchService` | `mcp-server/src/fba_mcp_server/services/product_research.py` | Adapter les schemas MCP vers `ProductToolUseCases` et remapper les résultats vers schemas MCP. | `ProductToolUseCases`, schemas MCP. |

## 8. Connecteurs

### Amazon

- **Fournisseur** : Amazon API compatible avec endpoint `/products/search`.
- **Rôle** : rechercher des produits sans appliquer de décisions métier.
- **Authentification** : header `Authorization: Amazon <access_key>:<secret_key>` et `X-Amz-Region`.
- **Modèles** : `AmazonCredentials`, `AmazonProduct`, `AmazonSearchResponse`.
- **Interfaces** : `AmazonConnector.search_products(query)` et `provider_name`.
- **Transport** : `AmazonTransport.get(url, headers)`, implémentation `UrllibAmazonTransport`.
- **Mapping** : payload JSON objet contenant `items`; chaque item requiert `asin` et `title`, accepte `price` et `currency` optionnels.

### Keepa

- **Fournisseur** : Keepa API compatible avec endpoint `/product`.
- **Rôle** : récupérer des métriques produit par ASIN ou valeur.
- **Authentification** : clé API transmise en query string `key`.
- **Modèles** : `KeepaCredentials`, `KeepaProduct`, `KeepaResponse`.
- **Interfaces** : `KeepaConnector.fetch(value)` et `provider_name`.
- **Transport** : `KeepaTransport.get(url, headers)`, implémentation `UrllibKeepaTransport`.
- **Mapping** : payload JSON objet contenant `products`; chaque product requiert `asin`, accepte `title`, `salesRank`.

### Bright Data

- **Fournisseur** : Bright Data.
- **Rôle** : collecter des données génériques pour cibles Amazon, Alibaba et Google.
- **Authentification** : header `Authorization: Bearer <api_token>` ; zone optionnelle en paramètre `zone`.
- **Modèles** : `BrightDataCredentials`, `BrightDataTarget`, `BrightDataRecord`, `BrightDataResponse`.
- **Interfaces** : `BrightDataConnector.collect(target, query)` et `provider_name`.
- **Transport** : `BrightDataTransport.get(url, headers)`, implémentation `UrllibBrightDataTransport`.
- **Mapping** : payload avec `records` ou `data`; chaque record générique expose `identifier`, `title`, `url`, `raw`.

### OpenAI

- **Fournisseur** : OpenAI API compatible `/embeddings` et `/responses`.
- **Rôle** : embeddings et génération de texte à partir de prompts versionnés.
- **Authentification** : header `Authorization: Bearer <api_key>` ; `OpenAI-Organization` optionnel.
- **Modèles** : `OpenAICredentials`, `OpenAIEmbedding`, `OpenAIResponse`, `OpenAICompletion`.
- **Interfaces** : `OpenAIConnector.fetch(value)`, `OpenAIConnector.complete(instructions, value)`, `provider_name`.
- **Transport** : `OpenAITransport.post(url, headers, body)`, implémentation `UrllibOpenAITransport`.
- **Mapping** : embeddings via `data[].embedding`; completions via `output_text` ou `output[].content[].text`.

### Connecteurs locaux MCP

- `LocalAmazonConnector` : retourne deux produits simulés `B0TEST0001` et `B0TEST0002` avec prix, devise, ventes, avis et rating.
- `LocalKeepaConnector` : retourne un `KeepaProduct` avec `sales_rank=900`.
- Ils sont utilisés dans `get_product_research_service()` pour permettre un MCP fonctionnel sans credentials externes.

## 9. Base de données

### Entités persistées

| Entité | Table | Rôle | Relations |
| --- | --- | --- | --- |
| `Category` | `categories` | Arbre de catégories produit. | Auto-référence parent/enfants ; 1 catégorie → N produits. |
| `Supplier` | `suppliers` | Fournisseur capable de sourcer des produits. | 1 fournisseur → N produits, quotes, emails. Contrainte unique `(source, identifier)`. |
| `Product` | `products` | Produit candidat normalisé pour la recherche FBA. | N:1 category, N:1 supplier ; 1 produit → N reviews, scores, quotes, emails. Contrainte unique `(source, identifier)`. |
| `Review` | `reviews` | Revue humaine d'une opportunité produit. | N:1 produit optionnel ; index `product_identifier`. |
| `Score` | `scores` | Score calculé d'une opportunité. | N:1 produit optionnel ; index `product_identifier`. |
| `Quote` | `quotes` | Devis fournisseur pour un produit. | N:1 produit optionnel, N:1 fournisseur optionnel. |
| `Email` | `emails` | Email échangé avec un fournisseur au sujet d'un produit. | N:1 produit optionnel, N:1 fournisseur optionnel. |

Toutes les entités persistées héritent de `TimestampMixin` avec `created_at` et `updated_at`.

### Diagramme Mermaid

```mermaid
erDiagram
    CATEGORY ||--o{ CATEGORY : parent_children
    CATEGORY ||--o{ PRODUCT : classifies
    SUPPLIER ||--o{ PRODUCT : supplies
    PRODUCT ||--o{ REVIEW : has
    PRODUCT ||--o{ SCORE : has
    PRODUCT ||--o{ QUOTE : has
    SUPPLIER ||--o{ QUOTE : provides
    PRODUCT ||--o{ EMAIL : concerns
    SUPPLIER ||--o{ EMAIL : exchanges

    CATEGORY {
      int id PK
      string name UK
      int parent_id FK
      datetime created_at
      datetime updated_at
    }
    SUPPLIER {
      int id PK
      string identifier
      string name
      string source
      int minimum_order_quantity
      numeric unit_cost
      string currency
      numeric reliability_score
      json attributes
      datetime created_at
      datetime updated_at
    }
    PRODUCT {
      int id PK
      string identifier
      string title
      string source
      numeric price
      string currency
      int sales_rank
      json attributes
      int category_id FK
      int supplier_id FK
      datetime created_at
      datetime updated_at
    }
    REVIEW {
      int id PK
      int product_id FK
      string product_identifier
      string decision
      string reviewer
      text notes
      datetime reviewed_at
      datetime created_at
      datetime updated_at
    }
    SCORE {
      int id PK
      int product_id FK
      string product_identifier
      numeric value
      text rationale
      json inputs
      datetime created_at
      datetime updated_at
    }
    QUOTE {
      int id PK
      int product_id FK
      int supplier_id FK
      numeric unit_cost
      string currency
      int minimum_order_quantity
      int lead_time_days
      text terms
      datetime created_at
      datetime updated_at
    }
    EMAIL {
      int id PK
      int product_id FK
      int supplier_id FK
      string direction
      string subject
      text body
      datetime sent_at
      datetime created_at
      datetime updated_at
    }
```

## 10. Dépendances externes

### Python runtime

| Dépendance | Utilisation |
| --- | --- |
| `pydantic` | Modèles typés connectors et schemas MCP. |
| `pydantic-settings` | Configuration MCP via variables d'environnement et `.env`. |
| `mcp` | Serveur MCP `FastMCP`. |
| `SQLAlchemy` | ORM et mapping entités persistées. |
| `alembic` | Migrations de schéma. |
| `psycopg[binary]` | Driver PostgreSQL. |

### Python dev

| Dépendance | Utilisation |
| --- | --- |
| `black` | Formatage Python. |
| `mypy` | Typage statique strict. |
| `pre-commit` | Hooks de qualité. |
| `pytest` | Tests. |
| `ruff` | Lint Python. |

### Frontend runtime

| Dépendance | Utilisation |
| --- | --- |
| `next` | Framework React App Router. |
| `react`, `react-dom` | UI dashboard. |
| `@tanstack/react-query` | Hooks de chargement/cache côté frontend. |
| `@radix-ui/react-slot` | Primitive UI utilisée par composants. |
| `class-variance-authority`, `clsx`, `tailwind-merge` | Composition de classes CSS. |
| `lucide-react` | Icônes. |

### Frontend dev

| Dépendance | Utilisation |
| --- | --- |
| `typescript` | Typage frontend. |
| `eslint`, `eslint-config-next` | Lint frontend. |
| `tailwindcss`, `postcss`, `autoprefixer` | CSS utilitaire. |
| `vitest`, `jsdom`, `@testing-library/react` | Tests frontend. |
| `@types/*` | Types Node/React. |

### Infrastructure

| Dépendance | Utilisation |
| --- | --- |
| Docker | Image Python runtime et orchestration locale. |
| PostgreSQL 17 Alpine | Base relationnelle. |
| uv | Gestion d'environnement/dépendances Python et image Docker. |
| n8n | Workflows exportables, non conteneurisé ici. |

## 11. Variables d'environnement

| Nom | Description | Obligatoire | Valeur par défaut |
| --- | --- | --- | --- |
| `APP_ENV` | Environnement applicatif backend/MCP. | Non | `local` |
| `LOG_LEVEL` | Niveau de logs backend/MCP. | Non | `INFO` |
| `POSTGRES_DB` | Nom de la base PostgreSQL Docker. | Non pour Docker local | `agentic_ecommerce` |
| `POSTGRES_USER` | Utilisateur PostgreSQL Docker. | Non pour Docker local | `agentic_ecommerce` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL Docker. | Non pour Docker local, requis en production sécurisée | `change_me` |
| `POSTGRES_HOST` | Hôte PostgreSQL documenté dans `.env.example`. | Non | `postgres` |
| `POSTGRES_PORT` | Port PostgreSQL documenté dans `.env.example`. | Non | `5432` |
| `DATABASE_URL` | URL SQLAlchemy/psycopg de connexion backend. | Non local, oui pour persistance réelle | `postgresql://agentic_ecommerce:change_me@postgres:5432/agentic_ecommerce` |
| `BACKEND_BASE_URL` | Base URL attendue par la config MCP. | Non | `http://backend:8000` |
| `MCP_SERVER_NAME` | Nom logique du serveur MCP. | Non | `agentic-ecommerce-mcp` |
| `MCP_HTTP_URL` | URL n8n attendue pour tools MCP HTTP. | Oui pour workflows n8n réels | `http://mcp-server:8000/tools/...` dans la doc n8n |
| `AGENTIC_API_URL` | URL n8n de persistance produits scorés. | Oui pour workflow n8n réel | `http://backend:8000/products` dans la doc n8n |
| `SUPPLIER_SEARCH_URL` | URL n8n de recherche fournisseurs. | Oui pour workflow fournisseur réel | `http://backend:8000/suppliers/search` dans la doc n8n |
| `SUPPLIER_ANALYSIS_URL` | URL n8n d'analyse fournisseurs. | Oui pour workflow fournisseur réel | `http://backend:8000/suppliers/analyse` dans la doc n8n |
| `SUPPLIER_SCORE_URL` | URL n8n de scoring fournisseurs. | Oui pour workflow fournisseur réel | `http://backend:8000/suppliers/score` dans la doc n8n |
| `NOTIFICATION_WEBHOOK_URL` | Webhook notification n8n. | Oui pour notification réelle | Aucune |
| `AMAZON_DAILY_QUERY` | Requête quotidienne n8n. | Non | `amazon fba product opportunities` |
| `AMAZON_MARKETPLACE` | Marketplace n8n. | Non | `amazon_us` |

Remarque : les credentials Amazon, Keepa, Bright Data et OpenAI existent sous forme de modèles dans le code, mais aucune variable d'environnement dédiée n'est encore câblée dans une factory de production.

## 12. Configuration

### Configuration Python

- `pyproject.toml` impose Python `>=3.13`.
- Ruff cible Python 3.13, line length 100, sources `backend/src` et `mcp-server/src`.
- Black utilise line length 100.
- Mypy est strict, avec `mypy_path` sur `backend/src` et `mcp-server/src`, packages `fba_advisor` et `fba_mcp_server`.
- Pytest charge `backend/tests` et `mcp-server/tests`, avec `pythonpath` configuré pour les deux packages.

### Configuration Docker

- `Dockerfile` construit une image Python 3.13 slim.
- `uv` est copié depuis `ghcr.io/astral-sh/uv:0.5.4`.
- Le build copie `pyproject.toml`, `README.md`, `backend` et `mcp-server`.
- La commande par défaut vérifie que `fba_advisor` et `fba_mcp_server` sont importables.
- `docker-compose.yml` définit `postgres`, `backend` et `mcp-server`.
- Les services backend et MCP utilisent la même image et montent leurs dossiers respectifs.
- Aucun port HTTP backend/MCP n'est exposé explicitement dans Compose à ce stade.

### Configuration MCP

- `McpServerSettings` charge `.env`, ignore les variables extra, est frozen.
- Variables : `APP_ENV`, `LOG_LEVEL`, `BACKEND_BASE_URL`, `MCP_SERVER_NAME`.
- `create_server()` configure les logs, crée `FastMCP(server_name)`, enregistre les quatre tools et retourne le serveur.
- L'objet global `mcp = create_server()` est créé à l'import du module.

## 13. Flux d'exécution : « Trouve-moi les meilleurs produits Amazon. »

### Interprétation dans l'état actuel

Dans le code présent, la demande doit être transformée en appel du tool `search_products` avec une requête textuelle, par exemple :

```json
{
  "query": "meilleurs produits Amazon",
  "marketplace": "amazon_us",
  "limit": 5
}
```

Le code ne contient pas encore de LLM orchestrateur qui convertirait automatiquement la phrase utilisateur en tool call. Le flux ci-dessous décrit ce qui se passe une fois le tool MCP appelé.

### Étapes exactes

1. Le client appelle `search_products(query="meilleurs produits Amazon", marketplace="amazon_us", limit=5)`.
2. Le tool construit `SearchProductsRequest`.
3. Pydantic valide : query longueur 2-120, marketplace enum, limit positif ≤ 20.
4. Le tool appelle `get_product_research_service()`.
5. La factory crée :
   - `LocalAmazonConnector`,
   - `AmazonProductCatalog`,
   - `LocalKeepaConnector`,
   - `KeepaProductAnalytics`,
   - `ProductResearchService`,
   - `MarginService`,
   - `ScoreService`,
   - `LoggingTracer`,
   - `ProductToolUseCases`,
   - `BackendProductResearchService`.
6. `BackendProductResearchService.search_products()` délègue à `ProductToolUseCases.search_products(query, limit)`.
7. `ProductToolUseCases` ouvre un span `product.search`, appelle `ProductResearchService.search(query)`, tronque à `limit`.
8. `ProductResearchService` trim la query, appelle `AmazonProductCatalog.search()`.
9. `AmazonProductCatalog` appelle `LocalAmazonConnector.search_products()`.
10. Le connecteur local retourne deux produits simulés avec ASIN, titre, prix, devise, ventes estimées, review_count et rating.
11. `AmazonProductCatalog` mappe chaque produit en `fba_advisor.domain.models.Product`.
12. `ProductResearchService` enrichit chaque produit via `KeepaProductAnalytics.enrich()`.
13. `KeepaProductAnalytics` appelle `LocalKeepaConnector.fetch(asin)` et ajoute `sales_rank=900` si l'ASIN correspond.
14. Aucun `ProductRepository` n'est injecté dans cette factory MCP : les produits ne sont pas persistés.
15. `BackendProductResearchService` mappe les `Product` domaine vers `ProductSummary` MCP.
16. Le tool retourne `ToolResponse(data=[...], simulated=false, message=...)`.

### Diagramme Mermaid

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant Client as Client MCP/Agent
    participant Tool as search_products
    participant Deps as get_product_research_service
    participant Adapter as BackendProductResearchService
    participant UC as ProductToolUseCases
    participant PS as ProductResearchService
    participant Cat as AmazonProductCatalog
    participant Amazon as LocalAmazonConnector
    participant Analytics as KeepaProductAnalytics
    participant Keepa as LocalKeepaConnector

    User->>Client: "Trouve-moi les meilleurs produits Amazon"
    Client->>Tool: search_products(query, marketplace, limit)
    Tool->>Tool: Valide SearchProductsRequest
    Tool->>Deps: Construit graphe de dépendances
    Deps-->>Tool: ProductResearchService MCP
    Tool->>Adapter: search_products(request)
    Adapter->>UC: search_products(query, limit)
    UC->>UC: span product.search
    UC->>PS: search(query)
    PS->>Cat: search(query)
    Cat->>Amazon: search_products(query)
    Amazon-->>Cat: AmazonSearchResponse simulé
    Cat-->>PS: list[Product]
    PS->>Analytics: enrich(product)
    Analytics->>Keepa: fetch(asin)
    Keepa-->>Analytics: KeepaResponse simulé
    Analytics-->>PS: Product enrichi
    PS-->>UC: produits domaine
    UC-->>Adapter: produits limités
    Adapter-->>Tool: list[ProductSummary]
    Tool-->>Client: ToolResponse JSON
    Client-->>User: Liste des produits
```

## 14. Principes d'architecture

### Clean Architecture

Le projet sépare explicitement le domaine, les cas d'usage, les ports et les adaptateurs. Les modèles domaine sont indépendants des frameworks. Les connecteurs et repositories implémentent les contrats attendus par les services.

### SOLID

- **Single Responsibility** : chaque connecteur sépare client, mapper, modèles, interface et exceptions ; chaque service a une responsabilité claire.
- **Open/Closed** : l'ajout d'un provider peut se faire via un nouveau connecteur et un port/adaptateur sans modifier le domaine.
- **Liskov Substitution** : les protocoles Python permettent de substituer clients réels et fakes/tests.
- **Interface Segregation** : ports petits (`ProductCatalog`, `ProductAnalytics`, `SupplierDirectory`, `ScoreRepository`, etc.).
- **Dependency Inversion** : les services dépendent d'abstractions plutôt que d'implémentations concrètes.

### DRY

Les patterns communs sont répétés de façon structurée mais non dupliquée en logique : chaque provider possède son mapper et ses modèles. Les réponses MCP partagent `ToolResponse`.

### KISS

Les calculs métier sont directs et testables : marge déterministe, scoring explicite, mappers simples. Les transports utilisent la bibliothèque standard `urllib`, évitant une dépendance HTTP additionnelle.

### Dependency Injection

Les services reçoivent leurs dépendances par constructeur : catalogues, analytics, repositories, connecteurs, prompts, tracer. La factory MCP centralise le graphe local actuel.

### Repository Pattern

Les repositories SQLAlchemy (`SqlAlchemyProductRepository`, `SqlAlchemySupplierRepository`, `SqlAlchemyReviewRepository`, `SqlAlchemyScoreRepository`) implémentent les ports de persistance et isolent l'ORM des services.

## 15. Décisions d'architecture (ADR)

### ADR-001 — Clean Architecture comme base

- **Contexte** : le projet doit évoluer sur plusieurs sprints et intégrer plusieurs providers/agents.
- **Décision** : structurer backend en domaine, application, ports, services, infrastructure/adapters.
- **Justification** : réduire le couplage aux frameworks, faciliter les tests et les remplacements de providers.
- **Conséquences** : plus de fichiers et de frontières à maintenir ; chaque nouvelle fonctionnalité doit choisir sa couche.

### ADR-002 — MCP comme frontière d'outillage agentique

- **Contexte** : le projet expose des actions consommables par agents ou clients compatibles MCP.
- **Décision** : créer un serveur `FastMCP` dédié avec tools produit.
- **Justification** : formaliser les capacités agentiques sans imposer une API HTTP métier classique.
- **Conséquences** : le dashboard et n8n nécessitent encore un transport réel si l'on veut les connecter directement aux tools.

### ADR-003 — Connecteurs provider isolés

- **Contexte** : Amazon, Keepa, Bright Data et OpenAI ont des APIs et formats différents.
- **Décision** : un dossier par provider avec protocoles, modèles, mapper, client, exceptions.
- **Justification** : rendre chaque provider remplaçable et testable.
- **Conséquences** : les mappings vers le domaine doivent rester hors logique métier.

### ADR-004 — PostgreSQL + SQLAlchemy + Alembic

- **Contexte** : les opportunités produit nécessitent une persistance relationnelle.
- **Décision** : utiliser PostgreSQL, SQLAlchemy 2 et Alembic.
- **Justification** : stack mature, compatible relations, JSONB et migrations versionnées.
- **Conséquences** : nécessite une gestion de sessions explicite et des migrations à chaque changement de schéma.

### ADR-005 — Dashboard découplé derrière `DashboardMcpClient`

- **Contexte** : l'UI doit avancer sans dépendre de l'intégration MCP réelle.
- **Décision** : définir une interface client dashboard et une implémentation simulée.
- **Justification** : garder l'UI testable et remplaçable.
- **Conséquences** : les données affichées ne sont pas encore les données backend/MCP réelles.

### ADR-006 — Prompts versionnés sur filesystem

- **Contexte** : les fonctions IA nécessitent des instructions maintenables.
- **Décision** : stocker les prompts dans `prompts/*.v1.md` et les charger via `PromptRepository`.
- **Justification** : versionner les prompts hors code Python.
- **Conséquences** : les suppressions/renommages de prompts lèvent `FileNotFoundError`.

### ADR-007 — Workflows n8n exportés mais non opérés par Compose

- **Contexte** : l'automatisation est utile mais l'infrastructure n8n peut varier.
- **Décision** : stocker des exports JSON désactivés, sans conteneur n8n local.
- **Justification** : garder les workflows portables et sans credentials embarqués.
- **Conséquences** : l'exécution nécessite une instance n8n externe/configurée.

## 16. Points d'extension

- **Nouveaux connecteurs** : ajouter un dossier sous `backend/src/fba_advisor/connectors/<provider>/` avec interface, modèles, mapper, client, exceptions.
- **Nouveaux adapters catalogue/analytics** : implémenter `ProductCatalog`, `ProductAnalytics` ou `SupplierDirectory`.
- **Nouveaux tools MCP** : créer un fichier dans `mcp-server/src/fba_mcp_server/tools/`, un schema request/response si nécessaire, enregistrer le tool dans `create_server()`.
- **Nouveaux services métier** : ajouter sous `backend/src/fba_advisor/services/<feature>/service.py` et dépendre de ports.
- **Nouveaux repositories** : implémenter les ports dans `backend/src/fba_advisor/repositories/`.
- **Nouveaux agents IA** : implémenter le port `DecisionAgent` et l'orchestration associée.
- **Dashboard réel** : remplacer `SimulatedDashboardMcpClient` par un client transport MCP/HTTP.
- **API HTTP backend** : ajouter un delivery mechanism sans déplacer la logique métier hors des use cases/services.
- **Scoring configurable** : étendre `services/score/config.yaml` et `ScoreConfig`.
- **Prompts IA** : ajouter `prompts/<nom>.vN.md` et référencer un `PromptSpec`.
- **Workflows n8n** : enrichir les exports et les URLs d'intégration.

## 17. Dette technique

### P0 — Risques ou blocages critiques avant production

- Aucun backend HTTP réel n'est présent alors que Docker/n8n référencent des URLs backend.
- Le serveur MCP n'expose pas de transport HTTP configuré dans Docker Compose ; les workflows n8n supposent des endpoints HTTP.
- Les credentials provider ne sont pas câblés dans une configuration de production ; MCP utilise des connecteurs locaux simulés.
- `POSTGRES_PASSWORD=change_me` est la valeur par défaut et ne doit pas être utilisée hors local.

### P1 — Limitations fonctionnelles importantes

- Dashboard alimenté par données simulées, non par MCP réel.
- Pas de persistance injectée dans la factory MCP actuelle : les recherches tool ne sauvegardent pas les produits.
- `ProductToolUseCases.analyse_product()` repose sur des heuristiques simples et données partielles.
- `ScoreService.calculate()` legacy utilise des poids codés en dur distincts du scoring configurable riche.
- `BrightDataClient` existe mais n'est pas intégré à un service métier ou un tool.
- `OpenAIService` existe mais n'est pas relié aux tools MCP actuels.
- Le port `DecisionAgent` existe sans implémentation concrète.

### P2 — Améliorations futures

- Ajouter gestion de session transactionnelle explicite dans les use cases de persistance.
- Ajouter retry, timeout configurable, rate limiting et observabilité structurée pour connecteurs externes.
- Formaliser les DTOs applicatifs pour réduire les mappings par dictionnaires.
- Unifier scoring legacy et scoring configurable.
- Ajouter documentation OpenAPI si une API HTTP backend est introduite.
- Ajouter secrets management pour credentials providers.
- Ajouter tests end-to-end dashboard ↔ MCP ↔ backend.
- Clarifier les conventions de versioning des prompts et configs.

## 18. Sécurité

### Secrets

- Les secrets ne doivent jamais être commités.
- `.env.example` contient seulement des valeurs locales et placeholders.
- Les credentials provider sont modélisés dans le code mais doivent être fournis par environnement sécurisé ou secret manager quand ils seront câblés.
- Les workflows n8n ne contiennent pas de secret ; ils attendent des variables d'environnement.

### Variables d'environnement

- `DATABASE_URL` contient potentiellement des credentials et doit être protégée.
- `POSTGRES_PASSWORD` doit être changé en production.
- Les variables n8n de webhooks et endpoints doivent être traitées comme sensibles si elles donnent accès à des actions internes.

### Authentification

- Connecteurs : Amazon, Bright Data, Keepa et OpenAI gèrent chacun leur authentification provider.
- Application : aucune authentification utilisateur/dashboard/backend n'est implémentée dans le code actuel.
- MCP : aucune politique d'autorisation fine par tool n'est implémentée dans le code actuel.

### Accès base de données

- PostgreSQL local expose le port `5432:5432` dans Docker Compose.
- Les repositories utilisent des sessions SQLAlchemy injectées.
- Les contraintes uniques protègent contre les doublons provider `(source, identifier)` pour produits et fournisseurs.

## 19. Conventions

### Nommage

- Packages Python en snake_case : `fba_advisor`, `fba_mcp_server`.
- Services métier suffixés `Service`.
- Ports Python exprimés en `Protocol`.
- Connecteurs suffixés `Client` et exposant `provider_name`.
- Models provider en Pydantic, models domaine en dataclasses.
- Tables SQL en pluriel anglais : `products`, `suppliers`, etc.
- Frontend composants React en PascalCase, hooks `use...`.

### Structure

- Une feature backend majeure possède idéalement : domaine/port/service/adapter/tests.
- Un provider externe possède : `client.py`, `interfaces.py`, `models.py`, `mapper.py`, `exceptions.py`.
- Un tool MCP possède : schema request si nécessaire, fonction tool, adaptation vers service.
- Les prompts sont versionnés sous `prompts/<name>.v<version>.md`.

### Organisation des modules

- Ne pas importer SQLAlchemy dans les services métier.
- Ne pas importer les clients provider dans le domaine.
- Ne pas importer le dashboard dans backend/MCP.
- Ne pas placer la logique métier dans les tools MCP ; les tools valident, loggent et délèguent.
- Les repositories SQLAlchemy convertissent entre entités ORM et modèles domaine.

## 20. Roadmap

### V1 — Stabilisation de la base actuelle

- Valider et maintenir la Clean Architecture existante.
- Garder tous les tests backend/MCP/frontend verts.
- Finaliser la documentation officielle d'architecture.
- Clarifier les environnements local, test et production.

### V2 — Intégration réelle MCP/backend/providers

- Câbler les credentials providers via configuration sécurisée.
- Remplacer les connecteurs locaux MCP par des clients réels configurables avec fallback local explicite.
- Ajouter transport HTTP ou mécanisme d'exposition compatible avec n8n.
- Injecter repositories SQLAlchemy dans les use cases nécessitant persistance.

### V3 — Produit et intelligence métier

- Brancher `OpenAIService` aux analyses avancées.
- Intégrer Bright Data aux flux de recherche concurrentielle/fournisseurs.
- Unifier le scoring configurable et le scoring tool.
- Ajouter review human-in-the-loop complète et audit trail.

### V4 — Plateforme agentique opérationnelle

- Implémenter des agents IA derrière `DecisionAgent`.
- Ajouter orchestration multi-agent et workflows robustes.
- Connecter le dashboard aux données réelles.
- Ajouter sécurité applicative complète, observabilité, rate limiting, retries et monitoring.

## Règles pour les futurs développements

- Respecter la Clean Architecture.
- Respecter SOLID.
- Éviter le couplage fort.
- Privilégier les interfaces et protocoles.
- Ne jamais casser l'API publique.
- Ne jamais modifier un module sans analyser ses dépendances.
- Ajouter des tests pour toute nouvelle fonctionnalité.
- Documenter tout nouveau module.
- Éviter la duplication.
- Conserver une architecture modulaire.
- Ne pas mettre de logique métier dans les connecteurs, les mappers, les pages UI ou les tools MCP.
- Toute nouvelle dépendance externe doit être justifiée par un besoin architectural clair.
- Toute évolution de base de données doit passer par une migration Alembic.
- Toute nouvelle variable d'environnement doit être documentée dans `.env.example` et dans cette documentation.
- Tout nouveau provider doit être introduit derrière un port ou une interface.
