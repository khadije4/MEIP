import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useCopy } from '../DataDisplay'

export function BeforeAfterImpactChart({baselineGdp,sectorValue,directLoss,unit}:{baselineGdp:number;sectorValue:number;directLoss:number;unit:string}) {
  const c=useCopy();const unaffected=baselineGdp-sectorValue;const remaining=sectorValue-directLoss
  const data=[{name:c('Avant','قبل'),unaffected,remaining:sectorValue,loss:0},{name:c('Après','بعد'),unaffected,remaining,loss:directLoss}]
  return <div data-testid="before-after-chart" className="h-72 w-full" role="img" aria-label={c('Comparaison absolue avant et après en millions de MRU','مقارنة مطلقة قبل وبعد بملايين الأوقية')}><ResponsiveContainer><BarChart data={data} margin={{top:8,right:10,left:8,bottom:5}}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis width={76}/><Tooltip formatter={(value,name)=>[typeof value==='number'?`${value.toLocaleString()} ${unit}`:'—',String(name)]}/><Legend/><Bar dataKey="unaffected" name={c('PIB non affecté','الناتج غير المتأثر')} stackId="gdp" fill="#1d3557"/><Bar dataKey="remaining" name={c('Secteur restant','القطاع المتبقي')} stackId="gdp" fill="#16865c"/><Bar dataKey="loss" name={c('Perte directe','الخسارة المباشرة')} stackId="gdp" fill="#e85d3f" fillOpacity={0.3}>{data.map((item,index)=><Cell key={item.name} fill={index===1?'#e85d3f':'transparent'}/>)}</Bar></BarChart></ResponsiveContainer></div>
}
