from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from .common import RiskCategory


class PredictionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    incidentCount: int = 0
    atmAge: int = 5
    population: int = 0
    pctOver60: float = Field(default=0.0, alias='pct_over60')
    transactionVolume: float = Field(default=0.0, alias='transaction_volume')
    atmCode: str | None = None
    agency: str | None = None
    city: str | None = None
    typeGab: str | None = None
    dominantCategory: str | None = None
    dominantMotif: str | None = None
    incidents7d: float | None = Field(default=None, alias='incidents_7d')
    incidents30d: float | None = Field(default=None, alias='incidents_30d')
    incidents90d: float | None = Field(default=None, alias='incidents_90d')
    monthlyFrequency: float | None = Field(default=None, alias='monthly_frequency')
    mttrGab: float | None = Field(default=None, alias='mttr_gab')
    incidentsWeekend: int | None = Field(default=None, alias='incidents_weekend')
    incidentsSemaine: int | None = Field(default=None, alias='incidents_semaine')
    ratioWeekend: float | None = Field(default=None, alias='ratio_weekend')
    jourPlusCritique: str | None = Field(default=None, alias='jour_plus_critique')


class PredictionResponse(BaseModel):
    atmCode: str | None = None
    agency: str | None = None
    city: str | None = None
    riskScore: float
    failureProbability: float
    riskCategory: RiskCategory
    recommendation: str
    explanation: str
    mttrGab: float = 0.0
    incidentsWeekend: int = 0
    incidentsSemaine: int = 0
    ratioWeekend: float = 0.0
    jourPlusCritique: str = 'Non renseigné'
    dominantMotif: str = 'Non renseigné'
    dominantCategory: str = 'Non classé'


class TopCriticalATM(BaseModel):
    atm: str
    agency: str
    city: str
    riskCategory: RiskCategory
    riskScore: float
    failureProbability: float
    topMotif: str
    topCategory: str
    averageDurationMinutes: float
    incidentCount: int
    mttrGab: float = 0.0
    incidentsWeekend: int = 0
    incidentsSemaine: int = 0
    ratioWeekend: float = 0.0
    jourPlusCritique: str = 'Non renseigné'
    explanation: str


class PredictionAtmFeatures(BaseModel):
    atmCode: str
    agency: str
    city: str
    typeGab: str
    dominantCategory: str
    dominantMotif: str
    incidents7d: float
    incidents30d: float
    incidents90d: float
    monthlyFrequency: float
    population: int
    pctOver60: float
    estimatedTransactionVolume: float
    mttrGab: float
    incidentsWeekend: int
    incidentsSemaine: int
    ratioWeekend: float
    jourPlusCritique: str
    incidentsLundi: int
    incidentsMardi: int
    incidentsMercredi: int
    incidentsJeudi: int
    incidentsVendredi: int
    incidentsSamedi: int
    incidentsDimanche: int


class AtRiskPredictionItem(BaseModel):
    atmCode: str
    agency: str
    city: str
    typeGab: str
    riskScore: float
    failureProbability: float
    riskCategory: RiskCategory
    dominantMotif: str
    dominantCategory: str
    mttrGab: float
    incidentsWeekend: int
    incidentsSemaine: int
    ratioWeekend: float
    jourPlusCritique: str
    explanation: str
    recommendation: str


class RecommendationItem(BaseModel):
    atm: str
    agency: str
    city: str
    riskCategory: RiskCategory
    priority: Literal['Standard', 'Moyenne', 'Haute', 'Urgente']
    actions: list[str]
    topMotif: str
    topCategory: str
    recommendedAction: str
    businessJustification: str
