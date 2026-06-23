# Backend FastAPI GAB

## Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Exécution

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentation Swagger

Ouvrir `http://localhost:8000/docs`

## API incidents

- `POST /api/incidents/upload`
- `GET /api/incidents`
- `GET /api/incidents/stats`
- `GET /api/incidents/top-agencies`
- `GET /api/incidents/top-atms`
- `GET /api/incidents/monthly`
- `GET /api/incidents/categories`

## API RGPH

- `POST /api/rgph/upload`
- `GET /api/rgph/stats`
- `GET /api/rgph/population`
- `GET /api/rgph/incidents-per-100k`

## API IA

- `POST /api/ai/train`
- `POST /api/ai/predict`
- `GET /api/ai/top-critical`

## Migrations

```bash
cd backend
alembic upgrade head
```
