function MapLegend() {
  const items = [
    { label: 'Critique', color: '#dc2626' },
    { label: 'Élevé', color: '#f97316' },
    { label: 'Moyen', color: '#f59e0b' },
    { label: 'Faible', color: '#22c55e' }
  ]

  return (
    <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
      <h3 className="text-lg font-semibold text-bporange-500">Légende de la carte</h3>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3 text-sm text-slate-700">
            <span className="h-4 w-4 rounded-full" style={{ backgroundColor: item.color }} />
            {item.label}
          </div>
        ))}
      </div>
    </div>
  )
}

export default MapLegend
