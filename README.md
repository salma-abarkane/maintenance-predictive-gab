# ATM Predictive Maintenance Platform

End-of-Studies (PFE) project in Big Data & Artificial Intelligence developed for Banque Populaire.

## Overview

This project is an AI-powered predictive maintenance platform for ATM networks. It combines Machine Learning, geospatial analytics, and interactive dashboards to predict ATM failures, analyze incidents, and support data-driven maintenance decisions using operational and demographic data.

## Architecture

- **Frontend:** React + TypeScript + Vite + Tailwind CSS + React Router + Recharts + React Leaflet + Lucide Icons
- **Backend:** FastAPI + Python + Pandas + Scikit-learn + XGBoost + SQLAlchemy + SQLite

## Project Structure

- `frontend/` – React web application
- `backend/` – FastAPI backend and AI engine

## Installation

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

## API Endpoints

- `GET http://localhost:8000/api/summary`
- `GET http://localhost:8000/api/incidents`
- `GET http://localhost:8000/api/demographics`
- `GET http://localhost:8000/api/map`
- `GET http://localhost:8000/api/predictions`
- `GET http://localhost:8000/api/recommendations`
- `POST http://localhost:8000/api/predict`

## Docker

### Run the application with Docker Compose

```bash
docker compose up --build
```

### Access

- **Frontend:** `http://localhost:4173`
- **Backend:** `http://localhost:8000`

## Features

- 🤖 AI-powered predictive maintenance for ATM networks
- 📊 Interactive dashboard with KPIs and analytics
- 📈 Machine Learning model for ATM failure prediction
- 🗺️ Interactive geographic visualization using Leaflet
- 🏦 ATM incident management and analytics
- 👥 Integration of demographic (RGPH) data
- 💡 AI-powered maintenance recommendations
- 📄 PDF report generation
- ⚡ FastAPI REST API
- 🎨 Modern React + TypeScript user interface

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Recharts
- React Leaflet

### Backend

- FastAPI
- Python
- SQLAlchemy
- SQLite
- Pandas
- Scikit-learn
- XGBoost

### Tools

- Docker
- Git
- GitHub
