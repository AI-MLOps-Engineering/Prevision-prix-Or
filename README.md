# Prevision-prix-Or

📁 Prevision-prix-Or/
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── forecast.py
│   │   └── health.py
│   └── schemas.py
│
├── ml/
│   ├── __init__.py
│   ├── data_fetcher.py
│   ├── preprocessing.py
│   ├── chronos_model.py   ← modèle Chronos
│   ├── tst_model.py       ← modèle TimeSeriesTransformerForPrediction
│   ├── train.py
│   └── inference.py       ← orchestre les deux modèles
│
├── ui/
│   ├── __init__.py
│   └── app.py
│
├── infra/
│   ├── Dockerfile.api
│   ├── Dockerfile.ui
│   ├── docker-compose.yaml
│   ├── nginx.conf
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── .github/
│   └── workflows/
│       └── ci-cd.yaml
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── requirements.txt
├── pyproject.toml        
├── .env
├── .gitignore
└── README.md


Projet de prévision du prix de l'or utilisant un modèle Transformer (Hugging Face),
servi via une API FastAPI et une interface Streamlit, packagé avec Docker et prêt
pour un déploiement Cloud (AWS/Azure).

## Stack

- FastAPI
- Streamlit
- Transformers (Hugging Face)
- Docker, Nginx
- CI/CD (GitHub Actions)
- Cloud (AWS/Azure)

## Lancement local

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
streamlit run ui/app.py
```


## Avec Docker

```bash
cd infra
docker-compose up --build
```

--- 