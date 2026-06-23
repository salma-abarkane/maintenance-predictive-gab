from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .api import incidents_router, rgph_router, ai_router, predict_router, health_router, map_router
from .services.data_loader import load_default_data

origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

app = FastAPI(
    title='GAB Predictive Maintenance API',
    version='1.0.0',
    description='Backend FastAPI pour le suivi des incidents GAB, RGPH et IA prédictive.'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(health_router)
app.include_router(incidents_router)
app.include_router(rgph_router)
app.include_router(ai_router)
app.include_router(predict_router)
app.include_router(map_router)


@app.on_event('startup')
def load_excel_data() -> None:
    try:
        load_default_data(force=True)
    except (FileNotFoundError, ValueError) as exc:
        logging.exception('Impossible de charger les fichiers Excel: %s', exc)


@app.get('/', tags=['monitoring'])
def root() -> dict:
    return {
        'service': 'GAB Maintenance Prédictive',
        'version': '1.0.0',
        'status': 'ready'
    }
