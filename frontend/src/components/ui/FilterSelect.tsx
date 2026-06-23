interface FilterSelectProps {
  label: string
  options: string[]
  value: string
  onChange: (value: string) => void
}

function FilterSelect({ label, options, value, onChange }: FilterSelectProps) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-3 shadow-sm">
      <label className="block text-xs font-semibold uppercase tracking-[0.24em] text-bporange-500">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="mt-3 w-full bg-transparent text-sm text-slate-900 outline-none">
        {options.map((option) => (
          <option key={option} value={option} className="bg-white">
            {option}
          </option>
        ))}
      </select>
    </div>
  )
}

export default FilterSelect
