import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface LineChartCardProps {
  label: string
  data: { month: string; incidents: number }[]
}

function LineChartCard({ label, data }: LineChartCardProps) {
  return (
    <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">{label}</h2>
          <p className="text-sm text-slate-500">Tendance des incidents sur les 6 derniers mois</p>
        </div>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 16, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 12 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="incidents" stroke="#F05A00" strokeWidth={3} dot={{ r: 4, fill: '#F05A00' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default LineChartCard
