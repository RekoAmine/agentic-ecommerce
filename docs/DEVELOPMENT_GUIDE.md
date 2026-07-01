# Agentic Ecommerce — Guide officiel de développement

> Statut : guide officiel de développement du repository.  
> Date de création : 2026-07-01.  
> Périmètre : tout changement dans ce monorepo doit respecter ce document.  
> Source : analyse du repository existant, de `README.md`, `pyproject.toml`, `docs/ARCHITECTURE.md`, `docs/ADR.md`, du code backend, du serveur MCP, du dashboard, des tests, des migrations, des workflows n8n et de la configuration Docker.

Ce guide est destiné aux développeurs humains et aux agents IA. Il décrit l'état réel du projet et les règles à suivre pour le faire évoluer sans casser son architecture.

---

## 1. Philosophie du projet

### Objectifs

Agentic Ecommerce est une plateforme privée d'aide à la décision pour la recherche et les opérations Amazon FBA. Le projet n'est pas conçu comme un SaaS public généraliste : il s'agit d'un système personnel, durable, extensible et orienté décision.

Les objectifs actuels sont :

- fournir un socle Clean Architecture clair et testable ;
- exposer des capacités métier via un serveur MCP pour agents et orchestrateurs ;
- isoler les fournisseurs externes Amazon, Keepa, Bright Data et OpenAI derrière des connecteurs remplaçables ;
- permettre la recherche produit, l'analyse, le scoring, l'estimation de marge et la persistance ;
- offrir un dashboard Next.js qui consomme une frontière MCP, actuellement simulée ;
- conserver des workflows n8n exportables pour automatiser des scénarios de recherche ;
- maintenir une documentation d'architecture utilisable comme référence de long terme.

### Principes

Les principes non négociables sont :

1. **Le domaine prime sur les frameworks.** Les règles métier vivent dans `backend/src/fba_advisor/domain`, `services` et `application`, pas dans FastMCP, Next.js, SQLAlchemy ou n8n.
2. **Les dépendances pointent vers l'intérieur.** Les couches externes appellent les use cases et implémentent des ports ; les services ne dépendent pas de détails techniques externes.
3. **Les contrats sont explicites.** Les ports Python, les schemas Pydantic, les dataclasses domaine, les entités SQLAlchemy et les types TypeScript doivent rester cohérents.
4. **Chaque fournisseur est remplaçable.** Aucun service métier ne doit être écrit comme si Amazon, Keepa, Bright Data ou OpenAI était irremplaçable.
5. **La testabilité est une contrainte de conception.** Toute nouvelle logique importante doit pouvoir être testée avec doubles, fakes ou repositories injectés.
6. **Les prompts sont des artefacts versionnés.** Les prompts OpenAI ne doivent pas être dispersés dans le code ; ils doivent rester dans `prompts/` ou dans un emplacement de prompt documenté.
7. **La plateforme doit rester exploitable plusieurs années.** Les choix rapides qui créent du couplage, du code implicite ou de la dette structurelle sont interdits.

### Vision long terme

La vision long terme est une plateforme agentique privée capable d'orchestrer plusieurs sources de données, plusieurs outils MCP, des analyses IA versionnées, une base de connaissance persistée et une interface de décision fiable.

À long terme, le repository doit pouvoir accueillir :

- de nouveaux connecteurs fournisseurs ;
- de nouveaux tools MCP ;
- une API HTTP éventuelle ;
- de nouveaux services métier ;
- des agents de décision concrets derrière les ports existants ;
- une persistance plus riche ;
- des workflows d'automatisation plus nombreux ;
- une interface frontend connectée à un transport réel.

Ces évolutions doivent toujours préserver la séparation entre domaine, application, ports, adaptateurs et mécanismes de livraison.

---

## 2. Organisation du repository

Le repository est un monorepo applicatif privé. Les changements transverses doivent être coordonnés dans une même Pull Request lorsque les contrats changent.

| Chemin | Rôle |
| --- | --- |
| `README.md` | Présentation générale, quick start, principes d'architecture et outillage. |
| `pyproject.toml` | Configuration Python : dépendances, groupes dev, Ruff, Black, Mypy, Pytest et uv. |
| `uv.lock` | Verrouillage des dépendances Python. |
| `.env.example` | Exemple de variables d'environnement attendues. Aucun secret réel ne doit y être ajouté. |
| `Dockerfile` | Image commune pour les services Python du projet. |
| `docker-compose.yml` | Orchestration locale PostgreSQL, backend importable et MCP server. |
| `backend/` | Package Python métier central `fba_advisor` et tests backend. |
| `backend/src/fba_advisor/domain/` | Modèles domaine indépendants des frameworks, principalement des dataclasses et enums métier. |
| `backend/src/fba_advisor/application/` | Cas d'usage applicatifs. Les protocoles externes doivent passer par cette couche. |
| `backend/src/fba_advisor/services/` | Services métier : produit, marge, score, review, supplier, OpenAI. |
| `backend/src/fba_advisor/ports/` | Protocoles et interfaces internes pour inversion de dépendance. |
| `backend/src/fba_advisor/connectors/` | Connecteurs fournisseurs externes, organisés par provider. |
| `backend/src/fba_advisor/repositories/` | Adaptateurs de persistance et adaptateurs connecteurs vers les ports métier. |
| `backend/src/fba_advisor/models/` | Entités SQLAlchemy persistées. Elles ne remplacent pas les modèles domaine. |
| `backend/src/fba_advisor/database/` | Base SQLAlchemy et gestion de session. |
| `backend/src/fba_advisor/infrastructure/` | Infrastructure transverse, actuellement tracing par logging. |
| `backend/tests/` | Tests backend : services, connecteurs, repositories et configuration. |
| `mcp-server/` | Serveur MCP Python `fba_mcp_server`, wrapper d'exécution, prompts MCP et tests MCP. |
| `mcp-server/src/fba_mcp_server/server.py` | Création de l'instance `FastMCP`, enregistrement des tools et gestion d'erreurs contrôlée. |
| `mcp-server/src/fba_mcp_server/tools/` | Un fichier par tool MCP. Les tools valident et délèguent ; ils ne contiennent pas de logique métier profonde. |
| `mcp-server/src/fba_mcp_server/schemas/` | Schemas Pydantic d'entrées, sorties et DTO MCP. |
| `mcp-server/src/fba_mcp_server/services/` | Adaptateurs MCP vers les use cases backend. |
| `mcp-server/src/fba_mcp_server/interfaces/` | Protocoles côté MCP. |
| `mcp-server/src/fba_mcp_server/exceptions/` | Exceptions applicatives MCP. |
| `mcp-server/src/fba_mcp_server/utils/` | Utilitaires MCP, notamment logging. |
| `mcp-server/tests/` | Tests de configuration et de tools MCP. |
| `frontend/` | Dashboard Next.js/TypeScript. |
| `frontend/src/app/` | Pages App Router. |
| `frontend/src/features/` | Logique frontend organisée par feature. |
| `frontend/src/lib/mcp/` | Frontière client MCP dashboard, actuellement simulée. |
| `frontend/src/lib/query/` | Clés TanStack Query. |
| `frontend/src/components/ui/` | Composants UI réutilisables. |
| `frontend/src/types/` | Types TypeScript partagés. |
| `frontend/src/__tests__/` | Tests Vitest frontend. |
| `migrations/` | Configuration Alembic et migrations versionnées. |
| `database/` | Documentation et actifs liés à la base de données. |
| `prompts/` | Prompts OpenAI versionnés. Ces fichiers sont la source autorisée des prompts métier. |
| `workflows/n8n/` | Exports JSON de workflows n8n. Ils sont désactivés par défaut et importables dans n8n. |
| `docs/` | Documentation officielle d'architecture, ADR, connecteurs, workflows et présent guide. |
| `docker/` | Documentation opérationnelle Docker. |

Règle : si un nouveau dossier est ajouté, il doit avoir une responsabilité unique, être documenté dans ce guide ou la documentation d'architecture, et ne pas dupliquer une responsabilité existante.

---

## 3. Workflow Git

### Création de branche

Créer une branche par changement logique :

```bash
git checkout -b feature/nom-court
```

Conventions recommandées :

- `feature/...` pour une nouvelle capacité ;
- `fix/...` pour une correction ;
- `docs/...` pour la documentation ;
- `refactor/...` pour une amélioration interne sans changement fonctionnel ;
- `test/...` pour des tests uniquement ;
- `chore/...` pour maintenance, dépendances ou configuration.

Une branche ne doit pas mélanger plusieurs objectifs sans raison explicite.

### Commits

Un commit doit être :

- atomique ;
- compréhensible sans lire toute la PR ;
- lié à un seul changement fonctionnel ou documentaire ;
- accompagné de tests si du code est modifié ;
- sans secrets, fichiers générés inutiles ou modifications accidentelles.

Format recommandé :

```text
<type>: <résumé impératif court>
```

Exemples :

- `docs: add official development guide`
- `feat: add supplier scoring use case`
- `fix: validate marketplace in product search tool`
- `refactor: isolate keepa connector mapping`

### Pull Requests

Une Pull Request doit contenir :

- le contexte ;
- la liste des changements ;
- les fichiers ou zones impactées ;
- les tests exécutés ;
- les risques et migrations éventuelles ;
- les captures si un changement visuel perceptible est fait dans le frontend.

Une PR qui change un contrat doit expliquer les consommateurs impactés : backend, MCP, frontend, workflows, migrations ou documentation.

### Revue de code

Toute revue doit vérifier :

- respect de la Clean Architecture ;
- absence de couplage direct interdit ;
- typage strict ;
- validation Pydantic aux frontières ;
- tests pertinents ;
- cohérence documentation/code ;
- absence de secrets ;
- lisibilité et simplicité.

Aucune PR ne doit être approuvée uniquement parce que les tests passent.

---

## 4. Standards Python

Le projet utilise Python 3.13. Les standards sont définis dans `pyproject.toml`.

### Ruff

Ruff est l'outil principal de linting. Configuration actuelle :

- `target-version = "py313"` ;
- `line-length = 100` ;
- sources : `backend/src` et `mcp-server/src` ;
- règles sélectionnées : `A`, `B`, `C4`, `D`, `E`, `F`, `I`, `N`, `UP`, `W` ;
- ignorées : `D203`, `D213` ;
- tests : ignores docstrings module/fonction `D100`, `D103`.

Commande :

```bash
uv run ruff check .
```

Règles pratiques :

- ne pas désactiver une règle sans justification locale ;
- préférer corriger le code plutôt que multiplier les `# noqa` ;
- garder les imports triés ;
- nommer clairement les variables et fonctions ;
- éviter les fonctions trop longues.

### Black

Black formate le code Python avec une longueur de ligne de 100 caractères.

Commande :

```bash
uv run black --check .
```

Pour formater :

```bash
uv run black .
```

Ne pas introduire de style manuel contraire à Black.

### Mypy

Mypy est configuré en mode strict :

- `python_version = "3.13"` ;
- `strict = true` ;
- `mypy_path = ["backend/src", "mcp-server/src"]` ;
- packages vérifiés : `fba_advisor`, `fba_mcp_server`.

Commande :

```bash
uv run mypy
```

Règles :

- toute fonction publique doit être typée ;
- éviter `Any` sauf frontière externe ou payload provider réellement dynamique ;
- convertir les payloads externes vers des modèles typés au plus tôt ;
- préférer `Protocol` pour les dépendances abstraites ;
- préférer `Mapping`/`Sequence` aux types concrets lorsqu'une fonction ne modifie pas la collection ;
- ne pas masquer les erreurs Mypy avec des casts non justifiés.

### Pydantic

Pydantic est utilisé pour :

- configuration via `pydantic-settings` ;
- schemas MCP d'entrée et sortie ;
- modèles de payload connecteur ;
- validation aux frontières.

Règles :

- valider les entrées des protocols externes avec Pydantic ;
- ne pas utiliser Pydantic comme modèle domaine par défaut ;
- garder les dataclasses domaine indépendantes ;
- utiliser `model_dump(mode="json")` lorsque la sortie doit être sérialisable ;
- documenter les contraintes importantes dans les schemas.

### Typage

Typage obligatoire pour :

- fonctions publiques ;
- méthodes de services ;
- protocols ;
- repositories ;
- connecteurs ;
- outils MCP ;
- fixtures complexes.

Préférences :

- `dataclass(frozen=True, slots=True)` pour les objets métier immuables ;
- `Protocol` pour les ports ;
- `Decimal` pour les montants financiers aux frontières où la précision est importante ;
- `Enum` ou `Literal` pour les valeurs fermées ;
- `Path` pour les chemins de fichiers.

### Docstrings

Les docstrings sont requises par Ruff dans le code source.

Règles :

- chaque module public doit expliquer son rôle ;
- chaque classe publique doit expliquer sa responsabilité ;
- chaque fonction ou méthode publique doit décrire ce qu'elle fait ;
- la docstring ne doit pas répéter mécaniquement le nom ;
- les détails métier ou invariants doivent être documentés dans la docstring ou dans la documentation projet.

---

## 5. Conventions de nommage

### Variables

- Utiliser `snake_case`.
- Choisir un nom métier explicite : `monthly_sales_estimate`, `review_count`, `margin_percent`.
- Éviter les abréviations ambiguës.
- Pour les montants, inclure l'unité ou le sens : `sale_price`, `landed_cost`, `fulfillment_cost`.
- Pour les booléens, utiliser `is_`, `has_`, `should_`, `can_` lorsque cela clarifie.

### Classes

- Utiliser `PascalCase`.
- Les services finissent généralement par `Service` : `ScoreService`, `MarginService`.
- Les ports repositories finissent par `Repository` : `ProductRepository`.
- Les connecteurs clients peuvent finir par `Client`.
- Les exceptions doivent finir par `Error` ou `Exception` selon le style du module existant.

### Fonctions et méthodes

- Utiliser `snake_case`.
- Employer un verbe clair : `search_products`, `analyse_product`, `calculate_margin`, `score_product`.
- Les méthodes qui persistent commencent souvent par `save`.
- Les méthodes de lecture peuvent commencer par `get`, `list`, `search` ou `find` selon le sens.

### Modules

- Utiliser `snake_case.py`.
- Un module doit avoir une responsabilité claire.
- Pour les tools MCP, conserver le modèle un fichier par tool.
- Pour les connecteurs, conserver les noms standard : `client.py`, `interfaces.py`, `models.py`, `mapper.py`, `exceptions.py`.

### Packages

- Utiliser des noms courts en `snake_case`.
- Ne pas créer de package générique fourre-tout comme `common`, `misc` ou `helpers` sans responsabilité explicite.
- Préférer un package métier (`services/score`) ou architectural (`ports`) plutôt qu'un regroupement vague.

### Tests

- Les fichiers de tests Python doivent suivre `test_*.py`.
- Les tests frontend vivent dans `frontend/src/__tests__/` et utilisent des noms explicites comme `score.test.ts`.
- Les noms de tests doivent décrire le comportement attendu, pas l'implémentation.
- Préférer `test_<action>_<expected_result>`.

---

## 6. Clean Architecture

### Règle centrale

Les dépendances doivent toujours pointer vers l'intérieur :

```text
Frameworks / UI / MCP / DB / Providers
→ Adapters
→ Application use cases
→ Services métier
→ Domain + Ports
```

Le domaine ne connaît aucun framework. Les services connaissent les ports et modèles domaine. Les adaptateurs connaissent les frameworks et implémentent les ports.

### Couches du projet

#### Domaine

Chemin : `backend/src/fba_advisor/domain/`.

Responsabilités :

- représenter les concepts métier ;
- contenir les dataclasses et enums indépendants ;
- rester sans dépendance à SQLAlchemy, Pydantic, MCP, Next.js ou APIs externes.

Interdits :

- imports de frameworks ;
- appels HTTP ;
- accès base ;
- logique de sérialisation provider ;
- prompts OpenAI.

#### Services métier

Chemin : `backend/src/fba_advisor/services/`.

Responsabilités :

- appliquer les règles métier ;
- orchestrer des calculs locaux ;
- utiliser des ports injectés ;
- retourner des modèles domaine ou valeurs métier.

Interdits :

- appeler directement FastMCP ;
- importer le frontend ;
- créer des sessions SQLAlchemy directement ;
- construire des clients HTTP provider en dur ;
- dépendre d'un connecteur concret lorsqu'un port existe.

#### Ports

Chemin : `backend/src/fba_advisor/ports/`.

Responsabilités :

- définir les capacités nécessaires au métier ;
- isoler les services des implémentations ;
- faciliter les fakes de tests.

Règles :

- les ports doivent rester petits ;
- un port doit exprimer un besoin métier, pas la forme d'une API externe ;
- ne pas créer un port unique géant.

#### Application

Chemin : `backend/src/fba_advisor/application/`.

Responsabilités :

- exposer des cas d'usage cohérents ;
- orchestrer plusieurs services ;
- servir de façade aux protocoles externes ;
- appliquer les règles d'orchestration transverses.

Règle : tout nouveau protocole externe doit appeler cette couche plutôt que réimplémenter la logique.

#### Adaptateurs et infrastructure

Chemins :

- `backend/src/fba_advisor/connectors/` ;
- `backend/src/fba_advisor/repositories/` ;
- `backend/src/fba_advisor/models/` ;
- `backend/src/fba_advisor/database/` ;
- `backend/src/fba_advisor/infrastructure/` ;
- `mcp-server/` ;
- `frontend/` ;
- `workflows/`.

Responsabilités :

- convertir les entrées/sorties externes ;
- implémenter les ports ;
- gérer transport, persistance, logging, API providers, UI et orchestration externe.

### Règles pratiques

- Un tool MCP valide, délègue et mappe ; il ne décide pas la stratégie métier.
- Un connecteur appelle un fournisseur ; il ne score pas un produit.
- Un repository persiste ; il ne fait pas d'analyse métier.
- Un service métier calcule et orchestre ; il ne connaît pas les détails du transport.
- Le frontend ne doit pas appeler directement les connecteurs backend.
- Les workflows n8n ne doivent pas devenir la seule source de logique métier.

---

## 7. SOLID

### S — Single Responsibility Principle

Chaque module doit avoir une responsabilité unique.

Application dans le projet :

- un tool MCP par fichier ;
- un service par domaine fonctionnel ;
- un connecteur par provider ;
- un mapper par connecteur ;
- un repository par responsabilité de persistance.

À éviter :

- services qui font aussi HTTP, persistance et scoring ;
- modules `utils` contenant de la logique métier ;
- pages frontend qui contiennent des règles backend.

### O — Open/Closed Principle

Le système doit être extensible sans modifier excessivement l'existant.

Application :

- ajouter un nouveau provider via un nouveau connecteur et un adapter vers un port ;
- ajouter un nouveau tool MCP via un fichier dédié et un enregistrement serveur ;
- ajouter un nouveau service sans modifier les services non liés ;
- ajouter une nouvelle stratégie via injection plutôt que condition globale.

### L — Liskov Substitution Principle

Toute implémentation d'un port doit pouvoir remplacer une autre sans casser le consommateur.

Application :

- un fake de test doit respecter le même contrat qu'un repository SQLAlchemy ;
- un connecteur local doit produire les mêmes concepts métier qu'un connecteur réel ;
- une implémentation de `ProductCatalog` ne doit pas exiger des paramètres cachés.

### I — Interface Segregation Principle

Les interfaces doivent rester petites.

Application :

- séparer catalogue produit, analytics, reviews, agents, repositories et tracing ;
- ne pas forcer un service de marge à dépendre d'un port fournisseur ;
- ne pas créer un `ProviderClient` universel.

### D — Dependency Inversion Principle

Les couches haut niveau dépendent d'abstractions.

Application :

- services vers ports ;
- application vers services injectés ;
- tools MCP vers interface de service MCP ;
- frontend vers `DashboardMcpClient` et non vers une implémentation globale non remplaçable.

---

## 8. Dépendances

### Quand ajouter une dépendance

Ajouter une dépendance uniquement si :

- elle résout un besoin réel et actuel ;
- elle réduit la complexité globale ;
- elle est maintenue ;
- elle est compatible Python 3.13 ou avec la version Node/Next utilisée ;
- elle ne duplique pas une dépendance déjà présente ;
- elle ne force pas une architecture contraire au projet.

Ne pas ajouter une dépendance pour éviter d'écrire quelques lignes simples, sauf si elle apporte sécurité, robustesse ou standardisation.

### Comment choisir une dépendance

Critères :

- maintenance active ;
- documentation claire ;
- licence compatible ;
- API stable ;
- faible surface d'attaque ;
- intégration propre avec Ruff, Mypy, Pytest ou Next.js ;
- possibilité de tester sans réseau ;
- absence de vendor lock-in inutile.

Pour un provider externe, préférer un connecteur interne minimal si le SDK officiel introduit trop de couplage.

### Comment l'ajouter

Python :

```bash
uv add <package>
```

Dépendance de développement Python :

```bash
uv add --dev <package>
```

Frontend :

```bash
cd frontend
npm install <package>
```

Après ajout :

- vérifier les fichiers lock ;
- documenter l'usage si la dépendance est structurante ;
- ajouter ou mettre à jour les tests ;
- exécuter les checks pertinents.

### Comment la mettre à jour

Avant mise à jour :

- lire changelog et breaking changes ;
- identifier les zones impactées ;
- mettre à jour dans une PR dédiée si le risque est non trivial.

Après mise à jour :

- exécuter tests ;
- exécuter lint, format et typecheck ;
- vérifier les migrations ou changements de configuration ;
- documenter les adaptations nécessaires.

---

## 9. Gestion des erreurs

### Exceptions

Règles :

- utiliser des exceptions spécifiques dans les connecteurs ;
- convertir les erreurs provider en exceptions de connecteur ;
- ne pas laisser fuiter des payloads secrets dans les messages d'erreur ;
- dans les tools MCP, retourner des erreurs contrôlées plutôt que crasher le serveur ;
- ne pas avaler silencieusement les exceptions.

Le serveur MCP enveloppe les tools pour retourner :

- `validation_error` pour les erreurs Pydantic ;
- `tool_execution_error` pour les autres exceptions contrôlées au niveau du tool.

### Logging

Règles :

- utiliser `logging.getLogger(__name__)` ;
- logger les événements métier utiles : début/fin de recherche, nombre de résultats, tool appelé ;
- ne jamais logger de secrets ;
- ne pas logger de payload provider complet si celui-ci peut contenir des données sensibles ;
- utiliser `extra` pour les attributs structurés lorsque pertinent.

### Validation

Règles :

- valider aux frontières externes avec Pydantic ;
- convertir les types tôt ;
- valider les enums comme marketplace ;
- limiter les tailles d'entrées ;
- pour les montants, vérifier les divisions par zéro et les valeurs négatives ;
- pour les ASINs, respecter les contraintes de longueur existantes.

La validation métier doit être placée dans les services ou use cases, pas uniquement dans le frontend.

---

## 10. Développement d'un nouveau connecteur

Un connecteur isole un provider externe. Il ne contient pas de logique métier.

### Structure obligatoire

Créer :

```text
backend/src/fba_advisor/connectors/<provider>/
  __init__.py
  client.py
  exceptions.py
  interfaces.py
  mapper.py
  models.py
```

Si le connecteur doit alimenter un service métier, créer aussi un adaptateur dans :

```text
backend/src/fba_advisor/repositories/
```

ou un autre dossier d'adaptateurs si une responsabilité plus précise existe.

### Étapes

1. **Définir le besoin métier.** Identifier quel service ou port consommera les données.
2. **Créer ou réutiliser un port.** Le service doit dépendre d'un port métier, pas du connecteur.
3. **Modéliser les payloads provider.** Ajouter des modèles Pydantic dans `models.py`.
4. **Définir le protocole transport.** Dans `interfaces.py`, décrire la capacité minimale du client ou transport.
5. **Écrire le mapper.** Convertir JSON brut → modèles provider typés → objets utiles.
6. **Écrire le client.** Gérer URL, headers, authentification, requêtes, parsing et erreurs.
7. **Écrire les exceptions.** Créer des erreurs provider spécifiques.
8. **Créer l'adaptateur métier.** Mapper les modèles provider vers les modèles domaine ou ports.
9. **Ajouter la configuration.** Utiliser `pydantic-settings`, jamais de secrets codés en dur.
10. **Tester avec un transport fake.** Les tests ne doivent pas dépendre du réseau.
11. **Documenter.** Mettre à jour `docs/connectors.md` ou documentation pertinente.

### Tests

Tests minimums :

- mapping de payload valide ;
- comportement sur payload incomplet ;
- gestion d'erreur HTTP/provider ;
- headers/authentication sans exposer le secret ;
- intégration avec l'adaptateur de port ;
- absence d'appel réseau réel.

### Documentation

Documenter :

- rôle du connecteur ;
- variables d'environnement ;
- limites connues ;
- format des données importantes ;
- stratégie de retry si elle existe ;
- méthode de test locale.

---

## 11. Développement d'un nouveau Tool MCP

Un tool MCP est un mécanisme de livraison. Il expose une capacité, valide l'entrée, délègue au backend et retourne une réponse sérialisable.

### Architecture

Flux obligatoire :

```text
Tool MCP
→ Schema Pydantic request
→ Service/interface MCP
→ Backend application use case
→ Services métier
→ Ports
→ Repositories/connectors
```

Le tool ne doit pas appeler directement un connecteur, une session SQLAlchemy ou une API provider.

### Étapes

1. **Définir le cas d'usage backend.** Ajouter ou réutiliser une méthode dans `backend/src/fba_advisor/application/`.
2. **Ajouter les schemas MCP.** Entrée dans `schemas/requests.py` ou module approprié, sortie dans `schemas/responses.py` ou `schemas/products.py`.
3. **Créer le fichier tool.** Dans `mcp-server/src/fba_mcp_server/tools/<nom>.py`.
4. **Valider les paramètres.** Construire le modèle Pydantic dès l'entrée du tool.
5. **Déléguer au service MCP.** Utiliser la factory ou dependency existante.
6. **Mapper la réponse.** Retourner `ToolResponse(...).model_dump(mode="json")` ou contrat équivalent.
7. **Enregistrer le tool.** Modifier `mcp-server/src/fba_mcp_server/server.py`.
8. **Tester.** Ajouter des tests de succès, validation et erreur.
9. **Documenter.** Mettre à jour `mcp-server/README.md` et la documentation d'architecture si le tool est structurant.

### Validation

Chaque tool doit valider :

- types ;
- bornes numériques ;
- enums ;
- longueurs de chaînes ;
- valeurs financières ;
- paramètres obligatoires.

### Tests

Tests minimums :

- appel valide ;
- sortie conforme au schema ;
- erreur de validation ;
- délégation au service attendu ;
- absence de logique métier dans le tool.

### Documentation

Documenter :

- nom du tool ;
- paramètres ;
- valeurs par défaut ;
- contraintes ;
- format de réponse ;
- caractère simulé ou réel des données.

---

## 12. Développement d'un nouveau Service

Un service implémente une capacité métier.

### Règles

- Placer le service dans `backend/src/fba_advisor/services/<domaine>/service.py`.
- Ajouter `__init__.py` pour exposer proprement le service si nécessaire.
- Utiliser les modèles domaine comme entrée/sortie lorsque possible.
- Injecter les dépendances via constructeur.
- Dépendre de ports, pas d'adaptateurs concrets.
- Garder le service testable sans réseau et sans base réelle.
- Écrire des méthodes petites et nommées selon le vocabulaire métier.
- Externaliser la configuration complexe dans un fichier ou un objet de configuration typé.

### Interdits

- créer un client HTTP directement dans le service ;
- lire des variables d'environnement partout dans le service ;
- importer `mcp.server`, `FastMCP`, React ou SQLAlchemy ;
- dupliquer des règles déjà présentes dans un autre service ;
- mélanger orchestration de protocole et calcul métier.

### Tests

Ajouter des tests unitaires couvrant :

- cas nominal ;
- cas limites ;
- entrées invalides ;
- dépendances fake ;
- persistance optionnelle si repository injecté.

---

## 13. Développement d'un nouveau Repository

Un repository est un adaptateur de persistance ou de conversion vers un port. Il ne définit pas la règle métier.

### Bonnes pratiques

- Définir d'abord le port dans `backend/src/fba_advisor/ports/`.
- Implémenter le port dans `backend/src/fba_advisor/repositories/`.
- Utiliser les entités SQLAlchemy uniquement dans l'adaptateur SQLAlchemy.
- Mapper explicitement entité ↔ modèle domaine.
- Injecter la session ou la factory de session.
- Ne pas créer de session globale cachée.
- Encapsuler commit/flush selon la convention existante.
- Tester avec une session de test ou fake appropriée.

### À éviter

- retourner des entités SQLAlchemy depuis les services métier ;
- importer les repositories dans le domaine ;
- effectuer des appels provider depuis un repository SQL ;
- ajouter des requêtes non testées ;
- masquer les erreurs de contrainte sans décision métier claire.

---

## 14. Tests

### Outillage

Python :

```bash
uv run pytest
```

Frontend :

```bash
cd frontend
npm run test
```

Checks complémentaires :

```bash
uv run ruff check .
uv run black --check .
uv run mypy
cd frontend && npm run lint
cd frontend && npm run typecheck
```

### Tests unitaires

À utiliser pour :

- services métier ;
- mappers ;
- validators ;
- calculs de score et marge ;
- tools MCP avec services fake ;
- fonctions frontend pures.

Règles :

- rapides ;
- déterministes ;
- sans réseau ;
- sans dépendre d'un ordre global ;
- données de test explicites.

### Tests d'intégration

À utiliser pour :

- repositories SQLAlchemy ;
- graphes de use cases ;
- interaction MCP → backend avec dépendances contrôlées ;
- workflows critiques si automatisés.

Règles :

- isoler l'environnement ;
- documenter les prérequis ;
- ne pas dépendre de credentials réels ;
- nettoyer les données si une base est utilisée.

### Couverture

La couverture doit viser les comportements critiques :

- calcul financier ;
- scoring ;
- validation de tool ;
- mapping provider ;
- persistance ;
- erreurs provider ;
- configuration.

Il vaut mieux une couverture utile des invariants qu'un pourcentage artificiel.

### Mocks, fakes et fixtures

Préférer :

- fakes simples implémentant les ports ;
- transports fake pour connecteurs ;
- fixtures Pytest lisibles ;
- données minimales mais réalistes.

Éviter :

- mocks trop couplés à l'implémentation ;
- tests qui vérifient uniquement qu'une méthode privée a été appelée ;
- snapshot massif sans valeur ;
- appels réseau réels.

---

## 15. Documentation

### Quand documenter

Documenter lorsque :

- une règle d'architecture est ajoutée ou changée ;
- un connecteur est ajouté ;
- un tool MCP est ajouté ;
- un workflow n8n change ;
- une migration modifie le schéma ;
- une dépendance structurante est introduite ;
- une configuration d'environnement est ajoutée ;
- une décision durable est prise.

### Quoi documenter

Documenter :

- le pourquoi, pas seulement le comment ;
- les frontières entre couches ;
- les contrats d'entrée/sortie ;
- les risques et limites ;
- les commandes de test ;
- les variables d'environnement ;
- les décisions d'architecture dans `docs/ADR.md` si elles sont durables.

### Comment documenter

- Utiliser Markdown clair.
- Garder les exemples à jour.
- Ne pas promettre une capacité non implémentée sans la marquer comme future ou simulée.
- Mettre à jour la documentation dans la même PR que le code.
- Préférer des sections courtes, listes et tableaux pour les règles opérationnelles.

---

## 16. Revue de code

Checklist de revue :

- [ ] Le changement a un objectif clair.
- [ ] Les fichiers modifiés appartiennent bien au périmètre de la PR.
- [ ] La Clean Architecture est respectée.
- [ ] Les services ne dépendent pas de frameworks externes.
- [ ] Les tools MCP ne contiennent pas de logique métier profonde.
- [ ] Les connecteurs ne contiennent pas de scoring ou règles produit.
- [ ] Les repositories ne retournent pas d'entités ORM au domaine.
- [ ] Les ports restent petits et orientés métier.
- [ ] Les schemas Pydantic valident les entrées externes.
- [ ] Le typage est complet et compatible Mypy strict.
- [ ] Les docstrings utiles sont présentes.
- [ ] Les erreurs sont contrôlées et non silencieuses.
- [ ] Les logs ne contiennent pas de secrets.
- [ ] Les prompts ne sont pas codés en dur dans le code.
- [ ] Les tests couvrent le comportement modifié.
- [ ] Les tests ne dépendent pas du réseau réel.
- [ ] La documentation est mise à jour.
- [ ] Les migrations sont présentes si le schéma change.
- [ ] Le frontend respecte les contrats MCP simulés ou réels.
- [ ] Aucun fichier généré ou temporaire inutile n'est commité.

---

## 17. Checklist avant chaque Pull Request

Avant d'ouvrir une PR :

- [ ] Relire le diff complet.
- [ ] Vérifier `git status`.
- [ ] Supprimer fichiers temporaires et logs locaux.
- [ ] Vérifier qu'aucun secret n'est présent.
- [ ] Exécuter les tests Python pertinents.
- [ ] Exécuter Ruff.
- [ ] Exécuter Black en mode check.
- [ ] Exécuter Mypy si du Python a changé.
- [ ] Exécuter les tests frontend si le frontend a changé.
- [ ] Exécuter lint/typecheck frontend si le frontend a changé.
- [ ] Ajouter ou mettre à jour la documentation.
- [ ] Ajouter ou mettre à jour les tests.
- [ ] Vérifier les migrations si les modèles persistés changent.
- [ ] Vérifier les workflows si un contrat appelé par n8n change.
- [ ] Préciser les limites connues dans la description de PR.
- [ ] Ajouter une capture d'écran pour tout changement visuel perceptible.
- [ ] Confirmer que les règles interdites de la section 20 sont respectées.

---

## 18. Checklist avant chaque Release

Avant une release :

- [ ] Toutes les PRs de la release sont mergées et revues.
- [ ] `uv run pytest` passe.
- [ ] `uv run ruff check .` passe.
- [ ] `uv run black --check .` passe.
- [ ] `uv run mypy` passe.
- [ ] Les tests frontend passent.
- [ ] Le build frontend passe si une livraison UI est prévue.
- [ ] Les migrations Alembic sont cohérentes et testées.
- [ ] Les variables d'environnement nouvelles sont documentées.
- [ ] `.env.example` est à jour si nécessaire.
- [ ] Les workflows n8n impactés sont exportés et documentés.
- [ ] Les prompts versionnés sont cohérents.
- [ ] Les ADR sont à jour pour les décisions structurantes.
- [ ] La documentation utilisateur/développeur est à jour.
- [ ] Les dépendances critiques sont verrouillées.
- [ ] Aucun secret ou credential n'est commité.
- [ ] Les changements de contrat sont listés dans les notes de release.
- [ ] Les risques de rollback sont identifiés.
- [ ] Les étapes de déploiement local ou cible sont vérifiées.

---

## 19. Bonnes pratiques

Bonnes pratiques spécifiques au projet :

- Toujours commencer par lire les docs existantes avant de modifier l'architecture.
- Réutiliser les ports existants avant d'en créer de nouveaux.
- Préférer une petite extension cohérente à une abstraction prématurée.
- Garder les prompts dans `prompts/` avec version explicite.
- Garder les workflows n8n exportés désactivés par défaut sauf décision contraire.
- Maintenir la distinction entre données simulées et données réelles.
- Nommer clairement les capacités simulées dans les messages et docs.
- Garder les connecteurs indépendants les uns des autres.
- Mapper les payloads externes avant de les donner au métier.
- Injecter les dépendances pour faciliter les tests.
- Utiliser `Decimal` pour les calculs financiers exposés aux frontières critiques.
- Ajouter un test de non-régression pour chaque bug corrigé.
- Mettre à jour l'architecture lorsque les flux changent.
- Garder les modules courts et orientés responsabilité.
- Ne pas faire dépendre le dashboard de détails internes backend.
- Ne pas faire du MCP une couche métier alternative.
- Vérifier que la configuration locale reste simple : `uv sync`, tests, Docker Compose.
- Favoriser des erreurs explicites plutôt que des comportements implicites.
- Écrire les PRs comme des artefacts de maintenance future.

---

## 20. Ce qu'il est interdit de faire

Interdictions strictes :

- Casser l'API publique ou les contrats MCP sans migration, documentation et justification.
- Contourner les interfaces/ports existants.
- Créer du couplage fort entre services et connecteurs.
- Écrire des prompts OpenAI directement dans le code métier.
- Mettre des secrets, tokens, clés API ou mots de passe dans le code, les tests ou la documentation.
- Dupliquer de la logique métier entre backend, MCP, frontend et n8n.
- Accéder directement aux connecteurs depuis les tools MCP.
- Accéder directement à la base sans Repository depuis les services métier.
- Utiliser les entités SQLAlchemy comme modèles domaine.
- Ajouter une dépendance lourde sans besoin réel.
- Ajouter des appels réseau dans les tests unitaires.
- Masquer une exception sans log ou décision explicite.
- Logger des credentials ou payloads sensibles.
- Créer un module `utils` pour y placer de la logique métier non classée.
- Ajouter une nouvelle couche d'architecture sans la documenter.
- Mélanger refactor massif et feature métier dans une même PR.
- Modifier des fichiers sans lien avec la tâche.
- Ignorer Ruff, Black ou Mypy sans justification.
- Faire dépendre le domaine de Pydantic, SQLAlchemy, MCP ou React.
- Ajouter de la logique de scoring dans un connecteur provider.
- Laisser croire qu'une donnée simulée est une donnée réelle.

---

## 21. Règles pour les IA (Codex / ChatGPT)

Les agents IA doivent être plus conservateurs que les humains lorsqu'ils modifient ce repository.

### Comment analyser le projet

Avant toute modification :

1. Lire la demande utilisateur complètement.
2. Vérifier l'état Git.
3. Chercher les instructions locales applicables.
4. Lire `README.md`, `pyproject.toml` et les docs pertinentes.
5. Identifier les couches touchées.
6. Inspecter les tests existants proches.
7. Comprendre les conventions du module avant d'écrire.
8. Ne pas faire d'hypothèse sur une capacité non implémentée.

Pour explorer le repository, utiliser des commandes ciblées comme `rg`, `find`, `sed`, `git status` et `git diff`. Éviter les commandes récursives coûteuses non nécessaires.

### Quand modifier un fichier

Une IA ne doit modifier un fichier que si :

- le fichier est directement nécessaire à la demande ;
- le changement est cohérent avec l'architecture ;
- les tests ou docs nécessaires sont mis à jour ;
- le diff reste minimal et compréhensible.

Si la demande dit de ne modifier qu'un fichier, l'IA doit respecter strictement cette limite.

### Quand créer un nouveau module

Créer un nouveau module seulement si :

- aucune structure existante ne convient ;
- le module a une responsabilité claire ;
- son emplacement respecte les couches ;
- il évite de grossir un module existant au-delà du raisonnable ;
- il est testé ou documenté.

Ne pas créer de module par préférence personnelle.

### Comment éviter les régressions

- Lire les tests existants avant de changer le code.
- Ajouter un test pour tout comportement nouveau ou corrigé.
- Exécuter les tests pertinents.
- Exécuter lint/typecheck si le code change.
- Vérifier `git diff` avant de finaliser.
- Ne pas modifier les contrats sans mettre à jour tous les consommateurs.
- Conserver la compatibilité des schemas lorsque possible.
- Ne pas reformater massivement des fichiers non liés.

### Comment respecter l'architecture

- Les tools MCP doivent déléguer au service MCP et aux use cases backend.
- Les services backend doivent dépendre de ports ou de modèles domaine.
- Les connecteurs doivent rester des adaptateurs provider.
- Les repositories doivent isoler la persistance.
- Les prompts doivent rester versionnés hors code.
- Le frontend doit passer par sa frontière client MCP.
- Les workflows n8n doivent appeler des contrats documentés, pas inventer une logique métier parallèle.

### Quand demander une validation

Dans un environnement interactif, demander validation humaine si :

- la demande implique un breaking change ;
- une décision d'architecture durable est nécessaire ;
- une dépendance structurante doit être ajoutée ;
- un secret ou credential serait nécessaire ;
- plusieurs interprétations incompatibles existent ;
- un changement pourrait supprimer des données ou migrations ;
- la demande contredit ce guide ou les ADR.

Dans un environnement non interactif, ne pas bloquer inutilement : choisir l'option la plus sûre, documenter l'hypothèse dans la réponse et limiter le changement.

### Règles de sortie pour les IA

À la fin d'une tâche, une IA doit fournir :

- résumé des changements ;
- fichiers modifiés ;
- tests ou checks exécutés ;
- limites éventuelles ;
- état des commandes échouées avec cause.

Si aucun test n'est exécuté, l'indiquer explicitement avec la raison.
