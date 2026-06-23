interface KpiCardProps {
  label: string
  value: string | number
  icon: React.ReactNode
  description: string
}

function KpiCard({ label, value, icon, description }: KpiCardProps) {
  return (
    <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">{label}</p>
          <p className="mt-4 text-3xl font-semibold text-slate-900">{value}</p>
        </div>
        <div className="inline-flex h-14 w-14 items-center justify-center rounded-3xl bg-orange-50 text-orange-500">
          {icon}
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-500">{description}</p>
    </div>
  )
}

export default KpiCard
