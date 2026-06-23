import { useEffect, useMemo, useState } from 'react'
import { Search, UploadCloud, ShieldAlert, Layers, TrendingUp } from 'lucide-react'
import { api } from '../services/api'
import { IncidentRecord, IncidentStatsResponse, TopAtmItem, MonthlyIncidentRecord, CategoryDistributionRecord, MaintenanceKpiResponse } from '../types/api'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import SimpleTable from '../components/tables/SimpleTable'
import SectionHeader from '../components/ui/SectionHeader'
import FilterSelect from '../components/ui/FilterSelect'
import BarChartCard from '../components/charts/BarChartCard'
import LineChartCard from '../components/charts/LineChartCard'

function IncidentAnalysis() {
  const [incidents, setIncidents] = useState<IncidentRecord[]>([])
  const [stats, setStats] = useState<IncidentStatsResponse | null>(null)
  const [topAtms, setTopAtms] = useState<TopAtmItem[]>([])
  const [monthly, setMonthly] = useState<MonthlyIncidentRecord[]>([])
  const [categories, setCategories] = useState<CategoryDistributionRecord[]>([])
  const [maintenanceKpis, setMaintenanceKpis] = useState<MaintenanceKpiResponse | null>(null)
  const [filterCity, setFilterCity] = useState('Toutes')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      api.getIncidents(),
      api.getIncidentStats(),
      api.getTopAtms(),
      api.getMonthlyIncidents(),
      api.getMotifDistribution(),
      api.getMaintenanceKpis()
    ])
      .then(([incidentData, statsData, atms, monthlyData, categoryData, kpiData]) => {
        setIncidents(incidentData)
        setStats(statsData)
        setTopAtms(atms)
        setMonthly(monthlyData)
        setCategories(categoryData)
        setMaintenanceKpis(kpiData)
      })
      .catch((error) => {
        console.error(error)
        setError((error as Error).message || 'Impossible de charger les données des incidents.')
      })
      .finally(() => setLoading(false))
  }, [])

  const cities = useMemo(() => ['Toutes', ...Array.from(new Set(incidents.map((item) => item.city)))], [incidents])

  const filteredIncidents = useMemo(() => {
    const query = search.toLowerCase()
    return incidents.filter((incident) => {
      const matchesCity = filterCity === 'Toutes' || incident.city === filterCity
      const matchesQuery = incident.agency.toLowerCase().includes(query) || incident.atm.toLowerCase().includes(query)
      return matchesCity && matchesQuery
    })
  }, [incidents, filterCity, search])

  const uploadIncidentFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setUploadMessage(null)
    setUploadError(null)

    try {
      const response = await api.uploadIncidents(file)
      setUploadMessage(response.message)
      setIncidents(await api.getIncidents())
      setStats(await api.getIncidentStats())
      setTopAtms(await api.getTopAtms())
      setMonthly(await api.getMonthlyIncidents())
      setCategories(await api.getMotifDistribution())
      setMaintenanceKpis(await api.getMaintenanceKpis())
    } catch (error) {
      setUploadError((error as Error).message)
    }
  }

  const monthlyChartData = useMemo(
    () => monthly.map((item) => ({ month: item.month, incidents: item.incidentCount })),
    [monthly]
  )

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !stats) {
    return (
      <div className="rounded-[26px] border border-rose-200 bg-rose-50 p-8 text-center text-rose-700">
        {error ?? 'Les données des incidents sont indisponibles pour le moment.'}
      </div>
    )
  }

  const topCategoryData = categories.map((item) => ({ name: item.category, value: item.count }))
  const topAtmData = topAtms.map((item) => ({ name: item.atm, value: item.incidentCount }))
  const pageSize = 200
  const totalPages = Math.max(1, Math.ceil(filteredIncidents.length / pageSize))
  const paginatedIncidents = filteredIncidents.slice((page - 1) * pageSize, page * pageSize)

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Analyse des incidents"
        description="Synthèse des pannes GAB, motifs d’arrêt et priorités de maintenance pour le réseau." 
      />

      <div className="grid gap-6 xl:grid-cols-4 lg:grid-cols-2">
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <ShieldAlert size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Incidents</p>
          </div>
          <p className="mt-4 text-4xl font-semibold text-slate-900">{stats.totalIncidents}</p>
          <p className="mt-3 text-sm text-slate-600">Incidents détectés sur le réseau étudié.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <Layers size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Agences concernées</p>
          </div>
          <p className="mt-4 text-4xl font-semibold text-slate-900">{stats.uniqueAgencies}</p>
          <p className="mt-3 text-sm text-slate-600">Centres de services impliqués.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <TrendingUp size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">GAB impactés</p>
          </div>
          <p className="mt-4 text-4xl font-semibold text-slate-900">{stats.uniqueAtms}</p>
          <p className="mt-3 text-sm text-slate-600">Distributeurs automatiques affectés.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <UploadCloud size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Import incidents</p>
          </div>
          <label className="mt-4 inline-flex cursor-pointer items-center rounded-3xl bg-[#FFF1E8] px-5 py-3 text-sm font-semibold text-[#F05A00] shadow-soft transition duration-200 hover:bg-[#FFE4D1] hover:text-[#F05A00]">
            <UploadCloud size={18} className="mr-2 text-[#F05A00]" />
            Charger incidents
            <input type="file" accept=".xlsx,.xls" className="hidden" onChange={uploadIncidentFile} />
          </label>
          <p className="mt-3 text-sm text-slate-600">Importer un fichier Excel pour mettre à jour les incidents.</p>
          {uploadMessage && <p className="mt-3 text-sm text-emerald-700">{uploadMessage}</p>}
          {uploadError && <p className="mt-3 text-sm text-rose-600">{uploadError}</p>}
        </div>
      </div>

      {maintenanceKpis && (
        <div className="grid gap-6 xl:grid-cols-4 lg:grid-cols-2">
          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Durée moyenne</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{maintenanceKpis.averageDurationMinutes.toFixed(1)} min</p>
            <p className="mt-3 text-sm text-slate-600">Calculée sur Durée (min).</p>
          </div>
          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Catégorie dominante</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{maintenanceKpis.dominantCategory}</p>
            <p className="mt-3 text-sm text-slate-600">Famille de panne la plus fréquente.</p>
          </div>
          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Incidents / GAB</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{maintenanceKpis.incidentsPerAtm.toFixed(1)}</p>
            <p className="mt-3 text-sm text-slate-600">Intensité moyenne par distributeur.</p>
          </div>
          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Motif dominant</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{maintenanceKpis.topMotif}</p>
            <p className="mt-3 text-sm text-slate-600">Motif le plus récurrent.</p>
          </div>
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-3 lg:grid-cols-2">
        <LineChartCard label="Incidents par mois" data={monthlyChartData} />
        <BarChartCard label="Top motifs" data={topCategoryData} />
        <BarChartCard label="Top GAB" data={topAtmData} />
      </div>

      <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Vue détaillée des incidents</h2>
            <p className="mt-2 text-slate-600">Filtrez les incidents par ville ou par nom de GAB pour identifier les augments de pannes.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="relative rounded-3xl border border-slate-200 bg-slate-50 p-3">
              <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                placeholder="Rechercher agence ou GAB"
                className="w-full bg-transparent pl-10 text-sm text-slate-900 outline-none"
              />
            </div>
            <FilterSelect
              label="Ville"
              options={cities}
              value={filterCity}
              onChange={(value) => {
                setFilterCity(value)
                setPage(1)
              }}
            />
          </div>
        </div>
      </div>

      <SimpleTable
        headers={['GAB', 'Agence', 'Ville', 'Motif', 'Sévérité', 'Date']}
        rows={paginatedIncidents.map((incident) => [
          incident.atm,
          incident.agency,
          incident.city,
          incident.category,
          incident.severity,
          incident.reportedAt
        ])}
      />

      <div className="flex flex-col gap-3 rounded-[26px] border border-slate-200/80 bg-white p-4 text-sm text-slate-600 shadow-soft sm:flex-row sm:items-center sm:justify-between">
        <p>
          Affichage de {paginatedIncidents.length} incidents sur {filteredIncidents.length.toLocaleString()} résultats filtrés.
        </p>
        <div className="flex items-center gap-3">
          <button
            type="button"
            disabled={page === 1}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            className="rounded-3xl bg-bporange-50 px-4 py-2 font-semibold text-bporange-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Précédent
          </button>
          <span>Page {page} / {totalPages}</span>
          <button
            type="button"
            disabled={page === totalPages}
            onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
            className="rounded-full bg-orange-500 px-8 py-4 font-bold text-white shadow-lg transition hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  )
}

export default IncidentAnalysis
