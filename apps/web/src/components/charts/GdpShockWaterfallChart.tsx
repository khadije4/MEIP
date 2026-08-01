import { Bar, CartesianGrid, Cell, ComposedChart, LabelList, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useCopy } from '../DataDisplay'
import { EconomicTooltip } from './EconomicTooltip'

export function GdpShockWaterfallChart({baselineGdp,directLoss,simulatedGdp,compensationGain=0}:{baselineGdp:number;directLoss:number;simulatedGdp:number;compensationGain?:number}){
 const c=useCopy();const compensatedGdp=simulatedGdp+compensationGain;const unit=c('millions MRU','مليون أوقية')
 const data=[
  {name:c('PIB initial','الناتج الأولي'),base:0,value:baselineGdp,type:'baseline',resultLevel:baselineGdp},
  {name:c('Perte du choc','خسارة الصدمة'),base:simulatedGdp,value:directLoss,type:'loss',resultLevel:simulatedGdp},
  {name:c('PIB simulé','الناتج المحاكى'),base:0,value:simulatedGdp,type:'result',resultLevel:simulatedGdp},
  {name:c('Gain requis','الزيادة المطلوبة'),base:simulatedGdp,value:compensationGain,type:'gain',resultLevel:compensatedGdp},
  {name:c('PIB compensé','الناتج بعد التعويض'),base:0,value:compensatedGdp,type:'compensated',resultLevel:compensatedGdp},
 ].filter(row=>compensationGain>0||row.type!=='gain')
 return <div data-testid="waterfall-chart" className="h-[340px] w-full max-w-full overflow-hidden" role="img" aria-label={c('Cascade de l’impact et de la compensation sur le PIB','مخطط شلال أثر الصدمة والتعويض على الناتج')}><ResponsiveContainer><ComposedChart data={data} margin={{top:32,right:4,left:0,bottom:16}}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name" interval={0} tick={{fontSize:9}}/><YAxis width={64}/><Tooltip content={({active})=><EconomicTooltip active={active} items={[{name:c('PIB initial','الناتج الأولي'),value:baselineGdp,unit,status:'observed'},{name:c('Perte directe','الخسارة المباشرة'),value:directLoss,unit,status:'simulated'},{name:c('PIB simulé','الناتج المحاكى'),value:simulatedGdp,unit,status:'simulated'},...(compensationGain>0?[{name:c('Gain requis','الزيادة المطلوبة'),value:compensationGain,unit,status:'simulated' as const},{name:c('PIB compensé','الناتج بعد التعويض'),value:compensatedGdp,unit,status:'simulated' as const}]:[])]}/>}/><Bar dataKey="base" stackId="waterfall" fill="transparent"/><Bar dataKey="value" stackId="waterfall"><LabelList dataKey="value" position="top" formatter={(value:unknown)=>Number(value).toLocaleString()}/>{data.map(row=><Cell key={row.name} fill={row.type==='loss'?'#e85d3f':row.type==='gain'?'#3aa876':row.type==='compensated'?'#087f5b':row.type==='result'?'#16865c':'#1d3557'}/>)}</Bar><Line dataKey="resultLevel" stroke="#64748b" strokeDasharray="4 3" dot={false} isAnimationActive={false}/></ComposedChart></ResponsiveContainer></div>
}
