from fastapi import APIRouter
from ..services.data_loader import get_data_status

router = APIRouter(prefix='/api', tags=['monitoring'])


@router.get('/health')
def health_check() -> dict:
    return {'status': 'ok', 'service': 'GAB Predictive Maintenance API'}


@router.get('/data-status')
def data_status() -> dict:
    return get_data_status()
