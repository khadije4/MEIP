import { Area, AreaChart, CartesianGrid, Legend, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { CompositionRow } from '../../services/stressTest'
import { useLanguage } from '../../contexts/LanguageContext'
import { useCopy } from '../DataDisplay'

const definitions=[
  {key:'primary_sector',fr:'Primaire',ar:'الأولي',color:'#16865c'},
  {key:'extractive_activities',fr:'Extraction',ar:'الاستخراج',color:'#e9852d'},
  {key:'manufacturing',fr:'Manufacturier',ar:'التصنيع',color:'#df675b'},
  {key:'construction_public_works',fr:'BTP',ar:'البناء',color:'#8a929d'},
  {key:'tertiary_sector',fr:'Tertiaire',ar:'الثالثي',color:'#397ebd'},
] as const

function CompositionTooltip({active,payload,label}:{active?:boolean;payload?:Array<{payload:CompositionRow;dataKey:string;value:number;color:string;name:string}>;label?:number}) {
  const c=useCopy(); if(!active||!payload?.length)return null
  const total=payload.reduce((sum,item)=>sum+(Number(item.value)||0),0)
  return <div className="rounded-xl border border-slate-200 bg-white/95 p-3 text-xs shadow-xl backdrop-blur"><p className="mb-2 font-black text-navy-900">{c('Année','السنة')} {label}</p>{payload.map(item=><div className="flex min-w-52 items-center justify-between gap-4 py-1" key={item.dataKey}><span style={{color:item.color}}>{item.name}</span><span className="tabular-nums">{Number(item.value).toLocaleString()} · {total?`${(Number(item.value)/total*100).toFixed(1)}%`:'—'}</span></div>)}</div>
}

export function GdpCompositionChart({data,selectedSector,selectedYear,onSelect}:{data:CompositionRow[];selectedSector:string;selectedYear:number;onSelect:(code:string)=>void}) {
  const c=useCopy();const {direction}=useLanguage()
  return <div data-testid="composition-chart" className="h-[390px] w-full" role="img" aria-label={c('Graphique de composition du PIB à cent pour cent','رسم تركيب الناتج بنسبة مئة بالمئة')}><ResponsiveContainer><AreaChart data={data} stackOffset="expand" margin={{top:10,right:12,left:0,bottom:8}}><CartesianGrid strokeDasharray="3 3" stroke="#e5e9ee"/><XAxis dataKey="year" tick={{fontSize:11}}/><YAxis domain={[0,1]} tickFormatter={value=>`${Math.round(Number(value)*100)}%`} width={48}/><Tooltip content={<CompositionTooltip/>}/><Legend wrapperStyle={{direction}}/><ReferenceLine x={selectedYear} stroke="#b78a21" strokeDasharray="4 4" strokeWidth={2}/>{definitions.map(item=><Area data-testid={`composition-area-${item.key}`} key={item.key} type="monotone" dataKey={item.key} name={c(item.fr,item.ar)} stackId="composition" stroke={item.color} fill={item.color} fillOpacity={selectedSector===item.key?.toString()?0.92:0.48} strokeWidth={selectedSector===item.key?3:1} onClick={()=>onSelect(item.key)} className="cursor-pointer transition-opacity" connectNulls={false}/>)}</AreaChart></ResponsiveContainer></div>
}
