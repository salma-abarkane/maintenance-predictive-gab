interface StatusBadgeProps {
  variant: 'Faible' | 'Moyen' | 'Élevé' | 'Critique'
}

const statusStyles = {
  Faible: 'bg-emerald-100 text-emerald-700',
  Moyen: 'bg-amber-100 text-amber-700',
  Élevé: 'bg-orange-100 text-orange-700',
  Critique: 'bg-rose-100 text-rose-700'
}

function StatusBadge({ variant }: StatusBadgeProps) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[variant]}`}>{variant}</span>
}

export default StatusBadge
