import { useEffect, useMemo, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import type { Indicator, Point } from '../types/economic'
import { IndicatorMultiSelect } from '../components/comparison/IndicatorMultiSelect'
import { MultiIndicatorChart, type MultiSeries } from '../components/charts/MultiIndicatorChart'
import { CurrentPriceWarning, DataTable, DownloadCsv, NumberValue, SelectField, useCopy } from '../components/DataDisplay'
import { KpiCard, PageContainer, PageHeader, Panel, StatePanel, WarningBanner } from '../components/Page'
import { annualGrowth, base100, hasCalendarGaps, summarizeComparison } from '../utils/comparison'
import { ChartSkeleton, PageLoadingState } from '../components/LoadingStates'
import { ChartErrorState, SectionErrorState } from '../components/ErrorStates'

const groups:Record<string,string[]>={main:['primary_sector','secondary_sector','tertiary_sector'],primary:['agriculture_forestry','livestock_hunting','fishing'],secondary:['extractive_activities','manufacturing','water_electricity','construction_public_works'],extractive:['oil_gas_extraction','metallic_mineral_extraction','snim_iron','gold_copper'],tertiary:['commerce','transport','information_communication','other_services'],expenditure:['final_consumption','gross_fixed_capital_formation','exports','imports']}
type Mode='actual'|'index'|'growth'|'small'

function querySelection(search:URLSearchParams){return (search.get('indicators')??'').split(',').filter(Boolean).slice(0,6)}

export function MultiComparePage(){
 const c=useCopy();const [search,setSearch]=useSearchParams();const fromUrl=querySelection(search)
 const {data:indicators,error:indicatorError,loading}=useApi<Indicator[]>('/api/indicators')
 const [selected,setSelectedState]=useState(fromUrl.length>=2?fromUrl:['fishing','extractive_activities'])
 const [cache,setCache]=useState<Record<string,Point[]>>({});const [mode,setMode]=useState<Mode>('actual')
 const [start,setStart]=useState(1998),[end,setEnd]=useState(2024),[ascending,setAscending]=useState(true)
 const [seriesError,setSeriesError]=useState(''),[retryTick,setRetryTick]=useState(0);const previousCount=useRef(selected.length)
 const setSelected=(codes:string[])=>{setSelectedState(codes);const params=new URLSearchParams(search);params.set('tab','compare');params.set('indicators',codes.join(','));setSearch(params)}

 useEffect(()=>{const codes=querySelection(search);if(codes.length>=2&&codes.join(',')!==selected.join(','))setSelectedState(codes)},[search,selected])
 useEffect(()=>{const missing=selected.filter(code=>!cache[code]);if(!missing.length)return;let active=true;Promise.all(missing.map(async code=>[code,(await api.get<{points:Point[]}>(`/api/indicators/${code}/series`)).data.points] as const)).then(rows=>active&&setCache(old=>({...old,...Object.fromEntries(rows)}))).catch(reason=>active&&setSeriesError(reason instanceof Error?reason.message:String(reason)));return()=>{active=false}},[cache,retryTick,selected])
 useEffect(()=>{if(!indicators)return;const valid=selected.filter(code=>indicators.some(item=>item.code===code));if(valid.length<2)setSelectedState(['fishing','extractive_activities']);else if(valid.length!==selected.length)setSelectedState(valid)},[indicators,selected])
 useEffect(()=>{if(previousCount.current<=4&&selected.length>4)setMode('small');previousCount.current=selected.length},[selected.length])

 const items=useMemo<MultiSeries[]>(()=>selected.flatMap(code=>{const i=indicators?.find(x=>x.code===code),raw=cache[code];if(!i||!raw)return[];const points=mode==='index'?base100(raw,start,end):mode==='growth'?annualGrowth(raw,start,end):raw.filter(p=>p.year>=start&&p.year<=end);return [{code,name:c(i.name_fr,i.name_ar??i.name_fr),unit:mode==='index'?c('Indice 100','مؤشر 100'):mode==='growth'?'%':i.unit,points}]}),[cache,c,end,indicators,mode,selected,start])
 const years=useMemo(()=>Array.from({length:end-start+1},(_,i)=>start+i).sort((a,b)=>ascending?a-b:b-a),[ascending,end,start])
 const units=new Set(items.map(x=>`${x.unit}:${x.code}`));const gaps=selected.some(code=>cache[code]&&hasCalendarGaps(cache[code],start,end))
 const rows=years.map(year=>[year,...selected.map(code=><NumberValue value={items.find(s=>s.code===code)?.points.find(p=>p.year===year)?.value}/>)])
 const seriesLoading=!seriesError&&selected.some(code=>!cache[code]);const noObservations=!seriesLoading&&items.length>0&&items.every(item=>item.points.every(point=>point.value==null))
 if(loading)return <PageLoadingState/>;if(indicatorError)return <PageContainer><SectionErrorState details={indicatorError.message} onRetry={()=>window.location.reload()}/></PageContainer>

 return <PageContainer>
  <PageHeader eyebrow={c('Comparaison multiple','مقارنة متعددة')} title={c('Comparer de 2 à 6 indicateurs','مقارنة من مؤشرين إلى 6 مؤشرات')} description={c('Valeurs importées, indices, croissance et petits graphiques sans valeurs inventées.','قيم مستوردة ومؤشرات ونمو ورسوم صغيرة دون اختلاق قيم.')}/>
  <div className="mt-6"><CurrentPriceWarning/></div>
  <Panel className="mt-6" title={c('Indicateurs sélectionnés','المؤشرات المحددة')}>
   <IndicatorMultiSelect indicators={indicators??[]} selected={selected} onChange={setSelected}/>
   <div className="mt-4 flex flex-wrap gap-2">{Object.entries(groups).map(([name,codes])=><button type="button" className="min-h-11 rounded-full border px-3 py-2 text-xs font-bold" onClick={()=>setSelected(codes.slice(0,6))} key={name}>{c(({main:'Secteurs principaux',primary:'Branches primaires',secondary:'Branches secondaires',extractive:'Branches extractives',tertiary:'Branches tertiaires',expenditure:'Indicateurs de dépense'} as Record<string,string>)[name],name)}</button>)}</div>
   <div className="mt-5 grid gap-3 sm:grid-cols-4"><SelectField label={c('Mode','الوضع')} value={mode} onChange={v=>setMode(v as Mode)}><option value="actual">{c('Valeurs réelles','القيم الفعلية')}</option><option value="index">{c('Indice base 100','مؤشر أساس 100')}</option><option value="growth">{c('Croissance annuelle','النمو السنوي')}</option><option value="small">{c('Petits graphiques','رسوم صغيرة')}</option></SelectField><SelectField label={c('Début','البداية')} value={start} onChange={v=>setStart(Math.min(+v,end))}>{Array.from({length:27},(_,i)=><option key={i}>{1998+i}</option>)}</SelectField><SelectField label={c('Fin','النهاية')} value={end} onChange={v=>setEnd(Math.max(+v,start))}>{Array.from({length:27},(_,i)=><option key={i}>{1998+i}</option>)}</SelectField></div>
  </Panel>
  {mode==='actual'&&units.size>1&&<div className="mt-5"><WarningBanner title={c('Compatibilité des unités','توافق الوحدات')}>{c('Les unités ou significations diffèrent; les valeurs ne sont pas redimensionnées.','تختلف الوحدات أو المعاني؛ لا تتم إعادة تحجيم القيم.')}</WarningBanner></div>}
  {mode==='growth'&&gaps&&<div className="mt-5"><WarningBanner title={c('Années calendaires manquantes','سنوات تقويمية مفقودة')}>{c('La croissance reste indisponible lorsqu’une année précédente manque.','يبقى النمو غير متاح عند غياب السنة السابقة.')}</WarningBanner></div>}
  <Panel className="mt-6" title={c('Comparaison historique','المقارنة التاريخية')}>{seriesError?<ChartErrorState details={seriesError} onRetry={()=>{setSeriesError('');setRetryTick(value=>value+1)}}/>:seriesLoading?<ChartSkeleton/>:noObservations?<StatePanel state="empty" title={c('Aucune observation commune','لا توجد ملاحظات مشتركة')} description={c('Choisissez d’autres indicateurs ou raccourcissez la période.','اختر مؤشرات أخرى أو قلّص الفترة.')}/>:<MultiIndicatorChart series={items} smallMultiples={mode==='small'}/>}</Panel>
  <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{selected.map(code=>{const i=indicators?.find(x=>x.code===code),s=summarizeComparison(cache[code]??[],start,end);return <Panel title={i?c(i.name_fr,i.name_ar??i.name_fr):code} key={code}><div className="grid grid-cols-1 gap-2 min-[360px]:grid-cols-2"><KpiCard label={c('Dernière valeur','آخر قيمة')} value={s.latest?.value.toLocaleString()??'—'}/><KpiCard label={c('Minimum','الحد الأدنى')} value={s.min?`${s.min.value.toLocaleString()} (${s.min.year})`:'—'}/><KpiCard label={c('Maximum','الحد الأقصى')} value={s.max?`${s.max.value.toLocaleString()} (${s.max.year})`:'—'}/><KpiCard label={c('Croissance moyenne','متوسط النمو')} value={s.averageGrowth==null?'—':`${s.averageGrowth.toFixed(2)}%`}/><KpiCard label={c('Volatilité','التقلب')} value={s.volatility==null?'—':`${s.volatility.toFixed(2)}%`}/><KpiCard label={c('Variation totale','التغير الكلي')} value={s.totalChange==null?'—':`${s.totalChange.toFixed(2)}%`}/></div></Panel>})}</div>
  <Panel className="mt-6" title={c('Tableau synchronisé','جدول متزامن')}><button type="button" onClick={()=>setAscending(x=>!x)} className="mb-3 min-h-11 rounded-lg border px-3 py-2 text-sm font-bold">{c('Trier par année','ترتيب حسب السنة')} {ascending?'↑':'↓'}</button><DataTable headers={[c('Année','السنة'),...selected.map(code=>{const i=indicators?.find(x=>x.code===code);return i?c(i.name_fr,i.name_ar??i.name_fr):code})]} rows={rows}/><DownloadCsv filename="meip-comparison.csv" headers={['year',...selected]} rows={years.map(year=>[year,...selected.map(code=>items.find(s=>s.code===code)?.points.find(p=>p.year===year)?.value??null)])}/></Panel>
 </PageContainer>
}
