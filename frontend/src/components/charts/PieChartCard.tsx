import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

interface PieChartCardProps {
  label: string
  data: { name: string; value: number }[]
}

const COLORS = ['#F05A00', '#D94A00', '#FF7A1A', '#FFC499']

function PieChartCard({ label, data }: PieChartCardProps) {
  return (
    <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">{label}</h2>
      <div className="mt-5 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} innerRadius={48} paddingAngle={4}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default PieChartCard
