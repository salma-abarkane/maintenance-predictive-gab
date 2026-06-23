interface SimpleTableProps {
  headers: string[]
  rows: Array<string[]>
}

function SimpleTable({ headers, rows }: SimpleTableProps) {
  return (
    <div className="overflow-hidden rounded-[26px] border border-slate-200/80 bg-white shadow-soft">
      <table className="min-w-full divide-y divide-slate-200 text-left">
        <thead className="bg-slate-50">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-6 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-bporange-500">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {rows.map((row, index) => (
            <tr key={index} className="hover:bg-slate-50">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-6 py-4 text-sm text-slate-700">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default SimpleTable
