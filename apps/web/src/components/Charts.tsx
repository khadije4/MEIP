import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from 'recharts'
import type { Point } from '../types/economic'

const colors = ['#075d3b', '#d9ac47', '#2563eb', '#be123c', '#7c3aed', '#0891b2', '#ea580c']
export type ChartSeries = { name: string; points: Point[]; color?: string }

function mergeSeries(series: ChartSeries[]) {
  const rows = new Map<number, Record<string, number | string | null>>()
  series.forEach((item) => item.points.forEach((point) => { const row = rows.get(point.year) ?? { year: point.year }; row[item.name] = point.value; rows.set(point.year, row) }))
  return [...rows.values()].sort((a,b) => Number(a.year)-Number(b.year))
}

export function TimeSeriesChart({ series, height = 330 }: { series: ChartSeries[]; height?: number }) {
  const data = mergeSeries(series)
  return <div style={{ height }} className="w-full" aria-label={series.map((s) => s.name).join(', ')}><ResponsiveContainer width="100%" height="100%"><LineChart data={data} margin={{ top: 10, right: 10, bottom: 4, left: 2 }}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0"/><XAxis dataKey="year" tick={{fontSize:12}}/><YAxis tick={{fontSize:11}} width={70}/><Tooltip formatter={(value) => typeof value === 'number' ? value.toLocaleString(undefined,{maximumFractionDigits:2}) : '—'}/><Legend/>{series.map((item,index) => <Line key={item.name} type="monotone" dataKey={item.name} connectNulls={false} stroke={item.color ?? colors[index%colors.length]} strokeWidth={2.4} dot={false} activeDot={{r:4}}/>)}</LineChart></ResponsiveContainer></div>
}

export function RankingChart({ data }: { data: Array<{ name: string; value: number | null }> }) {
  return <div className="h-72 w-full"><ResponsiveContainer><BarChart data={data} layout="vertical" margin={{left:10,right:20}}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0"/><XAxis type="number"/><YAxis type="category" dataKey="name" width={110} tick={{fontSize:11}}/><Tooltip/><Bar dataKey="value" fill="#07804e" radius={[0,6,6,0]}/></BarChart></ResponsiveContainer></div>
}
