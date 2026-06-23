from typing import List
from pydantic import BaseModel


class DemographicStatsResponse(BaseModel):
    totalCities: int
    totalPopulation: int
    averagePctOver60: float
    citiesWithIncidents: int


class PopulationByCityRecord(BaseModel):
    city: str
    population: int
    male: int
    female: int
    pctUnder15: float
    pct15To59: float
    pctOver60: float


class IncidentPer100kRecord(BaseModel):
    city: str
    incidents: int
    incidentsPer100k: float
