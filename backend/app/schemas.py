from typing import List, Literal
from pydantic import BaseModel

RiskCategory = Literal['Faible', 'Moyen', 'Élevé', 'Critique']
PriorityLevel = Literal['Standard', 'Moyenne', 'Haute', 'Urgente']

class Summary(BaseModel):
    totalIncidents: int
    totalAtms: int
    totalAgencies: int
    totalCities: int
    incidentTrend: List[dict]

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

class RiskPrediction(BaseModel):
    atm: str
    riskScore: float
    riskCategory: RiskCategory

class RecommendationItem(BaseModel):
    atm: str
    agency: str
    city: str
    riskCategory: RiskCategory
    priority: PriorityLevel
    actions: List[str]

class PredictionRequest(BaseModel):
    incidentCount: int
    atmAge: int
    population: int
    pctOver60: float
    transactionVolume: float

class PredictionResponse(BaseModel):
    riskScore: float
    riskCategory: RiskCategory
    recommendation: str

class ExcelUploadResponse(BaseModel):
    message: str
    importedRows: int
    createdAgencies: int
    createdAtms: int
    updatedCities: int


class RGPHUploadResponse(ExcelUploadResponse):
    pass


class ExcelImportResponse(BaseModel):
    message: str
    cities: int
    agencies: int
    atms: int
    incidents: int
