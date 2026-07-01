# Architecture Decision Records — Agentic Ecommerce

> Statut du registre : référence d'architecture au 2026-07-01.
> Source : analyse du repository existant, incluant le code Python, TypeScript, Docker, Alembic, tests, workflows n8n et documentation.
> Règle : ce registre documente uniquement les décisions déjà matérialisées dans le code présent. Les éléments non implémentés sont listés dans **ADR Futures**.

## ADR-001

### Titre

Organisation du repository en monorepo applicatif privé.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le repository contient plusieurs sous-systèmes cohérents : un backend Python `fba_advisor`, un serveur MCP Python `fba_mcp_server`, un dashboard Next.js, une configuration PostgreSQL/Alembic, des workflows n8n, de la documentation et des actifs Docker.

### Problème

Le projet doit faire évoluer ensemble les frontières métier, les outils agentiques, l'interface dashboard, la persistance et l'automatisation sans créer de divergence entre repositories séparés.

### Décision

Le projet est organisé comme un monorepo structuré par responsabilités :

- `backend/` pour le coeur métier et les adaptateurs backend.
- `mcp-server/` pour l'exposition MCP.
- `frontend/` pour le dashboard.
- `migrations/` et `database/` pour la persistance.
- `workflows/` pour les exports n8n.
- `docs/` pour les documents d'architecture.

### Justification

Cette organisation permet de versionner simultanément les contrats, ports, services, schémas de données et consommateurs. Elle correspond à une plateforme privée de décision Amazon FBA, pas à un SaaS public découpé en équipes indépendantes.

### Alternatives étudiées

- Repositories séparés par service : non matérialisé dans le code.
- Package backend unique sans frontend ni MCP : incompatible avec la présence effective de `frontend/` et `mcp-server/`.
- Architecture polyrepo pilotée par contrats externes : non présente.

### Conséquences

Les changements transverses doivent être coordonnés dans un seul commit/PR. Les outils de qualité racine (`uv`, `pytest`, `ruff`, `black`, `mypy`) couvrent principalement Python, tandis que le dashboard garde son outillage Node local.

### Impact futur

Toute extension majeure devra préserver les frontières de dossiers existantes ou justifier une nouvelle frontière dans ce registre.

---

## ADR-002

### Titre

Adoption d'une Clean Architecture avec inversion explicite des dépendances.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le backend est structuré en `domain`, `services`, `ports`, `repositories`, `connectors`, `application`, `models`, `database` et `infrastructure`. Les services métier consomment des protocoles et repositories injectés plutôt que des clients globaux.

### Problème

La plateforme doit rester testable, extensible et indépendante des fournisseurs externes Amazon, Keepa, Bright Data et OpenAI.

### Décision

Le code backend suit une Clean Architecture :

- Le domaine est framework-independent et basé sur des dataclasses.
- Les services métier orchestrent les règles sur des ports.
- Les ports définissent les contrats d'accès aux capacités externes.
- Les repositories et connecteurs sont des adaptateurs.
- La couche application expose une façade de use cases pour les protocoles.

### Justification

Cette séparation est visible dans les imports : les services de produit et de score dépendent de `ports` ou de types domaine, pas de FastMCP, Next.js ou de clients HTTP. Elle rend possible le remplacement d'un connecteur réel par un connecteur local ou un double de test.

### Alternatives étudiées

- Logique métier directement dans les tools MCP : évitée par `ProductToolUseCases`.
- Clients fournisseurs appelés directement depuis les pages frontend : non présent.
- ORM comme modèle domaine : évité par la séparation entre dataclasses domaine et entités SQLAlchemy.

### Conséquences

Chaque nouvelle capacité métier doit entrer par le domaine, les ports, les services ou la couche application, puis être exposée par un adaptateur.

### Impact futur

Les futurs protocoles HTTP, CLI ou agents IA devront appeler les use cases et ne pas dupliquer les règles métier.

---

## ADR-003

### Titre

Backend Python comme package métier importable plutôt que serveur HTTP autonome.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le backend contient un package `fba_advisor` avec services, ports, repositories et connecteurs. Aucun framework HTTP backend n'est présent dans les dépendances racine. Le serveur MCP importe directement les use cases backend.

### Problème

Le projet a besoin d'un coeur métier réutilisable par plusieurs protocoles sans imposer dès maintenant une API HTTP.

### Décision

Le backend actuel est une bibliothèque applicative importable. Son point d'orchestration principal pour les tools produit est `ProductToolUseCases`.

### Justification

Le Dockerfile vérifie l'import des packages `fba_advisor` et `fba_mcp_server`, mais ne lance pas d'API backend. Le `docker-compose.yml` déclare un service `backend`, mais son image exécute le `CMD` générique du Dockerfile.

### Alternatives étudiées

- Backend FastAPI/Django/Flask : aucun code ou dépendance ne le matérialise.
- Backend uniquement MCP : non retenu car un package métier backend séparé existe.
- Backend monolithique couplé à la base : non retenu par la présence de ports et services.

### Conséquences

Les intégrations HTTP référencées par configuration ou workflows sont des intentions d'intégration, pas des capacités backend HTTP actuellement implémentées.

### Impact futur

Si une API HTTP est ajoutée, elle devra être un adaptateur appelant `fba_advisor.application`, pas une nouvelle source de logique métier.

---

## ADR-004

### Titre

Serveur MCP FastMCP comme interface agentique principale.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le package `fba_mcp_server` crée une instance `FastMCP`, configure les logs et enregistre quatre tools : recherche produit, analyse produit, calcul de marge et scoring produit.

### Problème

Les agents et orchestrateurs doivent disposer d'une interface outillée, contrôlée et indépendante de l'interface utilisateur.

### Décision

Le serveur MCP est l'interface agentique principale du projet. Les tools MCP délèguent à une interface de service MCP puis au backend.

### Justification

Le serveur encapsule les tools dans `_safe_tool`, convertit les erreurs Pydantic et exceptions génériques en dictionnaires d'erreur contrôlés, puis lance le transport SDK par défaut.

### Alternatives étudiées

- Exposition directe via HTTP REST : non implémentée.
- Exposition des connecteurs externes comme tools sans couche application : non retenue.
- Dashboard appelant directement les tools MCP réels : non présent, le dashboard utilise un client simulé.

### Conséquences

Toute nouvelle capacité agentique doit être ajoutée comme tool MCP fin, avec validation, gestion d'erreur et délégation au backend.

### Impact futur

Le transport MCP réel vers le dashboard, n8n ou des agents devra respecter les contrats de tools et la façade applicative existante.

---

## ADR-005

### Titre

Connecteurs fournisseurs isolés derrière des interfaces et mappers typés.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Les connecteurs Amazon, Keepa, Bright Data et OpenAI sont organisés avec `interfaces.py`, `models.py`, `mapper.py`, `client.py` et `exceptions.py`.

### Problème

Les payloads fournisseurs sont externes, instables et ne doivent pas contaminer les modèles métier.

### Décision

Chaque fournisseur est représenté par un connecteur typé, des modèles Pydantic de payload, un mapper et des exceptions propres. Les services métier consomment des ports ou des adaptateurs normalisés.

### Justification

Les adaptateurs `AmazonProductCatalog` et `KeepaProductAnalytics` traduisent les modèles connecteurs en `Product` domaine. Les tests de connecteurs valident les comportements sans requêtes réseau réelles.

### Alternatives étudiées

- JSON brut propagé dans les services : évité par les mappers et modèles.
- SDK fournisseurs directement importés dans le domaine : non présent.
- Connecteurs globaux singletons : non présent.

### Conséquences

Un fournisseur peut être remplacé ou simulé sans modifier le domaine. Les erreurs fournisseur restent localisées.

### Impact futur

Tout nouveau fournisseur devra suivre la même structure et fournir un mapping vers les ports existants ou de nouveaux ports explicites.

---

## ADR-006

### Titre

Repository Pattern pour la persistance métier.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Les ports de persistance définissent `ProductRepository`, `SupplierRepository`, `ReviewRepository` et `ScoreRepository`. Les implémentations SQLAlchemy résident dans `backend/src/fba_advisor/repositories/sqlalchemy.py`.

### Problème

Les services doivent pouvoir persister ou lire des données sans dépendre de SQLAlchemy ni de PostgreSQL.

### Décision

La persistance est accédée via le Repository Pattern. Les services reçoivent des repositories optionnels ou requis selon leurs cas d'usage.

### Justification

`ProductResearchService` persiste seulement si un repository est injecté. `ReviewService` dépend d'un repository de review. `ScoreService` peut enregistrer un score si un repository et un identifiant produit sont fournis.

### Alternatives étudiées

- Accès direct à la session SQLAlchemy depuis les services : non retenu.
- Active Record sur les entités ORM : non retenu.
- Persistance obligatoire dans tous les services : non retenu, plusieurs services fonctionnent sans repository.

### Conséquences

Les tests peuvent utiliser des repositories en mémoire. La transaction reste contrôlée par la session fournie à l'adaptateur SQLAlchemy.

### Impact futur

Les nouveaux agrégats persistants devront définir un port avant toute implémentation SQLAlchemy.

---

## ADR-007

### Titre

PostgreSQL avec SQLAlchemy 2 et Alembic comme base de données cible.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le projet dépend de SQLAlchemy, Alembic et `psycopg[binary]`. Docker Compose démarre `postgres:17-alpine`. Les entités ORM couvrent catégories, fournisseurs, produits, revues, scores, devis et emails.

### Problème

La plateforme doit persister des données relationnelles structurées tout en conservant des attributs fournisseurs flexibles.

### Décision

La base cible est PostgreSQL. SQLAlchemy 2 définit les entités, Alembic versionne les migrations, et les champs flexibles utilisent JSON avec variante JSONB PostgreSQL.

### Justification

Les entités utilisent contraintes d'unicité, clés étrangères, types numériques précis, timestamps timezone-aware et colonnes JSON/JSONB pour les attributs provider.

### Alternatives étudiées

- SQLite comme base principale : non matérialisé.
- NoSQL document store : non présent.
- Fichiers plats : non adaptés aux relations produits/fournisseurs/reviews/scores.

### Conséquences

Les environnements locaux et CI doivent fournir une URL PostgreSQL ou adapter les tests à des engines compatibles. Les migrations Alembic deviennent la source de vérité du schéma déployé.

### Impact futur

Toute évolution de modèle persistant devra être accompagnée d'une migration Alembic et de tests repository.

---

## ADR-008

### Titre

Injection de dépendances par constructeurs et factories explicites.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Les services reçoivent leurs dépendances dans les constructeurs. Le serveur MCP construit son graphe dans `get_product_research_service`.

### Problème

Le code doit rester testable et substituable sans conteneur DI lourd.

### Décision

L'injection de dépendances est manuelle, explicite et basée sur constructeurs, Protocols et factories.

### Justification

Cette approche est suffisante pour le périmètre actuel. Les tests injectent des doubles locaux. Les connecteurs locaux MCP remplacent les vrais credentials fournisseurs dans le graphe par défaut.

### Alternatives étudiées

- Framework de dependency injection : non présent.
- Service locator global : non présent.
- Instanciation directe des clients externes dans les services : évitée.

### Conséquences

Les compositions d'objets doivent rester lisibles et centralisées. Le graphe MCP actuel est simple mais devra être structuré davantage si les dépendances augmentent.

### Impact futur

L'ajout d'une API HTTP ou d'agents multiples pourra nécessiter des factories partagées, sans rompre l'injection explicite.

---

## ADR-009

### Titre

Configuration par variables d'environnement typées et fichier `.env`.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le backend expose `BackendSettings`, le MCP expose `McpServerSettings`, et `.env.example` documente les variables de base : environnement, logging, PostgreSQL et `DATABASE_URL`.

### Problème

La configuration doit être portable entre local, Docker et tests tout en évitant les secrets codés en dur.

### Décision

Les paramètres runtime sont chargés depuis l'environnement. Le MCP utilise `pydantic-settings`; le backend utilise une dataclass avec `getenv`.

### Justification

Docker Compose consomme `.env`, PostgreSQL utilise des valeurs par défaut, et le serveur MCP valide ses paramètres avec Pydantic.

### Alternatives étudiées

- Configuration YAML globale : seul le scoring utilise YAML pour sa politique métier.
- Secrets codés dans le code : non retenu.
- Configuration uniquement CLI : non présente.

### Conséquences

Les environnements doivent maintenir `.env` et `DATABASE_URL`. Les variables absentes retombent sur des valeurs locales par défaut.

### Impact futur

Les secrets fournisseurs, credentials cloud et paramètres de sécurité devront être ajoutés au modèle de settings approprié et à `.env.example`.

---

## ADR-010

### Titre

Docker Compose local centré sur PostgreSQL, backend et MCP.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

`docker-compose.yml` déclare `postgres`, `backend` et `mcp-server`. Le Dockerfile construit une image Python 3.13 avec `uv` et copie backend/MCP.

### Problème

Le projet doit pouvoir démarrer une base PostgreSQL et des conteneurs applicatifs de base de manière reproductible.

### Décision

L'environnement Docker actuel fournit PostgreSQL managé par healthcheck et deux services Python basés sur la même image.

### Justification

Le compose isole la base, monte les dossiers backend/MCP et charge `.env`. Il ne déclare pas encore frontend ni n8n.

### Alternatives étudiées

- Compose complet incluant frontend et n8n : non présent.
- Images séparées spécialisées backend/MCP : non présent.
- Déploiement cloud déclaratif : non présent.

### Conséquences

Docker sert aujourd'hui de socle local, pas de manifeste de production complet. Le `CMD` de l'image reste générique.

### Impact futur

Les services exécutables réels devront définir des commandes explicites et éventuellement des Dockerfiles ou targets spécialisés.

---

## ADR-011

### Titre

Services métier petits, typés et spécialisés.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le backend contient des services séparés pour produit, fournisseur, marge, score, review et OpenAI.

### Problème

Les règles métier doivent être compréhensibles, testables et modifiables indépendamment.

### Décision

Chaque service porte une responsabilité métier unique : recherche/enrichissement produit, classement fournisseur, calcul de marge, scoring, revue humaine ou prompting OpenAI.

### Justification

Les tests unitaires couvrent chaque service avec des doubles injectés. Le `ScoreService` supporte à la fois un scoring legacy et un scoring riche configurable.

### Alternatives étudiées

- Service métier unique monolithique : non présent.
- Logique dispersée dans connecteurs/repositories : évitée.
- Rules engine externe : non présent.

### Conséquences

Les nouvelles règles doivent être placées dans le service approprié ou justifier la création d'un nouveau service.

### Impact futur

L'orchestration plus complexe devra rester au niveau application/use case plutôt que gonfler les services atomiques.

---

## ADR-012

### Titre

Scoring produit configurable par politique métier externe.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

`ScoreService` définit des poids par défaut, peut charger une configuration YAML et calcule des sous-scores concurrence, marge, brandabilité, différenciation, tendance et saisonnalité.

### Problème

Le scoring d'opportunité FBA doit évoluer sans réécrire l'ensemble du service.

### Décision

Le scoring riche est piloté par une configuration de poids et seuils, avec un fichier YAML présent dans le service de score.

### Justification

La configuration externe permet d'ajuster les pondérations tout en conservant des types domaine et une explication déterministe.

### Alternatives étudiées

- Score codé uniquement en dur : partiellement conservé pour le legacy, mais complété par la configuration riche.
- Modèle IA opaque unique : non retenu dans le service de score.
- Règles stockées en base : non présent.

### Conséquences

Les changements de politique de score doivent être testés, car ils modifient les décisions produit.

### Impact futur

Les futurs modèles IA pourront enrichir les entrées du scoring, mais ne doivent pas remplacer sans ADR la capacité déterministe explicable.

---

## ADR-013

### Titre

Dashboard Next.js découplé par client MCP simulé.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le frontend est une application Next.js App Router avec TypeScript, Tailwind, composants UI, TanStack Query et Vitest. Les pages consomment `DashboardMcpClient`, implémenté par `SimulatedDashboardMcpClient`.

### Problème

Le dashboard doit pouvoir être développé sans transport MCP réel ni API backend HTTP.

### Décision

L'interface dashboard est découplée derrière un contrat TypeScript `DashboardMcpClient` et alimentée actuellement par des données simulées.

### Justification

Cette séparation permet de remplacer l'adaptateur par un transport réel sans changer les features UI. Les données simulées couvrent overview, produits, événements et configuration.

### Alternatives étudiées

- Appels directs au backend Python : non présents.
- Appels directs aux connecteurs fournisseurs : non présents.
- Données codées dans chaque page : évitées par le client partagé.

### Conséquences

Le dashboard ne reflète pas encore l'état réel de PostgreSQL ou des tools MCP. Il sert de façade UI prête à brancher.

### Impact futur

La connexion MCP réelle devra implémenter l'interface existante et adapter la gestion d'erreur/chargement côté React Query.

---

## ADR-014

### Titre

Tests automatisés par couche avec Pytest et Vitest.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le repository contient des tests backend pour settings, services, repositories et connecteurs, des tests MCP pour tools/settings, et des tests frontend Vitest.

### Problème

Les frontières d'architecture doivent être validées sans dépendre systématiquement des services externes.

### Décision

Les tests unitaires utilisent doubles, transports simulés et repositories contrôlés. Pytest couvre Python, Vitest couvre TypeScript frontend.

### Justification

Les tests démontrent l'injection de dépendances, le mapping connecteur, le comportement repository et la stabilité du client dashboard.

### Alternatives étudiées

- Tests uniquement end-to-end : non présents.
- Tests manuels : insuffisants pour les règles métier.
- Tests réseau réels fournisseurs : évités.

### Conséquences

Les changements de ports, services ou contrats UI doivent être accompagnés de tests unitaires ciblés.

### Impact futur

Des tests d'intégration PostgreSQL, MCP transport réel et workflows n8n pourront compléter la suite sans remplacer les tests par couche.

---

## ADR-015

### Titre

Logging standard Python et tracing léger par logs structurés.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Le MCP configure `logging.basicConfig`. Le backend contient `LoggingTracer`, qui crée des spans avec identifiants, attributs, durée et logs d'erreur.

### Problème

Le projet a besoin d'observabilité locale sans dépendre immédiatement d'une plateforme APM.

### Décision

L'observabilité actuelle repose sur le module standard `logging` et un tracer léger injecté.

### Justification

Le tracer respecte l'inversion de dépendance via le port `Tracer` et peut être remplacé ultérieurement. Les tools MCP loggent validation et exceptions.

### Alternatives étudiées

- OpenTelemetry complet : non présent.
- Logs print non structurés : non retenus.
- Absence de tracing : non retenue, car les use cases MCP injectent `LoggingTracer`.

### Conséquences

Les logs restent simples et portables. La corrélation distribuée complète n'est pas encore disponible.

### Impact futur

L'introduction d'OpenTelemetry ou d'un collecteur devra implémenter le port de tracing plutôt que modifier les services métier.

---

## ADR-016

### Titre

Gestion des erreurs par exceptions spécialisées et réponses contrôlées aux frontières.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Les connecteurs définissent leurs exceptions provider. Le serveur MCP encapsule les tools dans `_safe_tool` et retourne des dictionnaires d'erreur pour validation ou exécution.

### Problème

Les erreurs externes et erreurs de validation ne doivent pas faire fuiter des exceptions non contrôlées aux clients MCP.

### Décision

Les adaptateurs externes lèvent des exceptions spécialisées, et la frontière MCP les convertit en réponses contrôlées.

### Justification

Cette approche isole les erreurs fournisseur dans leurs modules et protège le protocole MCP d'un crash non formaté.

### Alternatives étudiées

- Retour systématique de `None` : non retenu car ambigu.
- Exceptions brutes jusqu'au client : non retenu à la frontière MCP.
- Hiérarchie d'erreur applicative exhaustive : partiellement présente mais pas encore généralisée.

### Conséquences

Les consommateurs MCP doivent gérer des objets contenant `error`. Les services internes peuvent continuer à lever des exceptions métier ou techniques.

### Impact futur

Une taxonomie d'erreurs applicatives commune pourra être formalisée si plusieurs protocoles publics apparaissent.

---

## ADR-017

### Titre

Typage fort Python et TypeScript comme garde-fou architectural.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Python cible 3.13, Mypy est configuré en mode strict, Ruff/Black encadrent le style, et le frontend utilise TypeScript avec `tsc --noEmit`.

### Problème

Les contrats entre domaine, ports, adaptateurs et UI doivent rester explicites et vérifiables.

### Décision

Le projet adopte le typage fort : dataclasses typées, Protocols Python, modèles Pydantic, SQLAlchemy typé et interfaces TypeScript.

### Justification

Les types rendent visibles les dépendances autorisées et réduisent les erreurs de mapping entre providers, domaine et dashboard.

### Alternatives étudiées

- Python non typé : non retenu.
- Schéma OpenAPI comme source unique : non présent.
- TypeScript laxiste côté frontend : non retenu par le script `typecheck`.

### Conséquences

Les évolutions doivent maintenir Mypy et TypeScript au vert. Les payloads externes doivent être convertis en modèles typés.

### Impact futur

Des contrats générés pourront être ajoutés, mais ne doivent pas affaiblir les frontières typées existantes.

---

## ADR-018

### Titre

Workflows n8n exportés comme orchestration optionnelle, non runtime core.

### Statut

Accepté.

### Date

2026-07-01.

### Contexte

Deux workflows JSON sont présents dans `workflows/n8n/` et la documentation n8n existe. Aucun service n8n n'est déclaré dans Docker Compose.

### Problème

Le projet doit documenter des scénarios d'automatisation sans imposer n8n comme dépendance runtime locale.

### Décision

n8n est traité comme orchestration exportable optionnelle, désactivée par défaut et externe au runtime core.

### Justification

Les workflows matérialisent des scénarios de recherche et sourcing, mais l'absence de service n8n dans Docker Compose confirme qu'ils ne sont pas un composant obligatoire du lancement local.

### Alternatives étudiées

- n8n comme service obligatoire : non présent.
- Orchestration entièrement en Python : non présente pour ces workflows.
- Absence d'automatisation déclarée : non retenue car les exports existent.

### Conséquences

Les workflows peuvent dériver si les endpoints réels ne sont pas implémentés. Ils doivent être maintenus comme artefacts d'intégration.

### Impact futur

Si n8n devient runtime officiel, il faudra ajouter compose/deployment, tests d'intégration et ADR dédiée.

---

## ADR Futures

Les décisions suivantes ne sont pas encore complètement tranchées par le code présent et devront faire l'objet d'ADR spécifiques avant implémentation structurante :

- **Authentification et autorisation** : aucun mécanisme applicatif complet n'est présent pour utilisateurs, rôles ou sessions.
- **API HTTP backend** : le backend est un package importable ; le choix d'un framework, des routes et des contrats publics reste à décider.
- **Transport réel dashboard ↔ MCP/backend** : le dashboard utilise aujourd'hui un client simulé.
- **Cache** : aucun cache applicatif ou provider n'est implémenté.
- **Message Queue / jobs asynchrones** : aucune queue runtime n'est présente.
- **Multi-utilisateur** : le modèle actuel correspond à une plateforme privée, sans tenants ni comptes.
- **Agents IA concrets** : des ports existent, mais pas d'implémentation d'agent décisionnel autonome.
- **Sourcing automatique complet** : des services fournisseurs et workflows existent, mais l'automatisation end-to-end reste à finaliser.
- **Déploiement Cloud** : aucun manifeste cloud de production n'est présent.
- **Secrets management** : `.env` est le mécanisme courant ; un gestionnaire de secrets externe n'est pas décidé.
- **Observabilité avancée** : OpenTelemetry, métriques et traces distribuées ne sont pas encore adoptés.
- **Stratégie de migration de données en production** : Alembic existe, mais la procédure opérationnelle n'est pas définie.
- **Politique de sécurité fournisseur** : rotation, scopes, stockage et audit des clés Amazon/Keepa/Bright Data/OpenAI restent à formaliser.
- **Frontend data freshness** : fréquence de rafraîchissement, invalidation et états d'erreur réels restent à définir.
- **Stratégie de tests end-to-end** : les tests unitaires existent ; les tests E2E multi-services restent à décider.
