import { useEffect, useMemo, useState } from 'react'
import { UploadCloud, Users, BarChart3, MapPin } from 'lucide-react'
import { api } from '../services/api'
import { DemographicRecord, DemographicStatsResponse, IncidentPer100kRecord } from '../types/api'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import SimpleTable from '../components/tables/SimpleTable'
import SectionHeader from '../components/ui/SectionHeader'
import PieChartCard from '../components/charts/PieChartCard'
import BarChartCard from '../components/charts/BarChartCard'
import { BANKING_ACTIVITY_BY_CITY, formatDh, formatNumber, getBankingActivityForCity } from '../data/bankingActivity'

function DemographyAnalysis() {
  const [records, setRecords] = useState<DemographicRecord[]>([])
  const [stats, setStats] = useState<DemographicStatsResponse | null>(null)
  const [incidentsPer100k, setIncidentsPer100k] = useState<IncidentPer100kRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.getPopulationByCity(), api.getDemographicStats(), api.getIncidentsPer100k()])
      .then(([cityData, statsData, incidentsData]) => {
        setRecords(cityData)
        setStats(statsData)
        setIncidentsPer100k(incidentsData)
      })
      .catch((error) => {
        console.error(error)
        setError((error as Error).message || 'Impossible de charger les données démographiques.')
      })
      .finally(() => setLoading(false))
  }, [])

  const chartData = useMemo(
    () => records.map((record) => ({ name: record.city, value: record.population })),
    [records]
  )

  const ageDistribution = useMemo(() => {
    const totalCities = records.length || 1
    const averageUnder15 = records.reduce((sum, record) => sum + record.pctUnder15, 0) / totalCities
    const average15To59 = records.reduce((sum, record) => sum + record.pct15To59, 0) / totalCities
    const averageOver60 = records.reduce((sum, record) => sum + record.pctOver60, 0) / totalCities

    return [
      { name: '<15 ans', value: Number(averageUnder15.toFixed(1)) },
      { name: '15-59 ans', value: Number(average15To59.toFixed(1)) },
      { name: '>60 ans', value: Number(averageOver60.toFixed(1)) }
    ]
  }, [records])

  const uploadRgphFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setUploadMessage(null)
    setUploadError(null)

    try {
      const response = await api.uploadRgph(file)
      setUploadMessage(response.message)
      setRecords(await api.getPopulationByCity())
      setStats(await api.getDemographicStats())
      setIncidentsPer100k(await api.getIncidentsPer100k())
    } catch (error) {
      setUploadError((error as Error).message)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !stats) {
    return (
      <div className="rounded-[26px] border border-rose-200 bg-rose-50 p-8 text-center text-rose-700">
        {error ?? 'Les données RGPH sont indisponibles pour le moment.'}
      </div>
    )
  }

  const topDensity = incidentsPer100k.slice(0, 6).map((item) => ({ name: item.city, value: item.incidentsPer100k }))
  const bankingActivityRows = records.map((record) => {
    const activity = getBankingActivityForCity(record.city)
    return {
      city: record.city,
      population: record.population,
      estimatedGabCount: activity?.estimatedGabCount ?? 0,
      monthlyOperations: activity?.monthlyOperations ?? 0,
      monthlyConsumptionDh: activity?.monthlyConsumptionDh ?? 0
    }
  })
  const populationVsOperations = bankingActivityRows
    .filter((item) => item.monthlyOperations > 0)
    .map((item) => ({ name: item.city, value: item.monthlyOperations }))
  const populationVsConsumption = bankingActivityRows
    .filter((item) => item.monthlyConsumptionDh > 0)
    .map((item) => ({ name: item.city, value: item.monthlyConsumptionDh }))
  const activityTableRows = bankingActivityRows.length
    ? bankingActivityRows
    : BANKING_ACTIVITY_BY_CITY.map((item) => ({
        city: item.city,
        population: 0,
        estimatedGabCount: item.estimatedGabCount,
        monthlyOperations: item.monthlyOperations,
        monthlyConsumptionDh: item.monthlyConsumptionDh
      }))

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Analyse démographique RGPH 2024"
        description="Données populationnelles par ville, indicateurs RGPH et impacts des incidents par 100 000 habitants."
      />

      <div className="grid gap-6 xl:grid-cols-4 lg:grid-cols-2">
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <Users size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Villes couvertes</p>
          </div>
          <p className="mt-4 text-4xl font-semibold text-slate-900">{stats.totalCities}</p>
          <p className="mt-3 text-sm text-slate-600">Unités géographiques suivies.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <MapPin size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Population</p>
          </div>
          <p className="mt-4 text-4xl font-semibold text-slate-900">{stats.totalPopulation.toLocaleString()}</p>
          <p className="mt-3 text-sm text-slate-600">Population totale analysée.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <BarChart3 size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Proportion +60 ans</p>
          </div>
          <p className="mt-4 text-4xl font-semibold text-slate-900">{stats.averagePctOver60.toFixed(1)}%</p>
          <p className="mt-3 text-sm text-slate-600">Âge moyen des populations critiques.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <UploadCloud size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Import RGPH</p>
          </div>
          <label className="mt-4 inline-flex cursor-pointer items-center rounded-3xl bg-[#FFF1E8] px-5 py-3 text-sm font-semibold text-[#F05A00] shadow-soft transition duration-200 hover:bg-[#FFE4D1] hover:text-[#F05A00]">
            <UploadCloud size={18} className="mr-2 text-[#F05A00]" />
            Charger RGPH
            <input type="file" accept=".xlsx,.xls" className="hidden" onChange={uploadRgphFile} />
          </label>
          <p className="mt-3 text-sm text-slate-600">Mettre à jour les données RGPH depuis un fichier Excel.</p>
          {uploadMessage && <p className="mt-3 text-sm text-emerald-700">{uploadMessage}</p>}
          {uploadError && <p className="mt-3 text-sm text-rose-600">{uploadError}</p>}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <PieChartCard label="Part d’âge consolidée" data={ageDistribution} />
        <BarChartCard label="Population par ville" data={chartData.slice(0, 10)} />
        <BarChartCard label="Incidents / 100k" data={topDensity} />
      </div>

      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Activité bancaire des villes</h2>
          <p className="mt-2 text-sm text-slate-600">
            Indicateurs mensuels estimés à titre informatif. Ces données ne sont pas utilisées dans le calcul du risque IA.
          </p>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <BarChartCard label="Population vs Opérations" data={populationVsOperations} />
          <BarChartCard label="Population vs Consommation" data={populationVsConsumption} />
        </div>
        <div>
          <SimpleTable
            headers={['Ville', 'Population', 'Nombre de GAB', 'Opérations estimées', 'Consommation estimée']}
            rows={activityTableRows.map((item) => [
              item.city,
              item.population ? item.population.toLocaleString() : '-',
              formatNumber(item.estimatedGabCount),
              formatNumber(item.monthlyOperations),
              formatDh(item.monthlyConsumptionDh)
            ])}
          />
        </div>
      </div>

      <SimpleTable
        headers={['Ville', 'Population', 'Hommes', 'Femmes', '% <15 ans', '% 15-59 ans', '% >60 ans']}
        rows={records.map((record) => [
          record.city,
          record.population.toLocaleString(),
          record.male.toLocaleString(),
          record.female.toLocaleString(),
          `${record.pctUnder15}%`,
          `${record.pct15To59}%`,
          `${record.pctOver60}%`
        ])}
      />
    </div>
  )
}

export default DemographyAnalysis
