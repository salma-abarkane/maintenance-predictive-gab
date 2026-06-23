import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { RecommendationItem } from '../types/api'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import StatusBadge from '../components/ui/StatusBadge'
import SectionHeader from '../components/ui/SectionHeader'
import { BANKING_ACTIVITY_BY_CITY, formatDh, formatNumber } from '../data/bankingActivity'

function Recommendations() {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getRecommendations()
      .then(setRecommendations)
      .catch((error) => {
        console.error(error)
        setError((error as Error).message || 'Impossible de charger les recommandations.')
      })
      .finally(() => setLoading(false))
  }, [])

  const priorityCounts = useMemo(() => {
    return recommendations.reduce<Record<string, number>>((acc, item) => {
      acc[item.priority] = (acc[item.priority] || 0) + 1
      return acc
    }, {})
  }, [recommendations])
  const mostActiveCities = useMemo(
    () => [...BANKING_ACTIVITY_BY_CITY].sort((left, right) => right.monthlyOperations - left.monthlyOperations).slice(0, 3),
    []
  )
  const highConsumptionCities = useMemo(
    () => [...BANKING_ACTIVITY_BY_CITY].sort((left, right) => right.monthlyConsumptionDh - left.monthlyConsumptionDh).slice(0, 3),
    []
  )

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <div className="rounded-[26px] border border-rose-200 bg-rose-50 p-8 text-center text-rose-700">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Recommandations opérationnelles"
        description="Actions de maintenance priorisées pour les GAB à haut risque et les interventions les plus impactantes." 
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-bporange-500">Actions urgentes</h3>
          <p className="mt-3 text-slate-600">Interventions immédiates pour limiter les arrêts et stabiliser le réseau.</p>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-bporange-500">Répartition des priorités</h3>
          <ul className="mt-4 space-y-3 text-slate-700">
            {Object.entries(priorityCounts).map(([key, value]) => (
              <li key={key} className="rounded-3xl bg-slate-50 p-4">{key} : <span className="font-semibold text-slate-900">{value}</span></li>
            ))}
          </ul>
        </div>
        <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-bporange-500">Objectif stratégique</h3>
          <p className="mt-3 text-slate-600">Réduire le taux de panne et anticiper les investissements de maintenance.</p>
        </div>
      </div>

      <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
        <h3 className="text-lg font-semibold text-slate-900">Analyse d'activité bancaire</h3>
        <p className="mt-2 text-sm text-slate-600">
          Lecture métier complémentaire basée sur des estimations mensuelles. Ces indicateurs n’influencent pas les recommandations IA.
        </p>
        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          <div className="rounded-3xl bg-bporange-50 px-4 py-3 text-slate-700">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-bporange-500">Villes les plus actives</p>
            <ul className="mt-3 space-y-2 text-sm">
              {mostActiveCities.map((item) => (
                <li key={item.city}>{item.city} : {formatNumber(item.monthlyOperations)} opérations/mois</li>
              ))}
            </ul>
          </div>
          <div className="rounded-3xl bg-bporange-50 px-4 py-3 text-slate-700">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-bporange-500">Forte consommation</p>
            <ul className="mt-3 space-y-2 text-sm">
              {highConsumptionCities.map((item) => (
                <li key={item.city}>{item.city} : {formatDh(item.monthlyConsumptionDh)}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-3xl bg-slate-50 px-4 py-3 text-slate-700">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-bporange-500">Observation métier</p>
            <p className="mt-3 text-sm">
              Les villes à forte activité peuvent nécessiter une attention opérationnelle renforcée, sans modifier le scoring IA existant.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6">
        {recommendations.map((item, index) => (
          <div key={`${item.atm}-${index}`} className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.18em] text-bporange-500">{item.city} — {item.agency}</p>
                <h3 className="mt-2 text-xl font-semibold text-bporange-500">{item.atm}</h3>
                <p className="mt-1 text-slate-600">Priorité : {item.priority}</p>
                <p className="mt-1 text-sm text-slate-500">Motif dominant : {item.topMotif}</p>
                <p className="mt-1 text-sm text-slate-500">Catégorie dominante : {item.topCategory}</p>
              </div>
              <StatusBadge variant={item.riskCategory} />
            </div>
            <div className="mt-6 rounded-3xl bg-slate-50 px-4 py-3 text-slate-700">
              <p className="font-semibold text-slate-900">{item.recommendedAction}</p>
              <p className="mt-2 text-sm">{item.businessJustification}</p>
            </div>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              {item.actions.map((action, actionIndex) => (
                <div key={actionIndex} className="rounded-3xl bg-bporange-50 px-4 py-3 text-slate-700">
                  {action}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Recommendations
