import { useEffect, useMemo, useState } from 'react'
import { Activity, Banknote, Building, CreditCard, FileDown, MapPin, Sparkles, Timer, Wallet, Wrench } from 'lucide-react'
import KpiCard from '../components/cards/KpiCard'
import LineChartCard from '../components/charts/LineChartCard'
import BarChartCard from '../components/charts/BarChartCard'
import PieChartCard from '../components/charts/PieChartCard'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import { api } from '../services/api'
import { IncidentStatsResponse, DemographicStatsResponse, TopCriticalATM, MonthlyIncidentRecord, CategoryDistributionRecord, TopAgencyItem, MaintenanceKpiResponse } from '../types/api'
import {
  BANKING_ACTIVITY_BY_CITY,
  MOST_ACTIVE_CITY,
  TOTAL_MONTHLY_CONSUMPTION_DH,
  TOTAL_MONTHLY_OPERATIONS,
  formatDh,
  formatNumber
} from '../data/bankingActivity'

function Dashboard() {
  const [incidentStats, setIncidentStats] = useState<IncidentStatsResponse | null>(null)
  const [demographicStats, setDemographicStats] = useState<DemographicStatsResponse | null>(null)
  const [topCritical, setTopCritical] = useState<TopCriticalATM[]>([])
  const [monthly, setMonthly] = useState<MonthlyIncidentRecord[]>([])
  const [categories, setCategories] = useState<CategoryDistributionRecord[]>([])
  const [topAgencies, setTopAgencies] = useState<TopAgencyItem[]>([])
  const [maintenanceKpis, setMaintenanceKpis] = useState<MaintenanceKpiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      api.getIncidentStats(),
      api.getDemographicStats(),
      api.getTopCriticalAtms(5),
      api.getMonthlyIncidents(),
      api.getCategoryDistribution(),
      api.getTopAgencies(5),
      api.getMaintenanceKpis()
    ])
      .then(([incidentData, demographicData, criticalData, monthlyData, categoryData, agencyData, kpiData]) => {
        setIncidentStats(incidentData)
        setDemographicStats(demographicData)
        setTopCritical(criticalData)
        setMonthly(monthlyData)
        setCategories(categoryData)
        setTopAgencies(agencyData)
        setMaintenanceKpis(kpiData)
      })
      .catch((error) => {
        console.error(error)
        setError((error as Error).message || 'Impossible de charger le tableau de bord. Veuillez réessayer.')
      })
      .finally(() => setLoading(false))
  }, [])

  const monthlyChartData = useMemo(
    () => monthly.map((item) => ({ month: item.month, incidents: item.incidentCount })),
    [monthly]
  )

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !incidentStats || !demographicStats) {
    return (
      <div className="rounded-[26px] border border-rose-200 bg-rose-50 p-8 text-center text-rose-700">
        {error ?? 'Les données du tableau de bord sont indisponibles pour le moment.'}
      </div>
    )
  }

  const riskDistribution = categories.map((item) => ({ name: item.category, value: item.count }))
  const topAgencyChartData = topAgencies.map((item) => ({ name: item.agency, value: item.incidentCount }))
  const operationsByCityData = BANKING_ACTIVITY_BY_CITY.map((item) => ({ name: item.city, value: item.monthlyOperations }))
  const consumptionByCityData = BANKING_ACTIVITY_BY_CITY.map((item) => ({ name: item.city, value: item.monthlyConsumptionDh }))

  const criticalCount = topCritical.filter((item) => item.riskCategory === 'Critique').length
  const highRiskCount = topCritical.filter((item) => item.riskCategory === 'Élevé').length
  const exportReport = () => window.print()

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Tableau de bord exécutif"
        description="Vue consolidée des incidents, des tendances RGPH et des points de maintenance prioritaire pour le réseau GAB."
      />

      <div className="flex justify-end">
        <button
          type="button"
          onClick={exportReport}
          className="inline-flex cursor-pointer items-center rounded-3xl bg-[#F05A00] px-6 py-3.5 text-sm font-bold text-white shadow-soft transition duration-200 hover:bg-[#FF7A1A] focus:outline-none focus:ring-4 focus:ring-[#FFF1E8]"
        >
          <FileDown size={18} className="mr-2" />
          Exporter rapport PDF
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-4 lg:grid-cols-2">
        <KpiCard label="Incidents" value={incidentStats.totalIncidents} description="Nombre d’incidents documentés." icon={<Activity size={24} />} />
        <KpiCard label="GAB impactés" value={incidentStats.uniqueAtms} description="GAB affectés par le monitoring des pannes." icon={<Banknote size={24} />} />
        <KpiCard label="Agences" value={incidentStats.uniqueAgencies} description="Agences liées aux incidents détectés." icon={<Building size={24} />} />
        <KpiCard label="Villes couvertes" value={demographicStats.totalCities} description="Zones RGPH suivies par l’analyse." icon={<MapPin size={24} />} />
      </div>

      {maintenanceKpis && (
        <div className="grid gap-6 xl:grid-cols-4 lg:grid-cols-2">
          <KpiCard label="MTTR" value={`${maintenanceKpis.mttrMinutes.toFixed(1)} min`} description="Durée moyenne de résolution calculée depuis Durée (min)." icon={<Timer size={24} />} />
          <KpiCard label="Motif dominant" value={maintenanceKpis.topMotif} description="Motif le plus fréquent dans les incidents." icon={<Wrench size={24} />} />
          <KpiCard label="GAB critiques" value={maintenanceKpis.criticalAtms} description="GAB classés Critique par le scoring IA." icon={<Sparkles size={24} />} />
          <KpiCard label="Ville impactée" value={maintenanceKpis.mostImpactedCity} description="Ville avec le plus grand nombre d’incidents." icon={<MapPin size={24} />} />
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-3 lg:grid-cols-2">
        <KpiCard label="Opérations mensuelles estimées" value={formatNumber(TOTAL_MONTHLY_OPERATIONS)} description="Volume mensuel estimé à titre informatif, non utilisé par l’IA." icon={<CreditCard size={24} />} />
        <KpiCard label="Consommation mensuelle estimée" value={formatDh(TOTAL_MONTHLY_CONSUMPTION_DH)} description="Montant estimé à titre métier, indépendant des prédictions." icon={<Wallet size={24} />} />
        <KpiCard label="Ville la plus active" value={MOST_ACTIVE_CITY.city} description={`${formatNumber(MOST_ACTIVE_CITY.monthlyOperations)} opérations mensuelles estimées.`} icon={<MapPin size={24} />} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <LineChartCard label="Incidents mensuels" data={monthlyChartData} />
        <BarChartCard label="Top agences impactées" data={topAgencyChartData} />
        <PieChartCard label="Répartition des catégories" data={riskDistribution} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <BarChartCard label="Opérations par ville" data={operationsByCityData} />
        <BarChartCard label="Consommation par ville" data={consumptionByCityData} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <h2 className="text-xl font-semibold text-slate-900">Maintenance IA</h2>
          <p className="mt-4 text-slate-600">Les prédictions s’appuient sur l’historique incidents, la démographie RGPH et le comportement transactionnel estimé.</p>
          <div className="mt-6 grid gap-3">
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-700">GAB critiques</p>
                <StatusBadge variant="Critique" />
              </div>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{criticalCount}</p>
            </div>
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-700">Zones à haut risque</p>
                <StatusBadge variant="Élevé" />
              </div>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{highRiskCount}</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Dashboard
