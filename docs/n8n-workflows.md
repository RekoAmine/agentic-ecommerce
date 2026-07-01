# Workflows n8n

Ce dossier ajoute deux workflows n8n exportables pour automatiser les étapes de recherche Amazon, d'analyse, de scoring, de persistance et de notification.

## Fichiers exportables

Les exports JSON sont prêts à être importés depuis l'interface n8n avec **Import from File** :

- `workflows/n8n/daily-amazon-research.json`
- `workflows/n8n/product-supplier-research.json`

Les workflows sont désactivés par défaut (`active: false`) afin d'éviter tout déclenchement involontaire après import.

## Workflow quotidien

Chaîne demandée :

```text
Recherche Amazon
↓
Analyse
↓
Scoring
↓
Base
↓
Notification
```

Le workflow `Agentic Ecommerce - Recherche Amazon quotidienne` démarre tous les jours à `07:00 UTC` et exécute les nœuds suivants :

1. **Workflow quotidien** : déclencheur planifié.
2. **Préparer la recherche** : construit les paramètres `query`, `marketplace` et `limit`.
3. **Recherche Amazon** : appelle l'outil de recherche produit.
4. **Analyse** : appelle l'outil d'analyse produit.
5. **Scoring** : appelle l'outil de scoring produit.
6. **Base** : persiste le résultat dans l'API applicative.
7. **Notification** : publie un résumé vers le webhook de notification.

## Workflow Produits

Chaîne demandée :

```text
Produit validé
↓
Recherche fournisseurs
↓
Analyse
↓
Score
↓
Notification
```

Le workflow `Agentic Ecommerce - Recherche fournisseurs produit` démarre sur un webhook `POST /webhook/product-validated` et exécute les nœuds suivants :

1. **Produit validé** : reçoit le produit validé par l'utilisateur ou par une règle métier.
2. **Recherche fournisseurs** : recherche des fournisseurs candidats pour le produit.
3. **Analyse** : analyse les fournisseurs retournés.
4. **Score** : calcule le score de sourcing.
5. **Notification** : envoie le résultat final vers le webhook de notification.

Exemple de payload webhook :

```json
{
  "product_identifier": "B0EXAMPLE",
  "asin": "B0EXAMPLE",
  "title": "Produit exemple",
  "marketplace": "amazon_us"
}
```

## Variables d'environnement n8n

Configurez ces variables dans l'environnement n8n avant d'activer les workflows :

| Variable | Utilisation | Valeur par défaut dans l'export |
| --- | --- | --- |
| `MCP_HTTP_URL` | Endpoint HTTP des outils MCP (`search_products`, `analyse_product`, `score_product`). | `http://mcp-server:8000/tools/...` |
| `AGENTIC_API_URL` | Endpoint de persistance des produits scorés. | `http://backend:8000/products` |
| `SUPPLIER_SEARCH_URL` | Endpoint de recherche fournisseurs. | `http://backend:8000/suppliers/search` |
| `SUPPLIER_ANALYSIS_URL` | Endpoint d'analyse fournisseurs. | `http://backend:8000/suppliers/analyse` |
| `SUPPLIER_SCORE_URL` | Endpoint de scoring fournisseurs. | `http://backend:8000/suppliers/score` |
| `NOTIFICATION_WEBHOOK_URL` | Webhook Slack, Discord, email gateway ou autre service de notification. | Aucune |
| `AMAZON_DAILY_QUERY` | Requête quotidienne Amazon. | `amazon fba product opportunities` |
| `AMAZON_MARKETPLACE` | Marketplace Amazon ciblée. | `amazon_us` |

## Import et export

### Importer

1. Ouvrir n8n.
2. Cliquer sur **Workflows** puis **Import from File**.
3. Sélectionner l'un des fichiers JSON dans `workflows/n8n/`.
4. Vérifier les URLs et credentials.
5. Activer le workflow uniquement après validation.

### Réexporter après modification

Après modification dans n8n :

1. Ouvrir le workflow.
2. Cliquer sur le menu `...`.
3. Choisir **Download** ou **Export**.
4. Remplacer le fichier JSON correspondant dans `workflows/n8n/`.
5. Valider le JSON avant commit.

## Notes d'intégration

- Les nœuds HTTP utilisent des URLs configurables par variables d'environnement pour rester portables entre local, Docker et production.
- Les endpoints fournisseurs sont des points d'intégration attendus : ils peuvent être branchés sur l'API backend, un webhook interne ou un service externe.
- Le nœud de notification ne contient pas de secret ; il attend `NOTIFICATION_WEBHOOK_URL` dans l'environnement n8n.
- Les exports restent volontairement génériques pour être importables sans credentials n8n spécifiques.
