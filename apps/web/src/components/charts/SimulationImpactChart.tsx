import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useCopy } from '../DataDisplay'

export function SimulationImpactChart({baseline,simulated}:{baseline:number;simulated:number}) {
  const c=useCopy(); const data=[{name:c('Avant','قبل'),value:baseline,color:'#16865c'},{name:c('Après','بعد'),value:simulated,color:'#e76f61'}]
  return <div data-testid="impact-chart" className="h-64 w-full" role="img" aria-label={c('PIB avant et après le choc','الناتج قبل الصدمة وبعدها')}><ResponsiveContainer><BarChart data={data} margin={{top:8,right:8,left:5,bottom:5}}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis width={75}/><Tooltip formatter={(value)=>typeof value==='number'?value.toLocaleString(undefined,{maximumFractionDigits:2}):'—'}/><Bar dataKey="value" radius={[8,8,0,0]}>{data.map(item=><Cell key={item.name} fill={item.color}/>)}</Bar></BarChart></ResponsiveContainer></div>
}
