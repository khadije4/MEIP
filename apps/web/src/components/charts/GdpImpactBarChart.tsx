import { Bar, BarChart, CartesianGrid, LabelList, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useLanguage } from '../../contexts/LanguageContext'
import type { ImpactCategory } from '../../utils/latestYearSimulation'
import { useCopy } from '../DataDisplay'
import { EconomicTooltip } from './EconomicTooltip'

type ChartRow={key:ImpactCategory['key'];label:string;base:number|null;scenario:number|null}

export function GdpImpactBarChart({categories,year}:{categories:ImpactCategory[];year:number}){
 const c=useCopy();const {language}=useLanguage();const nf=new Intl.NumberFormat(language==='ar'?'ar-MR':'fr-MR',{maximumFractionDigits:0})
 const labels:Record<ImpactCategory['key'],string>={primary:c('Primaire','الأولي'),secondary:c('Secondaire','الثانوي'),tertiary:c('Tertiaire','الثالثي'),minerals:c('Minerais','المعادن'),gdp:c('PIB total','إجمالي الناتج')}
 const data:ChartRow[]=categories.map(item=>({...item,label:labels[item.key]}))
 const valueLabel=(value:unknown)=>typeof value==='number'?nf.format(value):''
 return <div data-testid="gdp-impact-bar-chart" className="h-[360px] w-full max-w-full overflow-hidden" role="img" aria-label={c(`Comparaison du PIB de base et du scénario pour ${year}`,`مقارنة الناتج الأساسي والسيناريو لسنة ${year}`)}>
  <ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{top:30,right:8,left:0,bottom:8}} barGap={4}>
   <CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label" interval={0} tick={{fontSize:11}}/><YAxis width={58} tick={{fontSize:10}} tickFormatter={valueLabel}/>
   <Tooltip content={({active,payload,label})=>{const row=payload?.[0]?.payload as ChartRow|undefined;return <EconomicTooltip active={active} year={`${label} · ${year}`} items={[{name:c('Base','الأساس'),value:row?.base,unit:c('millions MRU','مليون أوقية'),status:'observed'},{name:c('Scénario','السيناريو'),value:row?.scenario,unit:c('millions MRU','مليون أوقية'),status:'simulated'}]}/>}}/>
   <Legend/><Bar dataKey="base" name={`${c('Base','الأساس')} ${year}`} fill="#397ebd" radius={[5,5,0,0]}><LabelList dataKey="base" position="top" formatter={valueLabel} className="fill-blue-800 text-[9px]"/></Bar><Bar dataKey="scenario" name={c('Scénario','السيناريو')} fill="#16865c" radius={[5,5,0,0]}><LabelList dataKey="scenario" position="top" formatter={valueLabel} className="fill-mauritania-800 text-[9px]"/></Bar>
  </BarChart></ResponsiveContainer>
  <p data-testid="chart-summary" className="sr-only">{data.map(row=>`${row.label}: ${row.base??'—'} / ${row.scenario??'—'}`).join('; ')}</p>
 </div>
}
