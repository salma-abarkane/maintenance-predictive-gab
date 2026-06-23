interface RiskBadgeProps {
  value: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
}

const styleMap = {
  Faible: 'bg-emerald-100 text-emerald-700',
  Moyen: 'bg-amber-100 text-amber-700',
  Élevé: 'bg-orange-100 text-orange-700',
  Critique: 'bg-rose-100 text-rose-700'
}

function RiskBadge({ value }: RiskBadgeProps) {
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styleMap[value]}`}>{value}</span>
}

export default RiskBadge
