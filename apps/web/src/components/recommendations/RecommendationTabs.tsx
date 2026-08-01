import { useState } from 'react'
import type { Recommendation } from '../../types/economic'
import { Badge, useCopy } from '../DataDisplay'

const horizons=['immediate','stabilization','recovery','structural'] as const

export function RecommendationTabs({recommendations}:{recommendations:Recommendation[]}) {
  const c=useCopy(); const [active,setActive]=useState<(typeof horizons)[number]>('immediate')
  const labels={immediate:c('Immédiat','فوري'),stabilization:c('Stabilisation','استقرار'),recovery:c('Reprise','تعافٍ'),structural:c('Résilience structurelle','مرونة هيكلية')}
  const visible=recommendations.filter(item=>item.time_horizon===active)
  return <div><div role="tablist" aria-label={c('Horizons de réaction','آفاق الاستجابة')} className="flex gap-2 overflow-x-auto pb-2">{horizons.map(horizon=><button role="tab" aria-selected={active===horizon} key={horizon} onClick={()=>setActive(horizon)} className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-bold ${active===horizon?'bg-mauritania-700 text-white':'bg-slate-100 text-slate-700'}`}>{labels[horizon]}</button>)}</div><div className="mt-5 grid gap-4 lg:grid-cols-2">{visible.map(item=><article className="rounded-2xl border border-slate-200 p-5" key={item.code}><div className="flex items-start justify-between gap-3"><h3 className="font-bold text-slate-950">{c(item.title_fr,item.title_ar)}</h3><Badge tone={item.priority==='critical'?'danger':item.priority==='high'?'warning':'neutral'}>{item.priority}</Badge></div><p className="mt-3 text-sm leading-6 text-slate-700">{c(item.reason_fr,item.reason_ar)}</p><p className="mt-3 text-sm"><strong>{c('Objectif : ','الهدف: ')}</strong>{c(item.expected_objective_fr,item.expected_objective_ar)}</p><p className="mt-3 text-xs text-slate-500"><strong>{c('À suivre : ','للمتابعة: ')}</strong>{item.monitoring_indicators.join(', ')}</p><div className="mt-3"><Badge>{c('Confiance','الثقة')}: {item.confidence}</Badge></div><p className="mt-3 text-xs leading-5 text-slate-500">{c(item.limitations_fr,item.limitations_ar)}</p></article>)}{visible.length===0&&<p className="text-sm text-slate-500">{c('Aucune action pour cet horizon et ce niveau de risque.','لا توجد إجراءات لهذا الأفق ومستوى المخاطر.')}</p>}</div></div>
}
