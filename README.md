# Système de maintenance prédictive des GAB

Projet de fin d'études PFA en Big Data & Intelligence Artificielle pour la Banque Populaire.

## Architecture

- Frontend: React + TypeScript + Vite + Tailwind CSS + React Router + Recharts + React Leaflet + Lucide Icons
- Backend: FastAPI + Python + Pandas + Scikit-Learn + XGBoost + SQLAlchemy + SQLite

## Structure

- `frontend/` - application web React
- `backend/` - API FastAPI et moteur IA

## Commandes d'installation

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints principales

- `GET http://localhost:8000/api/summary`
- `GET http://localhost:8000/api/incidents`
- `GET http://localhost:8000/api/demographics`
- `GET http://localhost:8000/api/map`
- `GET http://localhost:8000/api/predictions`
- `GET http://localhost:8000/api/recommendations`
- `POST http://localhost:8000/api/predict`

## Docker

### Lancer les services avec Docker Compose

```bash
docker compose up --build
```

### Accès

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8000`
