# 📊 Prévision du prix de l’or (Prevision-prix-Or)

Application de **prévision de série temporelle** sur le cours de l’or (données Yahoo Finance), avec comparaison de deux approches : **Amazon Chronos** et un **Time Series Transformer** (Hugging Face). Une **API FastAPI** expose les prévisions ; une **UI Streamlit** les visualise. Le tout est conteneurisé (**Docker** + **Nginx**) et l’infra cloud est provisionnée avec **Terraform** sur **Scaleway**.

## 🔍 Sommaire

- [Arborescence](#arborescence)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation locale](#installation-locale)
- [Docker](#docker)
- [Tests et qualité](#tests-et-qualité)
- [Infrastructure (Terraform, Scaleway)](#infrastructure-terraform-scaleway)
- [CI/CD (GitHub Actions)](#cicd-github-actions)
- [Variables d’environnement](#variables-denvironnement)


## 🏗️ Architecture
```
Data ingestion from Yahoo Finance API → Feature Engineering → Chronos & TimeSeriesTransformer Training → Déploiement sur VPS → UI sur web 
```

## 📁 Arborescence

```text
Prevision-prix-Or/
├── api/                    # FastAPI (routes /health, /forecast)
├── ml/                     # Données, modèles (Chronos, TST), inférence
├── ui/                     # Streamlit
├── infra/
│   ├── Dockerfile.api
│   ├── Dockerfile.ui
│   ├── docker-compose.yaml
│   ├── nginx.conf
│   └── terraform/          # Instance Scaleway + bootstrap cloud-init
├── tests/                  # Pytest (API)
├── .github/workflows/      # CI/CD
├── requirements.txt        # Dépendances « full » locales (optionnel)
├── requirements-api.txt    # Image Docker API
├── requirements-ui.txt     # Image Docker UI
├── requirements-ci.txt       # CI GitHub Actions (léger)
└── pyproject.toml
```

## 🛠️ Stack technique

| Couche | Technologies |
|--------|----------------|
| API | FastAPI, Uvicorn |
| ML | PyTorch, `transformers`, `chronos-forecasting`, scikit-learn |
| UI | Streamlit, Plotly, pandas |
| Données | yfinance |
| Conteneurs | Docker, Nginx (reverse proxy) |
| Infra | Terraform, Scaleway |
| CI/CD | GitHub Actions (tests, build Docker, push, déploiement SSH) |


## 🚀 Lancer le projet

### Prérequis

- **Python 3.11** (aligné sur les Dockerfiles et le CI)
- **Docker** et **Docker Compose** v2 pour l’exécution stack complète
- Compte **Scaleway** + clés API pour Terraform (hors dépôt Git)

### Installation locale

À la racine du dépôt :

```bash
# API uniquement (même stack que le conteneur API)
pip install -r requirements-api.txt
set PYTHONPATH=.   # Windows PowerShell : $env:PYTHONPATH="."
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# UI Streamlit (nécessite aussi le package ml/ pour les imports)
pip install -r requirements-ui.txt
set PYTHONPATH=.
streamlit run ui/app.py --server.port 8501
```

L’API expose notamment :

- `GET /health/` — statut
- `POST /forecast/` — prévisions (charge les modèles ML à l’appel)

### Docker

Depuis le dossier `infra/` :

```bash
cd infra
docker compose up -d --build
```

Services typiques : API (`8000`), UI Streamlit (`8501`), Nginx (`80`) selon `docker-compose.yaml` et `nginx.conf`.

### Tests et qualité

Le fichier **`requirements-ci.txt`** installe le minimum pour les tests sans toute la stack lourde au chargement (l’import des modèles lourds est différé côté route `/forecast`).

```bash
pip install -r requirements-ci.txt
set PYTHONPATH=.
pytest -q
flake8 api ml tests
```

### Infrastructure (Terraform, Scaleway)

Le répertoire **`infra/terraform/`** décrit une instance (Ubuntu) avec IP publique et **cloud-init** exécutant `gold-bootstrap.sh` (installation Docker, clone du dépôt, premier `docker compose`).

1. Copier **`terraform.tfvars.example`** vers **`terraform.tfvars`** (non versionné) ou exporter les variables d’environnement Scaleway.
2. Renseigner `scw_access_key`, `scw_secret_key`, `scw_project_id`, `ssh_public_key`, etc. Voir **`variables.tf`**.
3. `terraform init` puis `terraform apply`.

Ne **jamais** committer `terraform.tfstate`, `*.tfvars` ni clés privées.

### CI/CD (GitHub Actions)

Workflow **`.github/workflows/ci-cd.yaml`** :

1. **CI** (push / PR sur `main`) : installation `requirements-ci.txt`, `pytest`, `flake8`, build des images Docker en validation.
2. **CD** (push sur `main` uniquement) : build et push des images vers **GitHub Container Registry** (`ghcr.io/.../api` et `.../ui`).

**Déploiement SSH** (optionnel) : définir la variable de dépôt **`DEPLOY_ENABLED`** = `true` et les secrets **`DEPLOY_HOST`**, **`DEPLOY_USER`**, **`DEPLOY_SSH_KEY`** (IP / utilisateur SSH de la VM, clé privée — pas les clés API Scaleway). Optionnel : **`DEPLOY_PATH`** (chemin du clone sur le serveur, défaut fréquent : `/root/Prevision-prix-Or`).

**Secret `DEPLOY_SSH_KEY` (dépannage)** : contenu de la **clé privée** complète (`id_ed25519` ou `id_rsa`, **pas** le `.pub`). Coller tout le bloc, de `-----BEGIN … PRIVATE KEY-----` jusqu’à `-----END … PRIVATE KEY-----`, avec les retours à la ligne. Préférer une clé **sans phrase secrète** pour GitHub Actions (sinon il faut étendre le workflow avec un secret `passphrase`). L’erreur `ssh: no key found` indique en général un secret vide, une clé publique à la place de la privée, ou un format PEM tronqué.

---
