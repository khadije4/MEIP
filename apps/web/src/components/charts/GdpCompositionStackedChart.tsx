import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { CompositionRow } from '../../services/stressTest'
import { useCopy } from '../DataDisplay'

export function GdpCompositionStackedChart({data}:{data:CompositionRow[]}) {
  const c=useCopy()
  const series=[
    ['primary_sector',c('Primaire','الأولي'),'#16865c'],
    ['extractive_activities',c('Extraction','الاستخراج'),'#ed8a2b'],
    ['manufacturing',c('Manufacturier','التصنيع'),'#e76f61'],
    ['construction_public_works',c('BTP','البناء'),'#87909b'],
    ['tertiary_sector',c('Tertiaire','الثالثي'),'#367dc4'],
  ] as const
  return <div data-testid="composition-chart" className="h-[360px] w-full" role="img" aria-label={c('Composition historique du PIB par grand secteur','التركيب التاريخي للناتج حسب القطاع')}><ResponsiveContainer width="100%" height="100%"><AreaChart data={data} stackOffset="expand" margin={{top:10,right:12,left:4,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0"/><XAxis dataKey="year" tick={{fontSize:11}}/><YAxis tickFormatter={value=>`${Math.round(Number(value)*100)}%`} domain={[0,1]} tick={{fontSize:11}}/><Tooltip formatter={(value)=>typeof value==='number'?value.toLocaleString(undefined,{maximumFractionDigits:2}):'—'}/><Legend/>{series.map(([key,name,color])=><Area key={key} type="monotone" dataKey={key} name={name} stackId="gdp" stroke={color} fill={color} connectNulls={false}/>)}</AreaChart></ResponsiveContainer></div>
}
