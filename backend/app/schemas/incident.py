from typing import List
from pydantic import BaseModel


class IncidentRecord(BaseModel):
    id: int
    agency: str
    atm: str
    city: str
    category: str
    severity: str
    reportedAt: str

    model_config = {
        'from_attributes': True
    }


class IncidentStatsResponse(BaseModel):
    totalIncidents: int
    uniqueAgencies: int
    uniqueAtms: int
    categories: List[str]


class TopAgencyItem(BaseModel):
    agency: str
    city: str
    incidentCount: int


class TopAtmItem(BaseModel):
    atm: str
    agency: str
    city: str
    incidentCount: int


class MonthlyIncidentRecord(BaseModel):
    month: str
    incidentCount: int


class CategoryDistributionRecord(BaseModel):
    category: str
    count: int
    percentage: float


class MaintenanceKpiResponse(BaseModel):
    averageDurationMinutes: float
    mttrMinutes: float
    topMotif: str
    dominantCategory: str
    criticalAtms: int
    incidentsPerAtm: float
    mostImpactedCity: str
