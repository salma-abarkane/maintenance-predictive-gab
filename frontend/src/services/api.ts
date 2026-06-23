import {
  IncidentRecord,
  IncidentStatsResponse,
  TopAgencyItem,
  TopAtmItem,
  MonthlyIncidentRecord,
  MaintenanceKpiResponse,
  CategoryDistributionRecord,
  DataStatusResponse,
  ExcelUploadResponse,
  DemographicStatsResponse,
  PopulationByCityRecord,
  IncidentPer100kRecord,
  MapPoint,
  PredictionRequest,
  PredictionResponse,
  PredictionAtmFeatures,
  AtRiskPredictionItem,
  TopCriticalATM,
  RecommendationItem
} from '../types/api'

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'
const REQUEST_TIMEOUT_MS = 20000

interface PredictEndpointResponse {
  code_gab?: string | null
  agence?: string | null
  ville?: string | null
  risk_score: number
  risk_level: PredictionResponse['riskCategory']
  probability: number
  explanation: string
  recommendation: string
  mttr_gab?: number
  incidents_weekend?: number
  incidents_semaine?: number
  ratio_weekend?: number
  jour_plus_critique?: string
  motif_dominant?: string
  categorie_dominante?: string
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`
  const fullUrl = new URL(url, window.location.origin).href
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(url, { ...init, signal: controller.signal })
    if (!response.ok) {
      const message = await response.text()
      throw new Error(`Erreur API: ${fullUrl} | status=${response.status} ${response.statusText} | détail=${message || 'Réponse vide'}`)
    }

    const contentType = response.headers.get('content-type') ?? ''
    if (!contentType.includes('application/json')) {
      const text = await response.text()
      throw new Error(`Réponse API non JSON: ${fullUrl} | status=${response.status} | content-type=${contentType || 'absent'} | extrait=${text.slice(0, 300)}`)
    }

    const data = (await response.json()) as T
    return data
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      const timeoutError = new Error(`Timeout API: ${fullUrl} a dépassé ${REQUEST_TIMEOUT_MS / 1000}s.`)
      ;(timeoutError as Error & { cause?: unknown }).cause = error
      throw timeoutError
    }
    if (error instanceof TypeError) {
      const networkError = new Error(`Connexion API impossible: ${fullUrl}. Vérifie que le backend FastAPI est démarré, que le proxy Vite /api est actif, et qu'aucun blocage réseau/CORS n'empêche l'appel. Détail navigateur: ${error.message}`)
      ;(networkError as Error & { cause?: unknown }).cause = error
      throw networkError
    }
    throw error
  } finally {
    window.clearTimeout(timeoutId)
  }
}

export const api = {
  getDataStatus: () => fetchJson<DataStatusResponse>('/data-status'),
  getIncidentStats: () => fetchJson<IncidentStatsResponse>('/incidents/stats'),
  getIncidents: () => fetchJson<IncidentRecord[]>('/incidents/'),
  getTopAgencies: (limit = 5) => fetchJson<TopAgencyItem[]>(`/incidents/top-agencies?limit=${limit}`),
  getTopAtms: (limit = 5) => fetchJson<TopAtmItem[]>(`/incidents/top-atms?limit=${limit}`),
  getMonthlyIncidents: () => fetchJson<MonthlyIncidentRecord[]>('/incidents/monthly'),
  getMaintenanceKpis: () => fetchJson<MaintenanceKpiResponse>('/incidents/maintenance-kpis'),
  getCategoryDistribution: () => fetchJson<CategoryDistributionRecord[]>('/incidents/categories'),
  getMotifDistribution: () => fetchJson<CategoryDistributionRecord[]>('/incidents/motifs'),
  uploadIncidents: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetchJson<ExcelUploadResponse>('/incidents/upload', { method: 'POST', body: formData })
  },
  getDemographicStats: () => fetchJson<DemographicStatsResponse>('/rgph/stats'),
  getPopulationByCity: () => fetchJson<PopulationByCityRecord[]>('/rgph/population'),
  getIncidentsPer100k: () => fetchJson<IncidentPer100kRecord[]>('/rgph/incidents-per-100k'),
  uploadRgph: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetchJson<ExcelUploadResponse>('/rgph/upload', { method: 'POST', body: formData })
  },
  getMapPoints: () => fetchJson<MapPoint[]>('/map/'),
  trainModel: () => fetchJson<{ message: string }>('/ai/train', { method: 'POST' }),
  predictRisk: async (payload: PredictionRequest) => {
    const result = await fetchJson<PredictEndpointResponse>('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    return {
      atmCode: result.code_gab,
      agency: result.agence,
      city: result.ville,
      riskScore: result.risk_score,
      failureProbability: result.probability * 100,
      riskCategory: result.risk_level,
      recommendation: result.recommendation,
      explanation: result.explanation,
      mttrGab: result.mttr_gab ?? 0,
      incidentsWeekend: result.incidents_weekend ?? 0,
      incidentsSemaine: result.incidents_semaine ?? 0,
      ratioWeekend: result.ratio_weekend ?? 0,
      jourPlusCritique: result.jour_plus_critique ?? 'Non renseigné',
      dominantMotif: result.motif_dominant ?? 'Non renseigné',
      dominantCategory: result.categorie_dominante ?? 'Non classé'
    }
  },
  getPredictionAtms: () => fetchJson<PredictionAtmFeatures[]>('/predict/atms'),
  getAtRiskPredictions: () => fetchJson<AtRiskPredictionItem[]>('/predict/at-risk'),
  getTopCriticalAtms: (limit = 5) => fetchJson<TopCriticalATM[]>(`/ai/top-critical?limit=${limit}`),
  getRecommendations: () => fetchJson<RecommendationItem[]>('/ai/recommendations')
}
