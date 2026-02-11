# Dubai Mall — Customer Segmentation (AI Engineer Portfolio)

> **Unsupervised Learning + FastAPI + Dashboard + Docker + CI**  
> Projet de segmentation client (clustering) sur le dataset *Mall Customers* avec un **pipeline entraîné**, une **API REST** et une **UI dashboard** (simulation + upload CSV + profils de clusters).

---

## Contexte

Dans un environnement retail hautement concurrentiel, le Dubai Mall souhaite mieux comprendre sa clientèle afin d’optimiser ses stratégies marketing et améliorer l’expérience client.

Ce projet met en place une **segmentation non supervisée** pour :
- identifier des segments homogènes,
- mieux cibler les campagnes,
- personnaliser l’expérience client,
- guider la stratégie de fidélisation.

---

## Objectif

Construire un modèle de segmentation permettant :
- **d’inférer un cluster** pour un client (simulation / API),
- **d’analyser un fichier CSV** (distribution des segments),
- **d’expliquer les segments** via des profils (moyennes âge / revenu / spending, etc.),
- **d’exporter un CSV enrichi** (avec colonne `cluster_id`).

---

## Jeu de données

Dataset : `data/Mall_Customers.csv`

Variables principales :
- `Gender`
- `Age`
- `Annual Income (k$)`
- `Spending Score (1-100)`

Les features retenues couvrent 3 dimensions :
- **Démographique** (Age, Gender)
- **Capacité financière** (Annual Income)
- **Comportement d’achat** (Spending Score)

---

## 1) Analyse Exploratoire (EDA)

Notebook : `notebooks/01_eda.ipynb`

Contenu :
- analyse descriptive,
- distributions,
- corrélations,
- exploration des signaux “segments” possibles.

---

## 2) Préprocessing

Notebook : `notebooks/02_clustering.ipynb`

Principes :
- sélection / validation des features attendues,
- standardisation et encodage (selon pipeline),
- justification (les méthodes de clustering sont sensibles à l’échelle).

---

## 3) Clustering & Évaluation

Méthodes testées (selon notebooks / itérations) :
- K-Means
- (optionnel selon exploration) Clustering hiérarchique, DBSCAN, GMM

Évaluation :
- Silhouette score
- Davies-Bouldin Index
- Calinski-Harabasz

---

## 4) Modèle retenu

**K-Means** (k = 4 dans la version actuelle, configurable dans le code d’entraînement)

Artefacts générés :
- `artifacts/clustering_pipeline.joblib`
- `artifacts/metadata.json`

> Le pipeline est re-généré automatiquement via `python -m scripts.train` (CI / Docker build selon configuration).

---

## 5) Interprétation des segments

L’application génère des **profils de clusters** :
- taille du cluster et % population,
- âge moyen,
- revenu moyen,
- spending moyen,
- label “métier” (si défini).

Ces profils alimentent :
- la liste “Profils de clusters”,
- un radar chart (comparatif normalisé),
- les badges colorés cohérents sur toute l’UI.

---

## Architecture (haut niveau)

- **FastAPI** : API + routes web
- **Jinja2** : templates HTML (dashboard)
- **Chart.js** : bar chart + radar chart
- **Scikit-learn** : pipeline + modèle
- **Joblib** : sérialisation pipeline
- **CI GitHub Actions** : lint + tests + entraînement (si configuré)

---

## Exécuter en local (dev)

### 1) Créer et activer l’environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

### 2) Entraîner le modèle (générer les artefacts)
```bash
python -m scripts.train
```

### 3) Lancer l’app
```bash
uvicorn main:app --reload
```

UI : http://127.0.0.1:8000  
Docs API (Swagger) : http://127.0.0.1:8000/docs

---

## Exécuter via Docker

### Build
```bash
docker build -t dubai-mall-ai .
```

### Run
```bash
docker run -p 8000:8000 dubai-mall-ai
```

http://127.0.0.1:8000

---

## ☁️ Déploiement Render (Docker)

Un fichier `render.yaml` est fourni :
```yaml
services:
  - type: web
    name: dubai-mall-ai
    env: docker
    plan: free
    autoDeploy: true
    healthCheckPath: /api/health
```

Déploiement :
1. Pousser le repo sur GitHub
2. Render → New → Web Service → “Deploy from GitHub repo”
3. Render détecte Docker et build automatiquement
4. Healthcheck : `/api/health`

---

# 🔌 Utiliser l’API (pour des tiers)

> Base URL = ton domaine Render (ou `http://127.0.0.1:8000` en local)  
> Exemple : `https://dubai-mall-ai.onrender.com`

## 1) Healthcheck
**GET** `/api/health`

```bash
curl -s https://dubai-mall-ai.onrender.com/api/health
```

Réponse :
```json
{ "status": "ok" }
```

## 2) Récupérer les métadonnées du modèle
**GET** `/api/metadata`

```bash
curl -s https://dubai-mall-ai.onrender.com/api/metadata
```

Retour typique :
```json
{
  "model_name": "kmeans",
  "expected_columns": ["Gender","Age","Annual Income (k$)","Spending Score (1-100)"],
  "params": { "n_clusters": 4, "random_state": 42, "n_init": 10 },
  "metrics": { "silhouette": 0.35, "davies_bouldin": 1.06, "calinski_harabasz": 101.48 }
}
```

## 3) Obtenir les profils des clusters
**GET** `/api/profiles`

```bash
curl -s https://dubai-mall-ai.onrender.com/api/profiles
```

Réponse :
```json
{ "profiles": [ ... ] }
```

## 4) Prédire le cluster d’un client (JSON)
**POST** `/api/cluster/row`

Body JSON (exactement ces champs) :
```json
{
  "Gender": "Male",
  "Age": 30,
  "Annual Income (k$)": 60,
  "Spending Score (1-100)": 50
}
```

cURL :
```bash
curl -s -X POST https://dubai-mall-ai.onrender.com/api/cluster/row   -H "Content-Type: application/json"   -d '{"Gender":"Male","Age":30,"Annual Income (k$)":60,"Spending Score (1-100)":50}'
```

Réponse typique :
```json
{
  "cluster_id": 2,
  "cluster_label": "Regular shoppers",
  "cluster_pct": 0.24,
  "warnings": []
}
```

## 5) Segmenter un fichier CSV (upload)
**POST** `/api/cluster/file` (multipart/form-data)

Le CSV doit contenir les colonnes :
- `Gender`
- `Age`
- `Annual Income (k$)`
- `Spending Score (1-100)`

cURL :
```bash
curl -s -X POST https://dubai-mall-ai.onrender.com/api/cluster/file   -F "file=@./data/Mall_Customers.csv"
```

Réponse :
- `n_rows`
- `cluster_counts`
- `profiles`
- `preview` (20 premières lignes typiquement)
- `warnings`

## 6) Export CSV enrichi (avec cluster_id)
**POST** `/api/cluster/file/export` (multipart/form-data)

```bash
curl -L -X POST https://dubai-mall-ai.onrender.com/api/cluster/file/export   -F "file=@./data/Mall_Customers.csv"   --output mall_customers_clustered.csv
```

➡️ Télécharge un CSV enrichi contenant une colonne `cluster_id`.

---

## Bonnes pratiques pour les utilisateurs tiers
- Utiliser `/api/metadata` pour valider les colonnes attendues.
- Valider les types (Age, Income, Spending = numériques).
- Préférer `/api/cluster/file` pour batch processing.
- Utiliser `/api/cluster/file/export` si besoin d’un fichier final exploitable.

---

## Qualité & CI

Le projet inclut :
- `ruff` (lint + fix)
- `pytest` (tests unitaires + API tests)
- GitHub Actions (CI)

En local :
```bash
ruff check .
pytest
```

---

## Technologies

- Python 3.12
- FastAPI + Uvicorn
- Pandas
- Scikit-learn
- Joblib
- Jinja2 + Chart.js
- Docker
- GitHub Actions
- Render

---

## Conclusion

Cette application fournit une **solution complète “data-to-product”** :
- pipeline ML entraînable,
- API de prédiction et batch,
- dashboard web,
- export opérationnel,
- Docker & déploiement cloud.

---
