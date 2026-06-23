from typing import List, Literal
from pydantic import BaseModel

RiskCategory = Literal['Faible', 'Moyen', 'Élevé', 'Critique']
PriorityLevel = Literal['Standard', 'Moyenne', 'Haute', 'Urgente']


class ExcelUploadResponse(BaseModel):
    message: str
    importedRows: int
    createdAgencies: int
    createdAtms: int
    updatedCities: int


class ErrorResponse(BaseModel):
    detail: str


class Summary(BaseModel):
    totalIncidents: int
    totalAtms: int
    totalAgencies: int
    totalCities: int
    incidentTrend: List[dict]


class DemographicRecord(BaseModel):
    city: str
    population: int
    male: int
    female: int
    pctUnder15: float
    pct15To59: float
    pctOver60: float


class MapPoint(BaseModel):
    city: str
    latitude: float
    longitude: float
    incidents: int
    gabCount: int = 0
    averageRiskScore: float = 0.0
    riskCategory: RiskCategory = 'Faible'


class RiskPrediction(BaseModel):
    atm: str
    riskScore: float
    riskCategory: RiskCategory


class ExcelImportResponse(BaseModel):
    message: str
    cities: int
    agencies: int
    atms: int
    incidents: int
