import { Area, AreaChart, CartesianGrid, Legend, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { CompositionRow } from '../../services/stressTest'
import { useLanguage } from '../../contexts/LanguageContext'
import { useCopy } from '../DataDisplay'
import { EconomicTooltip } from './EconomicTooltip'

const definitions=[
  {key:'primary_sector',fr:'Primaire',ar:'الأولي',color:'#16865c'},
  {key:'extractive_activities',fr:'Extraction',ar:'الاستخراج',color:'#e9852d'},
  {key:'manufacturing',fr:'Manufacturier',ar:'التصنيع',color:'#df675b'},
  {key:'construction_public_works',fr:'BTP',ar:'البناء',color:'#8a929d'},
  {key:'tertiary_sector',fr:'Tertiaire',ar:'الثالثي',color:'#397ebd'},
] as const

function CompositionTooltip({active,payload,label}:{active?:boolean;payload?:Array<{payload:CompositionRow;dataKey:string;name:string}>;label?:number}) {
  const c=useCopy();const total=payload?.[0]?.payload.gdp??null
  return <EconomicTooltip active={active} year={label} items={(payload??[]).map(item=>{const raw=item.payload[item.dataKey as keyof CompositionRow];const value=typeof raw==='number'?raw:null;return {name:item.name,value,unit:c('millions MRU','مليون أوقية'),share:value!=null&&total?value/total*100:null,status:'historical' as const}})}/>
}

export function GdpCompositionChart({data,selectedSector,targetSectors=[],selectedYear,onSelect}:{data:CompositionRow[];selectedSector:string;targetSectors?:string[];selectedYear:number;onSelect:(code:string)=>void}) {
  const c=useCopy();const {direction}=useLanguage()
  return <div data-testid="composition-chart" className="h-[390px] w-full" role="img" aria-label={c('Graphique de composition du PIB à cent pour cent','رسم تركيب الناتج بنسبة مئة بالمئة')}><ResponsiveContainer><AreaChart data={data} stackOffset="expand" margin={{top:10,right:12,left:0,bottom:8}}><CartesianGrid strokeDasharray="3 3" stroke="#e5e9ee"/><XAxis dataKey="year" tick={{fontSize:11}}/><YAxis domain={[0,1]} tickFormatter={value=>`${Math.round(Number(value)*100)}%`} width={48}/><Tooltip content={<CompositionTooltip/>}/><Legend wrapperStyle={{direction}}/><ReferenceLine x={selectedYear} stroke="#b78a21" strokeDasharray="4 4" strokeWidth={2}/>{definitions.map(item=>{const affected=selectedSector===item.key,target=targetSectors.includes(item.key);return <Area data-testid={`composition-area-${item.key}`} key={item.key} type="monotone" dataKey={item.key} name={c(item.fr,item.ar)} stackId="composition" stroke={affected?'#b42318':target?'#087f5b':item.color} fill={item.color} fillOpacity={affected?0.95:target?0.72:0.25} strokeWidth={affected||target?3:1} strokeDasharray={target?'5 2':undefined} onClick={()=>onSelect(item.key)} className="cursor-pointer transition-opacity" connectNulls={false}/>})}</AreaChart></ResponsiveContainer></div>
}
