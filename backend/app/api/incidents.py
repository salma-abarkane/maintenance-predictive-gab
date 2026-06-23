from fastapi import APIRouter, File, HTTPException, UploadFile
from ..schemas import (
    IncidentRecord,
    IncidentStatsResponse,
    TopAgencyItem,
    TopAtmItem,
    MonthlyIncidentRecord,
    CategoryDistributionRecord,
    MaintenanceKpiResponse,
    ExcelUploadResponse
)
from ..services import incident_service, excel_loader

router = APIRouter(prefix='/api/incidents', tags=['incidents'])


@router.post('/upload', response_model=ExcelUploadResponse)
def upload_incidents(file: UploadFile = File(...)) -> ExcelUploadResponse:
    try:
        return excel_loader.load_incidents_excel(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get('/', response_model=list[IncidentRecord])
def list_incidents(city: str | None = None, query: str | None = None) -> list[IncidentRecord]:
    return incident_service.list_incidents(city=city, query=query)


@router.get('/stats', response_model=IncidentStatsResponse)
def incident_stats() -> IncidentStatsResponse:
    return incident_service.get_incident_stats()


@router.get('/top-agencies', response_model=list[TopAgencyItem])
def top_agencies(limit: int = 5) -> list[TopAgencyItem]:
    return incident_service.get_top_agencies(limit=limit)


@router.get('/top-atms', response_model=list[TopAtmItem])
def top_atms(limit: int = 5) -> list[TopAtmItem]:
    return incident_service.get_top_atms(limit=limit)


@router.get('/monthly', response_model=list[MonthlyIncidentRecord])
def monthly_incidents(year: int = 2024) -> list[MonthlyIncidentRecord]:
    return incident_service.get_monthly_incidents(year=year)


@router.get('/categories', response_model=list[CategoryDistributionRecord])
def category_distribution() -> list[CategoryDistributionRecord]:
    return incident_service.get_category_distribution()


@router.get('/motifs', response_model=list[CategoryDistributionRecord])
def motif_distribution() -> list[CategoryDistributionRecord]:
    return incident_service.get_motif_distribution()


@router.get('/maintenance-kpis', response_model=MaintenanceKpiResponse)
def maintenance_kpis() -> MaintenanceKpiResponse:
    return incident_service.get_maintenance_kpis()
