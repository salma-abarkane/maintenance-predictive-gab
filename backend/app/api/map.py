from fastapi import APIRouter

from ..schemas import MapPoint
from ..services.data_service import list_map_points

router = APIRouter(prefix='/api/map', tags=['map'])


@router.get('/', response_model=list[MapPoint])
def get_map_points() -> list[MapPoint]:
    return list_map_points()
