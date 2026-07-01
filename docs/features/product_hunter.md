# Product Hunter — Spécification fonctionnelle et technique

> Statut : documentation de fonctionnalité basée uniquement sur le code présent au 2026-07-01.  
> Périmètre : recherche de produits Amazon FBA, analyse synthétique, calcul de marge et scoring exposés par les tools MCP existants.  
> Fichier source de référence : `docs/features/product_hunter.md`.

## 1. Présentation

### But de la fonctionnalité

Product Hunter est la fonctionnalité de découverte et de première qualification d'opportunités produit Amazon FBA. Elle regroupe les capacités réellement implémentées suivantes :

- rechercher des candidats produits à partir d'une requête textuelle ;
- enrichir ces candidats avec des signaux analytiques ;
- analyser un ASIN de façon synthétique ;
- calculer une marge FBA à partir d'entrées financières explicites ;
- calculer un score d'opportunité simple pour orienter la décision humaine.

La fonctionnalité est exposée aujourd'hui par le serveur MCP `fba_mcp_server` via quatre tools : `search_products`, `analyse_product`, `calculate_margin` et `score_product`.

### Objectifs métier

- Identifier rapidement des pistes de produits FBA à investiguer.
- Normaliser les données fournisseur/catalogue dans des modèles métier indépendants des fournisseurs.
- Fournir une première lecture de demande, concurrence, risque, marge et attractivité.
- Permettre à un agent, un opérateur humain ou un orchestrateur d'enchaîner recherche, analyse, marge et scoring.
- Préserver la testabilité et la remplaçabilité des fournisseurs via ports, services et adaptateurs.

### Utilisateurs concernés

- **Opérateur FBA / décideur métier** : consulte les candidats, marges et recommandations.
- **Agent IA ou orchestrateur MCP** : appelle les tools MCP pour automatiser la recherche.
- **Développeur backend** : maintient les services métier, ports, connecteurs et repositories.
- **Développeur MCP** : maintient les schemas Pydantic, tools et adaptateurs MCP.
- **Développeur data/persistance** : maintient les entités SQLAlchemy et migrations liées aux produits et scores.

### Limites actuelles

- Les tools MCP utilisent actuellement `LocalAmazonConnector` et `LocalKeepaConnector`, donc les résultats Product Hunter sont simulés au niveau du graphe MCP par défaut.
- Le backend est un package Python importable ; aucune API HTTP backend publique n'est implémentée.
- Le dashboard Next.js consomme un client MCP simulé et n'appelle pas encore le serveur MCP réel.
- La recherche fournisseur, Bright Data et OpenAI existent dans le codebase comme connecteurs/services séparés, mais ne sont pas branchés dans le graphe Product Hunter MCP actuel.
- La persistance produit et score existe via ports et repositories SQLAlchemy, mais le graphe MCP actuel ne lui injecte pas de repository.
- Le tool `analyse_product` produit une analyse heuristique limitée à partir d'une recherche par ASIN, sans vraie analyse IA.
- Le tool `score_product` utilise le calcul de score legacy simple, pas le moteur configurable riche `ScoreService.score`.

## 2. Cas d'utilisation

### UC-01 — Rechercher des produits candidats

- **Description** : un utilisateur ou agent recherche des produits correspondant à une requête.
- **Entrée** : `query`, `marketplace`, `limit`.
- **Sortie** : enveloppe `ToolResponse` contenant une liste de produits normalisés.
- **Résultat attendu** : les produits sont recherchés via le catalogue Amazon local, enrichis par Keepa local, tronqués à `limit`, puis retournés dans un format JSON compatible MCP.

### UC-02 — Rejeter une recherche vide ou invalide

- **Description** : une recherche dont la requête ne respecte pas le schema MCP doit être refusée proprement.
- **Entrée** : `query` trop court, trop long ou invalide ; `limit` non positif ou supérieur à 20 ; `marketplace` inconnu.
- **Sortie** : dictionnaire d'erreur contrôlé avec `error = validation_error` et détails Pydantic.
- **Résultat attendu** : aucune règle métier n'est exécutée ; le serveur MCP retourne une erreur structurée.

### UC-03 — Analyser un ASIN

- **Description** : un agent demande une synthèse de demande, concurrence, risque, opportunités et avertissements pour un ASIN.
- **Entrée** : `asin` de 10 caractères et `marketplace`.
- **Sortie** : objet contenant `asin`, `demand_level`, `competition_level`, `risk_level`, `opportunities`, `warnings`.
- **Résultat attendu** : le use case recherche le produit, sélectionne le candidat portant l'identifiant demandé ou le premier résultat, puis calcule des niveaux synthétiques.

### UC-04 — Calculer une marge FBA

- **Description** : un utilisateur fournit prix de vente, coût rendu, frais Amazon et coût fulfillment.
- **Entrée** : `sale_price`, `landed_cost`, `amazon_fees`, `fulfillment_cost`.
- **Sortie** : prix, coûts, profit net et pourcentage de marge.
- **Résultat attendu** : le service de marge valide les montants, calcule les coûts totaux et retourne profit et marge arrondis au centime.

### UC-05 — Scorer une opportunité produit

- **Description** : un agent calcule un score à partir de ventes mensuelles estimées, volume d'avis et marge.
- **Entrée** : `asin`, `monthly_sales_estimate`, `review_count`, `margin_percent`.
- **Sortie** : `asin`, `score`, `recommendation`, `rationale`.
- **Résultat attendu** : le score est calculé sur 100 ; une opportunité à 60 ou plus reçoit la recommandation `investigate`, sinon `watchlist`.

### UC-06 — Enrichir les produits via analytics

- **Description** : chaque produit retourné par le catalogue peut être enrichi par un port analytics.
- **Entrée** : produit domaine issu du catalogue.
- **Sortie** : produit domaine enrichi, notamment `sales_rank` et attributs `keepa` si les données existent.
- **Résultat attendu** : l'enrichissement ne casse pas la recherche si aucun item analytics correspondant n'est trouvé.

### UC-07 — Persister des produits ou scores lorsque des repositories sont injectés

- **Description** : le service produit et le service score peuvent persister leurs résultats si des repositories sont fournis.
- **Entrée** : `ProductRepository` pour les produits ; `ScoreRepository` et `product_identifier` pour les scores.
- **Sortie** : entités domaine inchangées après sauvegarde.
- **Résultat attendu** : le service reste indépendant de SQLAlchemy ; la persistance est optionnelle et injectée.

## 3. Architecture

### Modules impliqués

- `mcp-server/src/fba_mcp_server/server.py` : création du serveur `FastMCP`, enregistrement des tools et wrapper d'erreurs.
- `mcp-server/src/fba_mcp_server/tools/` : adaptateurs protocolaires MCP pour recherche, analyse, marge et score.
- `mcp-server/src/fba_mcp_server/schemas/` : schemas Pydantic d'entrées et enveloppe de réponse.
- `mcp-server/src/fba_mcp_server/services/product_research.py` : adaptation entre schemas MCP et use cases backend.
- `backend/src/fba_advisor/application/product_tools.py` : façade applicative Product Hunter.
- `backend/src/fba_advisor/services/product/service.py` : recherche produit via ports injectés.
- `backend/src/fba_advisor/services/margin/service.py` : calcul financier déterministe.
- `backend/src/fba_advisor/services/score/service.py` : scoring legacy et scoring configurable riche.
- `backend/src/fba_advisor/repositories/connectors.py` : adaptateurs Amazon/Keepa vers modèles domaine.
- `backend/src/fba_advisor/domain/models.py` : modèles domaine `Product`, `MarginInput`, `MarginEstimate`, `ProductScoreInput`, `ProductScore`.
- `backend/src/fba_advisor/repositories/sqlalchemy.py` et `backend/src/fba_advisor/models/entities.py` : persistance optionnelle.

### Services

- `ProductToolUseCases` : orchestre les cas d'utilisation Product Hunter.
- `ProductResearchService` : recherche et enrichissement de produits.
- `MarginService` : calcul de marge.
- `ScoreService` : calcul de score.
- `BackendProductResearchService` : pont MCP vers backend.
- `LoggingTracer` : tracing applicatif optionnel.

### Outils MCP

- `search_products`
- `analyse_product`
- `calculate_margin`
- `score_product`

### Connecteurs

- `LocalAmazonConnector` : connecteur local par défaut dans le graphe MCP.
- `LocalKeepaConnector` : connecteur local analytics par défaut dans le graphe MCP.
- `AmazonProductCatalog` : adaptateur catalogue normalisé.
- `KeepaProductAnalytics` : adaptateur analytics normalisé.
- Connecteurs réels Amazon et Keepa : présents dans le backend mais non injectés par défaut dans Product Hunter MCP.

### Base de données

La base cible est PostgreSQL via SQLAlchemy et Alembic. Les entités pertinentes pour Product Hunter sont :

- `products` ;
- `scores` ;
- `reviews` ;
- `categories` ;
- indirectement `suppliers`, `quotes`, `emails` pour les étapes sourcing futures.

### Dépendances

- Python 3.13.
- Pydantic et `pydantic-settings` pour validation/configuration MCP.
- FastMCP pour l'exposition MCP.
- SQLAlchemy et Alembic pour la persistance optionnelle.
- PostgreSQL comme base cible.
- Bibliothèque standard `urllib` dans les connecteurs HTTP réels.

### Diagramme Mermaid

```mermaid
flowchart TB
    Actor[Utilisateur ou agent IA] --> MCP[Serveur FastMCP]
    MCP --> SafeTool[_safe_tool]
    SafeTool --> SearchTool[search_products]
    SafeTool --> AnalyseTool[analyse_product]
    SafeTool --> MarginTool[calculate_margin]
    SafeTool --> ScoreTool[score_product]

    SearchTool --> Schemas[Schemas Pydantic MCP]
    AnalyseTool --> Schemas
    MarginTool --> Schemas
    ScoreTool --> Schemas

    Schemas --> MCPService[BackendProductResearchService]
    MCPService --> UseCases[ProductToolUseCases]

    UseCases --> ProductService[ProductResearchService]
    UseCases --> MarginService[MarginService]
    UseCases --> ScoreService[ScoreService]
    UseCases --> Tracer[LoggingTracer]

    ProductService --> CatalogPort[ProductCatalog]
    ProductService --> AnalyticsPort[ProductAnalytics]
    ProductService -. optionnel .-> ProductRepo[ProductRepository]

    CatalogPort --> AmazonAdapter[AmazonProductCatalog]
    AnalyticsPort --> KeepaAdapter[KeepaProductAnalytics]
    AmazonAdapter --> LocalAmazon[LocalAmazonConnector]
    KeepaAdapter --> LocalKeepa[LocalKeepaConnector]

    ScoreService -. optionnel .-> ScoreRepo[ScoreRepository]
    ProductRepo -. SQLAlchemy .-> DB[(PostgreSQL)]
    ScoreRepo -. SQLAlchemy .-> DB
```

## 4. Flux d'exécution

### Flux complet

1. L'utilisateur, un agent ou un orchestrateur appelle un tool MCP.
2. Le serveur FastMCP exécute le wrapper `_safe_tool`.
3. Le tool construit un schema Pydantic de requête.
4. Si la validation échoue, `_safe_tool` retourne `validation_error`.
5. Si la validation réussit, le tool récupère le service via `get_product_research_service`.
6. `get_product_research_service` construit le graphe local : Amazon local, Keepa local, service produit, service marge, service score, tracer.
7. `BackendProductResearchService` convertit les schemas MCP vers la façade applicative backend.
8. `ProductToolUseCases` ouvre un span de tracing si disponible.
9. Le service métier correspondant exécute la règle : recherche, analyse, marge ou scoring.
10. Le résultat est converti en dictionnaire ou schema de sortie.
11. Le tool enveloppe le résultat dans `ToolResponse` et retourne un JSON compatible MCP.
12. En cas d'exception non prévue, `_safe_tool` journalise et retourne `tool_execution_error`.

### Diagramme Mermaid

```mermaid
sequenceDiagram
    participant A as Agent ou utilisateur
    participant M as FastMCP
    participant T as Tool MCP
    participant V as Schema Pydantic
    participant S as BackendProductResearchService
    participant U as ProductToolUseCases
    participant B as Service métier
    participant C as Ports/Connecteurs

    A->>M: Appel tool
    M->>T: Exécution via _safe_tool
    T->>V: Construction requête validée
    alt Entrée invalide
        V-->>M: ValidationError
        M-->>A: {error: validation_error, details}
    else Entrée valide
        T->>S: Appel méthode adaptée
        S->>U: Délégation use case
        U->>B: Appel service métier
        opt Recherche produit
            B->>C: ProductCatalog.search
            C-->>B: Produits domaine
            B->>C: ProductAnalytics.enrich
            C-->>B: Produits enrichis
        end
        B-->>U: Résultat métier
        U-->>S: Résultat normalisé
        S-->>T: Données tool
        T-->>M: ToolResponse JSON
        M-->>A: Réponse MCP
    end
```

## 5. Outils MCP utilisés

### `search_products`

- **Rôle** : rechercher des produits candidats.
- **Paramètres** :
  - `query` : chaîne de 2 à 120 caractères ;
  - `marketplace` : valeur de marketplace, défaut `amazon_us` ;
  - `limit` : entier positif, défaut 5, maximum 20.
- **Retour** : `ToolResponse` contenant une liste de produits normalisés.
- **Dépendances** : `SearchProductsRequest`, `Marketplace`, `BackendProductResearchService`, `ProductToolUseCases`, `ProductResearchService`, `AmazonProductCatalog`, `KeepaProductAnalytics`.

### `analyse_product`

- **Rôle** : fournir une synthèse qualitative d'un ASIN.
- **Paramètres** :
  - `asin` : chaîne de 10 caractères ;
  - `marketplace` : valeur de marketplace, défaut `amazon_us`.
- **Retour** : demande, concurrence, risque, opportunités et avertissements.
- **Dépendances** : `AnalyseProductRequest`, recherche produit backend, heuristiques de `ProductToolUseCases.analyse_product`.

### `calculate_margin`

- **Rôle** : calculer profit net et marge FBA.
- **Paramètres** :
  - `sale_price` : Decimal strictement positif ;
  - `landed_cost` : Decimal positif ou nul ;
  - `amazon_fees` : Decimal positif ou nul ;
  - `fulfillment_cost` : Decimal positif ou nul.
- **Retour** : prix, coûts, `net_profit`, `margin_percent`.
- **Dépendances** : `CalculateMarginRequest`, `MarginInput`, `MarginService`.

### `score_product`

- **Rôle** : produire un score d'opportunité simple et une recommandation.
- **Paramètres** :
  - `asin` : chaîne de 10 caractères ;
  - `monthly_sales_estimate` : entier positif ou nul ;
  - `review_count` : entier positif ou nul ;
  - `margin_percent` : Decimal à deux décimales.
- **Retour** : `asin`, `score`, `recommendation`, `rationale`.
- **Dépendances** : `ScoreProductRequest`, `ProductScoreInput`, `ScoreService.calculate`.

## 6. Services impliqués

### `ProductToolUseCases`

- **Responsabilités** : façade applicative pour recherche, analyse, marge et score.
- **Dépendances** : `ProductResearchService`, `MarginService`, `ScoreService`, `Tracer` optionnel.
- **Notes** : cette classe évite de placer la logique métier dans les tools MCP.

### `ProductResearchService`

- **Responsabilités** : normaliser la requête, appeler le catalogue, enrichir via analytics et persister optionnellement.
- **Dépendances** : `ProductCatalog`, `ProductAnalytics` optionnel, `ProductRepository` optionnel.
- **Comportement notable** : une requête vide après trim retourne une liste vide.

### `MarginService`

- **Responsabilités** : valider les montants et calculer revenu, coûts, profit, marge et frais de referral.
- **Dépendances** : aucune dépendance externe.
- **Comportement notable** : refuse prix de vente nul/négatif, coûts négatifs et taux de referral hors `[0, 1]`.

### `ScoreService`

- **Responsabilités** : calculer un score legacy simple via `calculate` et un score configurable détaillé via `score`.
- **Dépendances** : `ScoreRepository` optionnel, `ScoreConfig`, `ScoreWeights`.
- **Comportement notable** : `score_product` MCP utilise actuellement `calculate`, pas `score`.

### `BackendProductResearchService`

- **Responsabilités** : convertir les requêtes MCP validées vers appels backend et formater les réponses.
- **Dépendances** : `ProductToolUseCases`.

### `LoggingTracer`

- **Responsabilités** : journaliser début, succès et échec de spans applicatifs.
- **Dépendances** : logging Python.

## 7. Connecteurs

### `LocalAmazonConnector`

- **Utilisation** : connecteur par défaut du graphe MCP.
- **Pourquoi** : fournir des données déterministes sans credentials externes.
- **Retour** : `AmazonSearchResponse` contenant deux `AmazonProduct` simulés.

### `LocalKeepaConnector`

- **Utilisation** : connecteur analytics par défaut du graphe MCP.
- **Pourquoi** : enrichir les produits sans appel réseau Keepa.
- **Retour** : `KeepaResponse` contenant un `KeepaProduct` avec `sales_rank = 900`.

### `AmazonProductCatalog`

- **Utilisation** : adaptateur entre un `AmazonConnector` et le port `ProductCatalog`.
- **Pourquoi** : convertir les modèles connecteur Amazon en `Product` domaine.

### `KeepaProductAnalytics`

- **Utilisation** : adaptateur entre un `KeepaConnector` et le port `ProductAnalytics`.
- **Pourquoi** : enrichir un `Product` domaine avec rang de vente et attributs analytics.

### Connecteurs réels Amazon et Keepa

- **Utilisation actuelle dans Product Hunter MCP** : non injectés par défaut.
- **Pourquoi ils existent** : préparer l'intégration fournisseur réelle derrière les mêmes interfaces.
- **Condition d'utilisation future** : remplacer les connecteurs locaux dans la composition des dépendances sans modifier les services métier.

## 8. Modèle de données

### Entités domaine

- `Product` : candidat produit normalisé avec identifiant, titre, source, prix, devise, rang de vente et attributs.
- `MarginInput` : entrées financières nécessaires à une estimation de marge.
- `MarginEstimate` : résultat financier avec revenu, coût total, profit, taux de marge et frais referral.
- `ProductScoreInput` : entrées normalisées pour scoring legacy.
- `ProductScore` : score calculé, rationale, sous-scores optionnels et explication.

### Entités persistées

- `Product` SQLAlchemy : persiste les candidats produit.
- `Score` : persiste les scores et leurs inputs.
- `Review` : persiste les décisions humaines.
- `Category` : structure les catégories produit.
- `Supplier`, `Quote`, `Email` : utiles aux flux sourcing futurs et à la continuité après Product Hunter.

### Relations

- Une catégorie peut avoir plusieurs produits.
- Un produit peut avoir un fournisseur, plusieurs reviews, plusieurs scores, plusieurs quotes et plusieurs emails.
- Un fournisseur peut avoir plusieurs produits, quotes et emails.

### Diagramme Mermaid

```mermaid
erDiagram
    CATEGORY ||--o{ CATEGORY : parent
    CATEGORY ||--o{ PRODUCT : classifies
    SUPPLIER ||--o{ PRODUCT : supplies
    PRODUCT ||--o{ REVIEW : has
    PRODUCT ||--o{ SCORE : has
    PRODUCT ||--o{ QUOTE : has
    SUPPLIER ||--o{ QUOTE : provides
    PRODUCT ||--o{ EMAIL : concerns
    SUPPLIER ||--o{ EMAIL : receives_or_sends

    PRODUCT {
        int id
        string identifier
        string title
        string source
        decimal price
        string currency
        int sales_rank
        json attributes
    }

    SCORE {
        int id
        string product_identifier
        decimal value
        text rationale
        json inputs
    }

    REVIEW {
        int id
        string product_identifier
        string decision
        string reviewer
        text notes
        datetime reviewed_at
    }

    SUPPLIER {
        int id
        string identifier
        string name
        string source
        int minimum_order_quantity
        decimal unit_cost
        decimal reliability_score
        json attributes
    }
```

## 9. Algorithme

### Recherche produit

Pseudo-code :

```text
recevoir query et limit validés
ouvrir span product.search
normaliser query par trim
si query est vide : retourner []
appeler ProductCatalog.search(query)
si ProductAnalytics existe :
    pour chaque produit : enrichir produit
si ProductRepository existe :
    pour chaque produit : sauvegarder produit
tronquer la liste à limit
journaliser product.search.completed avec count
retourner les produits
```

### Analyse produit

Pseudo-code :

```text
recevoir asin et marketplace validés
ouvrir span product.analyse
rechercher des produits avec query = asin
sélectionner le produit dont identifier == asin
sinon, si une liste existe, sélectionner le premier produit
rank = product.sales_rank si produit disponible
si rank existe et rank <= 1000 : demand_level = high
sinon : demand_level = medium
si product existe et review_count > 500 : competition_level = high
sinon : competition_level = medium
si product existe et product.price existe : risk_level = controlled
sinon : risk_level = needs_data
retourner synthèse opportunités et avertissements statiques
```

### Calcul de marge

Pseudo-code :

```text
recevoir sale_price, landed_cost, amazon_fees, fulfillment_cost validés
ouvrir span product.margin
construire MarginInput :
    selling_price = sale_price
    product_cost = landed_cost
    fulfillment_fee = fulfillment_cost
    referral_fee_rate = amazon_fees / sale_price
valider :
    selling_price > 0
    coûts >= 0
    0 <= referral_fee_rate <= 1
referral_fee = selling_price * referral_fee_rate
total_cost = product_cost + fulfillment_fee + referral_fee + shipping_cost + fixed_costs
profit = selling_price - total_cost
margin_rate = profit / selling_price
retourner net_profit et margin_percent arrondis à 0,01
```

### Scoring legacy MCP

Pseudo-code :

```text
recevoir asin, monthly_sales_estimate, review_count, margin_percent validés
ouvrir span product.score
demand_score = min(monthly_sales_estimate / 1000, 1)
competition_score = min(review_count / 1000, 1)
margin_rate = min(margin_percent / 100, 1)
supplier_reliability = 0.5
review_sentiment = 0.5
normaliser chaque valeur entre 0 et 1
competition = 1 - competition_score
weighted = (
    demand * 0.30
    + competition * 0.20
    + margin * 0.30
    + supplier * 0.15
    + sentiment * 0.05
) / somme_des_poids
score = round(weighted * 100, 2)
rationale = Strong si score >= 75, Moderate si score >= 50, sinon Weak
recommendation = investigate si score >= 60, sinon watchlist
retourner score arrondi, recommendation et rationale
```

## 10. Configuration

### Variables d'environnement backend

- `APP_ENV` : environnement applicatif, défaut `local`.
- `LOG_LEVEL` : niveau de log, défaut `INFO`.
- `DATABASE_URL` : URL PostgreSQL, défaut `postgresql://agentic_ecommerce:change_me@postgres:5432/agentic_ecommerce`.

### Variables d'environnement MCP

- `APP_ENV` : environnement applicatif, défaut `local`.
- `LOG_LEVEL` : niveau de log, défaut `INFO`.
- `BACKEND_BASE_URL` : URL backend configurée, défaut `http://backend:8000`; actuellement non utilisée par le graphe Product Hunter local.
- `MCP_SERVER_NAME` : nom serveur MCP, défaut `agentic-ecommerce-mcp`.

### Paramètres de tools

- `SearchProductsRequest.limit` : maximum 20.
- `SearchProductsRequest.query` : longueur 2 à 120.
- `AnalyseProductRequest.asin` et `ScoreProductRequest.asin` : longueur 10.
- Montants `CalculateMarginRequest` : décimaux avec deux décimales, maximum 10 chiffres.

### Pondérations

Le tool `score_product` utilise les pondérations legacy codées dans `ScoreService.calculate` :

- demande : 0,30 ;
- concurrence inversée : 0,20 ;
- marge : 0,30 ;
- fiabilité fournisseur : 0,15 ;
- sentiment reviews : 0,05.

Le moteur riche `ScoreService.score` peut charger `backend/src/fba_advisor/services/score/config.yaml` avec :

- concurrence : 0,20 ;
- marge : 0,25 ;
- brandabilité : 0,15 ;
- différenciation : 0,15 ;
- tendance : 0,15 ;
- saisonnalité : 0,10 ;
- références de normalisation : marge cible 0,30, offres concurrentes 50, avis 1000, sales rank 100000, croissance 0,30, volatilité saisonnière 0,50.

### Fichiers de configuration

- `.env.example` : exemples de variables.
- `backend/src/fba_advisor/config.py` : configuration backend.
- `mcp-server/src/fba_mcp_server/config.py` : configuration MCP.
- `backend/src/fba_advisor/services/score/config.yaml` : configuration du scoring riche.
- `docker-compose.yml` : services d'exécution dont PostgreSQL.

## 11. Gestion des erreurs

| Erreur possible | Comportement attendu | Stratégie de reprise |
| --- | --- | --- |
| Entrée MCP invalide | `_safe_tool` retourne `validation_error` avec détails Pydantic | Corriger les paramètres appelants |
| Exception tool non prévue | `_safe_tool` journalise et retourne `tool_execution_error` | Examiner logs, reproduire avec tests |
| Requête produit vide après trim | `ProductResearchService.search` retourne `[]` | Demander une requête exploitable |
| Prix de vente <= 0 | `MarginService` lève `ValueError` | Corriger `sale_price` |
| Coûts négatifs | `MarginService` lève `ValueError` | Corriger les coûts |
| Taux referral hors `[0, 1]` | `MarginService` lève `ValueError` | Vérifier `amazon_fees / sale_price` |
| Aucun enrichissement Keepa trouvé | Retour du produit original | Continuer avec signaux partiels |
| Somme des pondérations riches <= 0 | `ScoreService.score` lève `ValueError` | Corriger `ScoreWeights` ou YAML |
| Erreur connecteur réel future | Exception fournisseur locale au connecteur | Mapper l'erreur au niveau adaptateur/protocole |
| Échec persistance optionnelle | Exception SQLAlchemy attendue hors services purs | Rollback session par l'appelant |

## 12. Logging

### À journaliser

- Appels de tools avec paramètres non sensibles : query, marketplace, ASIN.
- Début, succès et échec des spans applicatifs via `LoggingTracer`.
- Nombre de produits retournés par `product.search.completed`.
- Erreurs de validation MCP en niveau warning.
- Exceptions tool non prévues en niveau exception/error.

### Niveaux de logs

- `INFO` : démarrage serveur, appels tools, succès de recherche.
- `WARNING` : validation d'entrée échouée.
- `ERROR` / exception : échec d'exécution de tool ou span applicatif.
- `DEBUG` : non utilisé actuellement pour Product Hunter ; pourrait être ajouté pour diagnostics locaux sans données sensibles.

### Événements importants

- `MCP server configured`.
- `Searching products`.
- `Analysing product`.
- `Calculating margin`.
- `Scoring product`.
- `product.search.completed`.
- `Tool validation failed`.
- `Tool execution failed`.

## 13. Tests

### Tests unitaires

- Validation des services métier : recherche, marge, score, review.
- Validation des connecteurs et mappers sans requêtes réseau réelles.
- Validation des settings backend et MCP.
- Validation de la configuration scoring YAML.

### Tests d'intégration

- Tests repositories SQLAlchemy sur sauvegarde produit, fournisseur, review et score.
- Tests tools MCP avec construction de réponses et gestion de validation.
- Tests potentiels futurs : composition avec vrais connecteurs derrière interfaces.

### Cas limites

- Requête vide ou composée d'espaces.
- Limite à 1 et à 20 produits.
- ASIN longueur différente de 10.
- Ventes mensuelles à 0 ou très élevées.
- Nombre d'avis à 0 ou très élevé.
- Marge négative possible après coûts.
- Frais Amazon supérieurs au prix de vente.
- Produit sans prix pour `analyse_product`.
- Keepa sans item correspondant.
- Repository absent ou présent.

### Données de test

- Produits locaux `B0TEST0001` et `B0TEST0002` produits par `LocalAmazonConnector`.
- `sales_rank = 900` produit par `LocalKeepaConnector` quand l'ASIN correspond.
- Montants synthétiques pour `MarginInput`.
- Entrées `ProductScoreInput` avec combinaisons faible, moyenne et forte.

### Checklist

- [ ] `search_products` retourne une enveloppe `ToolResponse` valide.
- [ ] `search_products` respecte `limit`.
- [ ] `search_products` refuse une requête invalide.
- [ ] `analyse_product` refuse un ASIN invalide.
- [ ] `analyse_product` retourne `controlled` si un prix existe.
- [ ] `calculate_margin` calcule correctement profit et marge.
- [ ] `calculate_margin` refuse les montants invalides.
- [ ] `score_product` retourne `investigate` à partir de 60.
- [ ] `score_product` retourne `watchlist` sous 60.
- [ ] Les repositories SQLAlchemy sauvegardent les produits et scores si injectés.
- [ ] Les erreurs sont converties en dictionnaires contrôlés au niveau MCP.

## 14. Performance

### Points sensibles

- Appels fournisseurs externes futurs Amazon et Keepa.
- Enrichissement produit unitaire : un appel analytics par produit dans l'implémentation actuelle.
- Construction du graphe de dépendances à chaque appel tool via `get_product_research_service`.
- Persistance optionnelle produit par produit si un repository est injecté.
- Parsing et mapping des payloads externes réels.

### Optimisations possibles

- Réutiliser un graphe de dépendances configuré au démarrage du serveur MCP.
- Ajouter du batching analytics si le connecteur Keepa réel le permet.
- Mettre en cache les résultats d'enrichissement par ASIN avec TTL court.
- Ajouter pagination/streaming si les résultats dépassent les limites actuelles.
- Mesurer latence par span avant toute optimisation structurante.

### Cache éventuel

Aucun cache Product Hunter n'est actuellement implémenté. Un cache futur devrait :

- être explicite et invalidable ;
- éviter les secrets et payloads fournisseur sensibles ;
- utiliser une clé incluant source, marketplace, requête ou ASIN ;
- respecter la fraîcheur nécessaire aux décisions FBA.

## 15. Sécurité

### Validations

- Les entrées tools sont validées par Pydantic.
- Les calculs financiers valident prix, coûts et taux.
- Les connecteurs réels doivent convertir les payloads externes vers modèles typés avant exposition aux services.

### Secrets

- Aucun secret réel ne doit être committé.
- Les credentials fournisseurs doivent passer par variables d'environnement.
- Les logs ne doivent pas inclure tokens, headers d'autorisation ou payloads sensibles complets.

### Permissions

- Product Hunter MCP n'implémente pas d'authentification applicative dans le code actuel.
- La sécurité d'accès au serveur MCP doit être gérée par l'environnement d'exécution tant qu'une couche applicative dédiée n'existe pas.
- La base PostgreSQL doit être protégée par credentials d'environnement et réseau privé.

### Données sensibles

- Les ASIN et requêtes ne sont pas des secrets mais peuvent révéler une stratégie produit ; les journaux doivent rester contrôlés.
- Les coûts, marges, scores et notes de review sont sensibles métier.
- Les futures réponses fournisseurs doivent être filtrées avant logging.

## 16. Dépendances

### Dépendances internes

- Domaine : `fba_advisor.domain.models`.
- Ports : `fba_advisor.ports.catalog`, `fba_advisor.ports.repositories`, `fba_advisor.ports.tracing`.
- Services : `ProductResearchService`, `MarginService`, `ScoreService`.
- Application : `ProductToolUseCases`.
- Adaptateurs : `AmazonProductCatalog`, `KeepaProductAnalytics`.
- MCP : tools, schemas, services et serveur `fba_mcp_server`.
- Persistance optionnelle : repositories SQLAlchemy, entités et migrations.

### Dépendances externes

- FastMCP / SDK MCP.
- Pydantic et `pydantic-settings`.
- SQLAlchemy.
- Alembic.
- PostgreSQL.
- Fournisseurs externes préparés : Amazon, Keepa, Bright Data, OpenAI.
- Docker pour l'exécution conteneurisée.

## 17. Roadmap

### Version actuelle

- Tools MCP `search_products`, `analyse_product`, `calculate_margin`, `score_product`.
- Connecteurs locaux simulés Amazon et Keepa dans la composition MCP.
- Services métier purs pour recherche, marge et scoring.
- Persistance optionnelle disponible mais non branchée dans le graphe MCP par défaut.
- Dashboard découplé avec client MCP simulé.

### V2

- Brancher les connecteurs réels Amazon et Keepa via configuration et injection.
- Injecter les repositories SQLAlchemy dans le graphe Product Hunter lorsque `DATABASE_URL` est disponible.
- Utiliser le moteur riche `ScoreService.score` pour produire sous-scores et explications.
- Ajouter un transport réel dashboard → MCP ou une API HTTP adaptatrice.
- Ajouter métriques de latence et taux d'erreur par tool.

### V3

- Ajouter recherche fournisseur dans le flux Product Hunter après validation produit.
- Intégrer Bright Data pour sourcing/veille concurrentielle si les ports métier sont définis.
- Intégrer OpenAI pour analyse de review, différenciation, brandabilité et synthèse.
- Ajouter orchestration multi-étapes : recherche, scoring, sourcing, review humaine.
- Ajouter historique consultable depuis le dashboard sur données persistées.

### Améliorations futures

- Batch enrichment Keepa.
- Cache contrôlé par TTL.
- Configuration de pondérations par marketplace ou catégorie.
- Gestion d'authentification/autorisation MCP.
- Observabilité structurée avec corrélation de requêtes.

## 18. Dette technique

### P0

- Aucune authentification applicative Product Hunter n'est implémentée côté MCP ; à traiter avant exposition hors environnement privé.
- Les connecteurs locaux peuvent donner une fausse impression de données réelles si l'interface utilisateur ne signale pas clairement le mode simulé.

### P1

- Le graphe MCP construit les dépendances à chaque appel tool au lieu d'utiliser une composition centralisée réutilisable.
- La persistance existe mais n'est pas injectée dans Product Hunter MCP par défaut.
- `BACKEND_BASE_URL` existe dans la configuration MCP mais le backend HTTP correspondant n'est pas implémenté.
- `analyse_product` reste heuristique et ne consomme pas encore de vraie analyse enrichie.
- `score_product` n'utilise pas le scoring riche configurable avec sous-scores.

### P2

- La marketplace est validée mais peu exploitée dans les connecteurs locaux.
- Les opportunités et warnings de l'analyse produit sont statiques.
- Les seuils métier de l'analyse sont codés en dur.
- Aucun cache n'est présent pour les appels analytics.

## 19. ADR liées

- **ADR-001 — Monorepo applicatif privé** : Product Hunter traverse backend, MCP, persistance et documentation dans un même repository.
- **ADR-002 — Clean Architecture** : la logique métier reste dans backend/services/application, pas dans les tools MCP.
- **ADR-003 — Backend importable plutôt que serveur HTTP autonome** : Product Hunter est appelé comme package Python par MCP.
- **ADR-004 — Serveur MCP FastMCP comme interface agentique principale** : les capacités Product Hunter sont exposées en tools MCP.
- **ADR-005 — Connecteurs fournisseurs isolés derrière interfaces et mappers typés** : Amazon et Keepa passent par adaptateurs et ports.
- **ADR-006 — Repository Pattern pour persistance métier** : produits et scores peuvent être sauvegardés via repositories injectés.

## 20. Impact sur le reste du projet

### Modules impactés

- **Backend** : Product Hunter est centré sur `fba_advisor.application`, `services`, `ports`, `repositories` et `domain`.
- **MCP server** : les tools et schemas MCP constituent la frontière publique actuelle.
- **Database** : les entités `products` et `scores` sont directement pertinentes si la persistance est activée.
- **Dashboard** : impact futur lorsque le client simulé sera remplacé par un transport réel.
- **Workflows n8n** : les workflows exportés peuvent orchestrer des scénarios de recherche, analyse et scoring, mais dépendent de transports HTTP/MCP effectivement exposés.
- **Connecteurs** : Amazon et Keepa sont nécessaires au flux actuel ; Bright Data et OpenAI sont des extensions non branchées dans ce flux.

### Risques

- Confondre données locales simulées et données fournisseur réelles.
- Ajouter de la logique métier dans les tools MCP au lieu des services/use cases.
- Coupler le dashboard directement aux connecteurs ou repositories.
- Modifier les schemas MCP sans tenir compte des consommateurs agents/workflows.
- Activer des connecteurs réels sans gestion robuste des quotas, timeouts, erreurs et secrets.

### Compatibilité

- Les contrats MCP actuels doivent rester stables pour les agents consommateurs.
- Les modèles domaine doivent rester indépendants de SQLAlchemy, FastMCP et payloads fournisseurs.
- Les repositories SQLAlchemy doivent conserver l'upsert par couple `(source, identifier)` pour les produits.
- Toute future API HTTP doit appeler `ProductToolUseCases` au lieu de dupliquer les règles.
