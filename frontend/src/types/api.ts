export interface IncidentRecord {
  id: number
  agency: string
  atm: string
  city: string
  category: string
  severity: string
  reportedAt: string
}

export interface IncidentStatsResponse {
  totalIncidents: number
  uniqueAgencies: number
  uniqueAtms: number
  categories: string[]
}

export interface TopAgencyItem {
  agency: string
  city: string
  incidentCount: number
}

export interface TopAtmItem {
  atm: string
  agency: string
  city: string
  incidentCount: number
}

export interface MonthlyIncidentRecord {
  month: string
  incidentCount: number
}

export interface MaintenanceKpiResponse {
  averageDurationMinutes: number
  mttrMinutes: number
  topMotif: string
  dominantCategory: string
  criticalAtms: number
  incidentsPerAtm: number
  mostImpactedCity: string
}

export interface CategoryDistributionRecord {
  category: string
  count: number
  percentage: number
}

export interface ExcelUploadResponse {
  message: string
  importedRows: number
  createdAgencies: number
  createdAtms: number
  updatedCities: number
}

export interface DataStatusResponse {
  loaded: boolean
  loadedAt: string | null
  lastError: string
  files: {
    incidents: boolean
    rgph: boolean
    mapping: boolean
    cityStats: boolean
  }
  counts: {
    incidents: number
    agencies: number
    atms: number
    cities: number
  }
}

export interface DemographicRecord {
  city: string
  population: number
  male: number
  female: number
  pctUnder15: number
  pct15To59: number
  pctOver60: number
}

export interface DemographicStatsResponse {
  totalCities: number
  totalPopulation: number
  averagePctOver60: number
  citiesWithIncidents: number
}

export interface PopulationByCityRecord {
  city: string
  population: number
  male: number
  female: number
  pctUnder15: number
  pct15To59: number
  pctOver60: number
}

export interface IncidentPer100kRecord {
  city: string
  incidents: number
  incidentsPer100k: number
}

export interface MapPoint {
  city: string
  latitude: number
  longitude: number
  incidents: number
  gabCount: number
  averageRiskScore: number
  riskCategory: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
}

export interface PredictionRequest {
  atmCode?: string
  agency?: string
  city?: string
  typeGab?: string
  dominantCategory?: string
  dominantMotif?: string
  incidents_7d?: number
  incidents_30d?: number
  incidents_90d?: number
  monthly_frequency?: number
  mttr_gab?: number
  incidents_weekend?: number
  incidents_semaine?: number
  ratio_weekend?: number
  jour_plus_critique?: string
  incidentCount?: number
  atmAge?: number
  population: number
  pct_over60?: number
  pctOver60?: number
  transaction_volume?: number
  transactionVolume?: number
}

export interface PredictionResponse {
  atmCode?: string | null
  agency?: string | null
  city?: string | null
  riskScore: number
  failureProbability: number
  riskCategory: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
  recommendation: string
  explanation: string
  mttrGab: number
  incidentsWeekend: number
  incidentsSemaine: number
  ratioWeekend: number
  jourPlusCritique: string
  dominantMotif: string
  dominantCategory: string
}

export interface TopCriticalATM {
  atm: string
  agency: string
  city: string
  riskCategory: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
  riskScore: number
  failureProbability: number
  topMotif: string
  topCategory: string
  averageDurationMinutes: number
  incidentCount: number
  mttrGab: number
  incidentsWeekend: number
  incidentsSemaine: number
  ratioWeekend: number
  jourPlusCritique: string
  explanation: string
}

export interface PredictionAtmFeatures {
  atmCode: string
  agency: string
  city: string
  typeGab: string
  dominantCategory: string
  dominantMotif: string
  incidents7d: number
  incidents30d: number
  incidents90d: number
  monthlyFrequency: number
  population: number
  pctOver60: number
  estimatedTransactionVolume: number
  mttrGab: number
  incidentsWeekend: number
  incidentsSemaine: number
  ratioWeekend: number
  jourPlusCritique: string
  incidentsLundi: number
  incidentsMardi: number
  incidentsMercredi: number
  incidentsJeudi: number
  incidentsVendredi: number
  incidentsSamedi: number
  incidentsDimanche: number
}

export interface AtRiskPredictionItem {
  atmCode: string
  agency: string
  city: string
  typeGab: string
  riskScore: number
  failureProbability: number
  riskCategory: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
  dominantMotif: string
  dominantCategory: string
  mttrGab: number
  incidentsWeekend: number
  incidentsSemaine: number
  ratioWeekend: number
  jourPlusCritique: string
  explanation: string
  recommendation: string
}

export interface RecommendationItem {
  atm: string
  agency: string
  city: string
  riskCategory: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
  priority: string
  actions: string[]
  topMotif: string
  topCategory: string
  recommendedAction: string
  businessJustification: string
}
