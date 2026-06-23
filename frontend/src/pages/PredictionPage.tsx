import { useEffect, useState } from 'react'
import { ArrowRight, Activity, CalendarCheck, RefreshCw, Zap } from 'lucide-react'
import { api } from '../services/api'
import { AtRiskPredictionItem, PredictionAtmFeatures, PredictionRequest, PredictionResponse, TopCriticalATM } from '../types/api'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import SectionHeader from '../components/ui/SectionHeader'
import SimpleTable from '../components/tables/SimpleTable'

function PredictionPage() {
  const [atmOptions, setAtmOptions] = useState<PredictionAtmFeatures[]>([])
  const [selectedAtmCode, setSelectedAtmCode] = useState('')
  const [transactionVolume, setTransactionVolume] = useState(0)
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null)
  const [topCritical, setTopCritical] = useState<TopCriticalATM[]>([])
  const [atRiskPredictions, setAtRiskPredictions] = useState<AtRiskPredictionItem[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [refreshingPredictions, setRefreshingPredictions] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const fallbackTimer = window.setTimeout(() => {
      if (!mounted) return
      setError('Le chargement IA prend plus de temps que prévu. La page reste accessible pendant la récupération des données.')
      setLoading(false)
    }, 4000)

    const formatLoadError = (label: string, reason: unknown) => {
      const message = reason instanceof Error ? reason.message : String(reason)
      return `${label}: ${message}`
    }

    Promise.allSettled([api.getTopCriticalAtms(6), api.getPredictionAtms(), api.getAtRiskPredictions()])
      .then(([criticalResult, atmResult, atRiskResult]) => {
        if (!mounted) return

        const errors: string[] = []

        if (criticalResult.status === 'fulfilled') {
          setTopCritical(criticalResult.value)
        } else {
          errors.push(formatLoadError('Top GAB critiques', criticalResult.reason))
        }

        if (atmResult.status === 'fulfilled') {
          const atmData = atmResult.value
          setAtmOptions(atmData)
          if (atmData.length > 0) {
            setSelectedAtmCode(atmData[0].atmCode)
            setTransactionVolume(atmData[0].estimatedTransactionVolume)
          }
        } else {
          errors.push(formatLoadError('Liste des GAB', atmResult.reason))
        }

        if (atRiskResult.status === 'fulfilled') {
          setAtRiskPredictions(atRiskResult.value)
        } else {
          errors.push(formatLoadError('Prédictions automatiques', atRiskResult.reason))
        }

        setError(errors.length > 0 ? `Certaines données IA sont indisponibles. ${errors.join(' | ')}` : null)
      })
      .catch((error) => {
        if (!mounted) return
        console.error(error)
        setError((error as Error).message || 'Impossible de charger les données IA.')
      })
      .finally(() => {
        if (!mounted) return
        window.clearTimeout(fallbackTimer)
        setLoading(false)
      })

    return () => {
      mounted = false
      window.clearTimeout(fallbackTimer)
    }
  }, [])

  const selectedAtm = atmOptions.find((item) => item.atmCode === selectedAtmCode) ?? null
  const filteredAtRiskPredictions = atRiskPredictions.filter(
    (item) => item.riskCategory === 'Critique' || item.riskCategory === 'Élevé' || item.failureProbability > 70
  )

  const handleAtmChange = (atmCode: string) => {
    const nextAtm = atmOptions.find((item) => item.atmCode === atmCode) ?? null
    setSelectedAtmCode(atmCode)
    setPrediction(null)
    if (nextAtm) {
      setTransactionVolume(nextAtm.estimatedTransactionVolume)
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedAtm) {
      setMessage('Sélectionne un Code GAB avant de lancer la prédiction.')
      return
    }

    setSubmitting(true)
    setMessage(null)

    try {
      const payload: PredictionRequest = {
        atmCode: selectedAtm.atmCode,
        agency: selectedAtm.agency,
        city: selectedAtm.city,
        typeGab: selectedAtm.typeGab,
        dominantCategory: selectedAtm.dominantCategory,
        dominantMotif: selectedAtm.dominantMotif,
        incidents_7d: selectedAtm.incidents7d,
        incidents_30d: selectedAtm.incidents30d,
        incidents_90d: selectedAtm.incidents90d,
        monthly_frequency: selectedAtm.monthlyFrequency,
        population: selectedAtm.population,
        pct_over60: selectedAtm.pctOver60,
        transaction_volume: transactionVolume
      }
      const result = await api.predictRisk(payload)
      setPrediction(result)
      setMessage('Prédiction de risque générée avec succès.')
    } catch (error) {
      setMessage((error as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleTrain = async () => {
    setSubmitting(true)
    setMessage(null)
    try {
      const result = await api.trainModel()
      setMessage(result.message)
    } catch (error) {
      setMessage((error as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const refreshAutomaticPredictions = async () => {
    setRefreshingPredictions(true)
    setMessage(null)
    try {
      const result = await api.getAtRiskPredictions()
      setAtRiskPredictions(result)
      setMessage('Prédictions automatiques actualisées.')
    } catch (error) {
      setMessage((error as Error).message)
    } finally {
      setRefreshingPredictions(false)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Module IA — Prédiction"
        description="Première version explicable basée sur un modèle Random Forest entraîné sur l’historique incidents GAB de septembre 2025 à avril 2026."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <Zap size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Prédiction instantanée</p>
          </div>
          <p className="mt-4 text-3xl font-semibold text-slate-900">{prediction ? prediction.riskCategory : 'À calculer'}</p>
          <p className="mt-3 text-sm text-slate-600">Score : {prediction ? `${prediction.riskScore.toFixed(1)} / 100` : 'Entrez les paramètres et lancez la prédiction.'}</p>
          {prediction && (
            <>
              <p className="mt-2 text-sm font-semibold text-bporange-500">Probabilité de panne : {prediction.failureProbability.toFixed(1)}%</p>
              <p className="mt-3 text-sm text-slate-600">{prediction.explanation}</p>
            </>
          )}
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3 text-orange-500">
            <Activity size={20} />
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Paramètres</p>
          </div>
          <p className="mt-4 text-slate-700">Sélectionnez un GAB réel : les caractéristiques incidents, agence, ville et contexte RGPH sont chargés automatiquement.</p>
        </div>
        <button
          onClick={handleTrain}
          className="rounded-[26px] border border-orange-200 bg-orange-50 px-6 py-6 text-left text-slate-900 shadow-md transition hover:bg-orange-50"
          disabled={submitting}
        >
          <div className="flex items-center gap-3">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-orange-50">
              <CalendarCheck size={20} className="text-orange-500" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">Réentraîner le modèle</p>
              <p className="mt-1 text-sm text-slate-600">Actualise les scores IA avec les dernières données.</p>
            </div>
          </div>
        </button>
      </div>

      <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Prédiction automatique des GAB à risque</h2>
            <p className="mt-2 text-sm text-slate-600">
              Cette section utilise le modèle IA pour analyser automatiquement tous les GAB disponibles et identifier ceux qui présentent un risque élevé de panne.
            </p>
          </div>
          <button
            type="button"
            onClick={refreshAutomaticPredictions}
            disabled={refreshingPredictions}
            className="inline-flex cursor-pointer items-center justify-center rounded-3xl bg-[#F05A00] px-6 py-3.5 text-sm font-bold text-white shadow-soft transition duration-200 hover:bg-[#FF7A1A] focus:outline-none focus:ring-4 focus:ring-[#FFF1E8] disabled:cursor-not-allowed disabled:opacity-70"
          >
            <RefreshCw size={18} className="mr-2" />
            Actualiser les prédictions
          </button>
        </div>
        <div className="mt-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-900">GAB prédits à risque de panne</h3>
          <SimpleTable
            headers={['Rang', 'Code GAB', 'Agence', 'Ville', 'Probabilité', 'Risque', 'Motif dominant', 'Recommandation']}
            rows={filteredAtRiskPredictions.map((item, index) => [
              String(index + 1),
              item.atmCode,
              item.agency,
              item.city,
              `${item.failureProbability.toFixed(1)}%`,
              item.riskCategory,
              item.dominantMotif,
              item.recommendation
            ])}
          />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <h2 className="text-xl font-semibold text-slate-900">Formulaire de prédiction</h2>
          <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Code GAB</span>
                <select
                  value={selectedAtmCode}
                  onChange={(e) => handleAtmChange(e.target.value)}
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                >
                  {atmOptions.map((item) => (
                    <option key={item.atmCode} value={item.atmCode}>
                      {item.atmCode}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Type GAB</span>
                <input
                  value={selectedAtm?.typeGab ?? ''}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Agence</span>
                <input
                  value={selectedAtm?.agency ?? ''}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Ville</span>
                <input
                  value={selectedAtm?.city ?? ''}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Catégorie dominante</span>
                <input
                  value={selectedAtm?.dominantCategory ?? ''}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Motif dominant</span>
                <input
                  value={selectedAtm?.dominantMotif ?? ''}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
            </div>
            <div className="grid gap-4 sm:grid-cols-4">
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Incidents 7j</span>
                <input
                  value={selectedAtm?.incidents7d ?? 0}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Incidents 30j</span>
                <input
                  value={selectedAtm?.incidents30d ?? 0}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Incidents 90j</span>
                <input
                  value={selectedAtm?.incidents90d ?? 0}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Fréquence mensuelle</span>
                <input
                  value={selectedAtm?.monthlyFrequency ?? 0}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Population locale</span>
                <input
                  value={selectedAtm?.population ?? 0}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">% +60 ans</span>
                <input
                  value={selectedAtm?.pctOver60 ?? 0}
                  readOnly
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Transactions / jour</span>
                <input
                  value={transactionVolume}
                  onChange={(e) => setTransactionVolume(Number(e.target.value))}
                  type="number"
                  min={0}
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none"
                />
              </label>
            </div>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <button
                type="submit"
                className="inline-flex cursor-pointer items-center justify-center rounded-3xl bg-[#F05A00] px-6 py-3.5 text-sm font-bold text-white shadow-soft transition duration-200 hover:bg-[#FF7A1A] focus:outline-none focus:ring-4 focus:ring-[#FFF1E8] disabled:cursor-not-allowed disabled:opacity-70"
                disabled={submitting}
              >
                Calculer le risque
                <ArrowRight size={18} className="ml-2" />
              </button>
              {message && <p className="text-sm text-bporange-500">{message}</p>}
            </div>
          </form>
        </div>

        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <h2 className="text-xl font-semibold text-slate-900">Top GAB critiques</h2>
          <div className="mt-6 space-y-4">
            {(filteredAtRiskPredictions.length > 0 ? filteredAtRiskPredictions.slice(0, 3) : topCritical.slice(0, 3).map((item) => ({
              atmCode: item.atm,
              agency: item.agency,
              city: item.city,
              failureProbability: item.failureProbability,
              riskScore: item.riskScore
            }))).map((item) => (
              <div key={item.atmCode} className="rounded-3xl bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-semibold text-slate-900">{item.atmCode}</p>
                    <p className="text-sm text-slate-600">{item.agency} — {item.city}</p>
                  </div>
                  <p className="text-sm font-bold text-orange-600">{item.failureProbability.toFixed(1)}%</p>
                </div>
                <p className="mt-3 text-sm text-slate-600">Score: {item.riskScore.toFixed(1)} / 100</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <SimpleTable
        headers={['Rang', 'Code GAB', 'Agence', 'Ville', 'Score', 'Probabilité', 'Risque', 'Motif dominant']}
        rows={topCritical.map((item, index) => [
          String(index + 1),
          item.atm,
          item.agency,
          item.city,
          `${item.riskScore.toFixed(1)} / 100`,
          `${item.failureProbability.toFixed(1)}%`,
          item.riskCategory,
          item.topMotif
        ])}
      />
    </div>
  )
}

export default PredictionPage
