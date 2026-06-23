from fastapi import APIRouter, File, HTTPException, UploadFile
from ..schemas import (
    ExcelUploadResponse,
    DemographicStatsResponse,
    PopulationByCityRecord,
    IncidentPer100kRecord
)
from ..services import rgph_service, excel_loader

router = APIRouter(prefix='/api/rgph', tags=['rgph'])


@router.post('/upload', response_model=ExcelUploadResponse)
def upload_rgph(file: UploadFile = File(...)) -> ExcelUploadResponse:
    try:
        return excel_loader.load_rgph_excel(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get('/stats', response_model=DemographicStatsResponse)
def demographic_stats() -> DemographicStatsResponse:
    return rgph_service.get_demographic_stats()


@router.get('/population', response_model=list[PopulationByCityRecord])
def population_by_city() -> list[PopulationByCityRecord]:
    return rgph_service.get_population_by_city()


@router.get('/incidents-per-100k', response_model=list[IncidentPer100kRecord])
def incidents_per_100k() -> list[IncidentPer100kRecord]:
    return rgph_service.get_incidents_per_100k()
